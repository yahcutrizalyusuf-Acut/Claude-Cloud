import express, { NextFunction, Request, Response } from "express";
import crypto from "crypto";
import fs from "fs";
import path from "path";
import dotenv from "dotenv";
import { Buku, Store, Ucapan, idAcak } from "./store";
import { PermintaanDraf, aiAktif, buatDraf } from "./ai";

dotenv.config();

const PUBLIC_DIR = path.join(__dirname, "..", "public");
const store = new Store(process.env.DATA_DIR || path.join(__dirname, "..", "data"));

export const app = express();
app.set("trust proxy", true);
app.use(express.json({ limit: "25mb" }));
app.use((_req, res, next) => {
  res.setHeader("X-Content-Type-Options", "nosniff");
  next();
});

// ─── Bantuan ──────────────────────────────────────────────────────────────────

class GagalInput extends Error {}

function teks(nilai: unknown, nama: string, maks: number, wajib = true): string {
  const s = typeof nilai === "string" ? nilai.trim() : "";
  if (wajib && !s) throw new GagalInput(`${nama} wajib diisi`);
  if (s.length > maks) throw new GagalInput(`${nama} paling panjang ${maks} huruf`);
  return s;
}

function tanggal(nilai: unknown, nama: string): string {
  const s = teks(nilai, nama, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s) || Number.isNaN(Date.parse(s))) {
    throw new GagalInput(`${nama} tidak valid`);
  }
  return s;
}

const media = (nama: string) => `/media/${nama}`;

function ucapanPublik(u: Ucapan) {
  return {
    id: u.id,
    nama: u.nama,
    hubungan: u.hubungan,
    pesan: u.pesan,
    foto: u.foto.map(media),
    suara: u.suara && media(u.suara),
    dibuat: u.dibuat,
  };
}

// Yang boleh dilihat siapa saja yang punya tautan. Selama mode rahasia aktif
// dan buku belum dibuka, isi ucapan tidak dikirim, hanya nama penulisnya.
function bukuPublik(b: Buku) {
  const tampil = b.ucapan.filter((u) => !u.tersembunyi);
  const bolehLihatIsi = !b.rahasia || b.status === "dibuka";
  return {
    id: b.id,
    untuk: b.untuk,
    acara: b.acara,
    tanggalAcara: b.tanggalAcara,
    batasTulis: b.batasTulis,
    pembuat: b.pembuat,
    sampul: b.sampul && media(b.sampul),
    rahasia: b.rahasia,
    status: b.status,
    jumlahUcapan: tampil.length,
    penulis: tampil.map((u) => u.nama),
    ucapan: bolehLihatIsi ? tampil.map(ucapanPublik) : null,
    aiAktif: aiAktif(),
  };
}

function bukuAdmin(b: Buku) {
  return {
    ...bukuPublik(b),
    ucapan: b.ucapan.map((u) => ({ ...ucapanPublik(u), tersembunyi: u.tersembunyi })),
    dibukaPada: b.dibukaPada,
  };
}

function ambilBuku(req: Request): Buku {
  const buku = store.ambil(req.params.id);
  if (!buku) throw new TidakAda("Buku tidak ditemukan");
  return buku;
}

class TidakAda extends Error {}
class Terlarang extends Error {}

function ambilBukuAdmin(req: Request): Buku {
  const buku = ambilBuku(req);
  const kunci = Buffer.from(String(req.get("x-kunci") || ""));
  const benar = Buffer.from(buku.kunciAdmin);
  if (kunci.length !== benar.length || !crypto.timingSafeEqual(kunci, benar)) {
    throw new Terlarang("Kunci pembuat tidak cocok");
  }
  return buku;
}

type Handler = (req: Request, res: Response) => Promise<unknown>;
const aman = (fn: Handler) => (req: Request, res: Response, next: NextFunction) =>
  fn(req, res).catch(next);

// Batas sederhana per alamat IP untuk fitur AI, supaya biaya API tidak bocor.
const jatahAi = new Map<string, number[]>();
function bolehPakaiAi(ip: string): boolean {
  const sejamLalu = Date.now() - 60 * 60 * 1000;
  const riwayat = (jatahAi.get(ip) || []).filter((t) => t > sejamLalu);
  if (riwayat.length >= 15) return false;
  riwayat.push(Date.now());
  jatahAi.set(ip, riwayat);
  return true;
}

// ─── API: Pembuat ─────────────────────────────────────────────────────────────

// POST /api/buku → buat buku baru, balas dengan id dan kunci pembuat
app.post(
  "/api/buku",
  aman(async (req, res) => {
    const b = req.body || {};
    const tanggalAcara = tanggal(b.tanggalAcara, "Tanggal acara");
    const batasTulis = tanggal(b.batasTulis, "Batas akhir menulis");
    if (batasTulis > tanggalAcara) {
      throw new GagalInput("Batas akhir menulis harus sebelum atau sama dengan tanggal acara");
    }
    const isi = {
      untuk: teks(b.untuk, "Nama penerima", 80),
      acara: teks(b.acara, "Acara", 80),
      pembuat: teks(b.pembuat, "Nama pembuat", 80),
      tanggalAcara,
      batasTulis,
      rahasia: b.rahasia !== false,
      sampul: null as string | null,
    };
    if (b.sampul) isi.sampul = await store.simpanMedia(String(b.sampul), "foto");
    const buku = await store.buat(isi);
    res.status(201).json({ id: buku.id, kunciAdmin: buku.kunciAdmin });
  })
);

// GET /api/kelola/:id (header X-Kunci) → semua ucapan, termasuk yang disembunyikan
app.get(
  "/api/kelola/:id",
  aman(async (req, res) => {
    res.json(bukuAdmin(ambilBukuAdmin(req)));
  })
);

// PATCH /api/kelola/:id/ucapan/:uid { tersembunyi } → sembunyikan/tampilkan ucapan
app.patch(
  "/api/kelola/:id/ucapan/:uid",
  aman(async (req, res) => {
    const buku = ambilBukuAdmin(req);
    const u = buku.ucapan.find((x) => x.id === req.params.uid);
    if (!u) throw new TidakAda("Ucapan tidak ditemukan");
    u.tersembunyi = Boolean(req.body?.tersembunyi);
    await store.ubah(buku);
    res.json(bukuAdmin(buku));
  })
);

// POST /api/kelola/:id/status { status: "terbuka" | "dikunci" | "dibuka" }
app.post(
  "/api/kelola/:id/status",
  aman(async (req, res) => {
    const buku = ambilBukuAdmin(req);
    const status = req.body?.status;
    if (!["terbuka", "dikunci", "dibuka"].includes(status)) {
      throw new GagalInput("Status tidak dikenali");
    }
    buku.status = status;
    if (status === "dibuka" && !buku.dibukaPada) buku.dibukaPada = new Date().toISOString();
    await store.ubah(buku);
    res.json(bukuAdmin(buku));
  })
);

// ─── API: Penulis dan penerima ────────────────────────────────────────────────

// GET /api/buku/:id → info buku (isi ucapan hanya kalau boleh dilihat)
app.get(
  "/api/buku/:id",
  aman(async (req, res) => {
    res.json(bukuPublik(ambilBuku(req)));
  })
);

// POST /api/buku/:id/ucapan { nama, hubungan, pesan, foto: dataURL[], suara: dataURL }
app.post(
  "/api/buku/:id/ucapan",
  aman(async (req, res) => {
    const buku = ambilBuku(req);
    if (buku.status !== "terbuka") {
      throw new GagalInput("Maaf, buku ini sudah ditutup untuk ucapan baru");
    }
    const b = req.body || {};
    const foto: unknown[] = Array.isArray(b.foto) ? b.foto : [];
    if (foto.length > 3) throw new GagalInput("Foto paling banyak 3");
    const ucapan: Ucapan = {
      id: idAcak(8),
      nama: teks(b.nama, "Nama", 60),
      hubungan: teks(b.hubungan, "Hubungan", 60, false),
      pesan: teks(b.pesan, "Ucapan", 2000, !b.suara),
      foto: [],
      suara: null,
      tersembunyi: false,
      dibuat: new Date().toISOString(),
    };
    try {
      for (const f of foto) ucapan.foto.push(await store.simpanMedia(String(f), "foto"));
      if (b.suara) ucapan.suara = await store.simpanMedia(String(b.suara), "suara");
    } catch (err) {
      throw new GagalInput((err as Error).message);
    }
    buku.ucapan.push(ucapan);
    await store.ubah(buku);
    res.status(201).json({ id: ucapan.id, jumlahUcapan: buku.ucapan.length });
  })
);

// POST /api/buku/:id/draf { hubungan, nada, poin } → draf ucapan dari AI
app.post(
  "/api/buku/:id/draf",
  aman(async (req, res) => {
    const buku = ambilBuku(req);
    if (!aiAktif()) {
      res.status(503).json({ error: "Fitur bantu tulis belum diaktifkan" });
      return;
    }
    if (!bolehPakaiAi(req.ip || "")) {
      res.status(429).json({ error: "Terlalu sering minta draf, coba lagi nanti" });
      return;
    }
    const nada = ["resmi", "santai", "aceh"].includes(req.body?.nada) ? req.body.nada : "resmi";
    const permintaan: PermintaanDraf = {
      untuk: buku.untuk,
      acara: buku.acara,
      hubungan: teks(req.body?.hubungan, "Hubungan", 60, false),
      nada,
      poin: teks(req.body?.poin, "Poin", 500, false),
    };
    res.json({ draf: await buatDraf(permintaan) });
  })
);

// ─── File statis dan halaman ──────────────────────────────────────────────────

app.use("/media", express.static(store.mediaDir, { maxAge: "30d", immutable: true }));
app.use(express.static(PUBLIC_DIR, { index: false }));

const INDEX = fs.readFileSync(path.join(PUBLIC_DIR, "index.html"), "utf8");

const escapeHtml = (s: string) =>
  s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

// Semua halaman memakai index.html yang sama. Untuk tautan buku, judul dan
// gambar pratinjau diisi supaya kartu tautan di WA tampil menarik.
app.get(["/", "/b/:id", "/buku/:id", "/kelola/:id"], (req, res) => {
  const buku = req.params.id ? store.ambil(req.params.id) : undefined;
  let judul = "Buku Kenangan Bersama";
  let deskripsi = "Kumpulkan ucapan, foto, dan suara dari banyak orang untuk satu orang istimewa.";
  let gambar = "/ikon.svg";
  if (buku) {
    judul = `Buku kenangan untuk ${buku.untuk}`;
    deskripsi = `${buku.acara}. Tulis ucapanmu sebelum ${buku.batasTulis}.`;
    if (buku.sampul) gambar = media(buku.sampul);
  }
  const asal = `${req.protocol}://${req.get("host")}`;
  const html = INDEX.replace(/__JUDUL__/g, escapeHtml(judul))
    .replace(/__DESKRIPSI__/g, escapeHtml(deskripsi))
    .replace(/__GAMBAR__/g, escapeHtml(asal + gambar));
  res.type("html").send(html);
});

// ─── Error ────────────────────────────────────────────────────────────────────

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  if (err instanceof GagalInput) return res.status(400).json({ error: err.message });
  if (err instanceof TidakAda) return res.status(404).json({ error: err.message });
  if (err instanceof Terlarang) return res.status(403).json({ error: err.message });
  if ((err as { type?: string }).type === "entity.too.large") {
    return res.status(413).json({ error: "Kiriman terlalu besar" });
  }
  console.error("Error:", err);
  return res.status(500).json({ error: "Terjadi kesalahan di server" });
});

// ─── Start Server ─────────────────────────────────────────────────────────────

if (require.main === module) {
  const PORT = Number(process.env.PORT) || 3000;
  app.listen(PORT, () => {
    console.log(`✅ Buku Kenangan berjalan di http://localhost:${PORT}`);
    console.log(`   Bantu tulis AI: ${aiAktif() ? "aktif" : "nonaktif (ANTHROPIC_API_KEY kosong)"}`);
  });
}
