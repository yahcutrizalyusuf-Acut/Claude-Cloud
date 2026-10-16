import fs from "fs";
import path from "path";
import crypto from "crypto";

// ─── Types ────────────────────────────────────────────────────────────────────

// terbuka  → penulis masih bisa mengirim ucapan
// dikunci  → batas akhir lewat / dikunci pembuat, menunggu hari acara
// dibuka   → penerima sudah membuka buku
export type StatusBuku = "terbuka" | "dikunci" | "dibuka";

export interface Ucapan {
  id: string;
  nama: string;
  hubungan: string;
  pesan: string;
  foto: string[]; // nama file di folder media
  suara: string | null; // nama file di folder media
  tersembunyi: boolean;
  dibuat: string;
}

export interface Buku {
  id: string;
  kunciAdmin: string;
  untuk: string;
  acara: string;
  tanggalAcara: string; // YYYY-MM-DD
  batasTulis: string; // YYYY-MM-DD, akhir hari itu
  pembuat: string;
  sampul: string | null;
  rahasia: boolean;
  status: StatusBuku;
  ucapan: Ucapan[];
  dibuat: string;
  dibukaPada: string | null;
}

// ─── Penyimpanan ──────────────────────────────────────────────────────────────
// Satu file JSON cukup untuk purwarupa (puluhan buku, ratusan ucapan).
// Ganti ke basis data sungguhan sebelum dipakai luas.

export class Store {
  readonly mediaDir: string;
  private readonly dbFile: string;
  private data: { buku: Record<string, Buku> };
  private antrian: Promise<void> = Promise.resolve();

  constructor(dataDir: string) {
    this.mediaDir = path.join(dataDir, "media");
    this.dbFile = path.join(dataDir, "db.json");
    fs.mkdirSync(this.mediaDir, { recursive: true });
    this.data = fs.existsSync(this.dbFile)
      ? JSON.parse(fs.readFileSync(this.dbFile, "utf8"))
      : { buku: {} };
  }

  ambil(id: string): Buku | undefined {
    const buku = this.data.buku[id];
    if (buku && buku.status === "terbuka" && lewatBatas(buku.batasTulis)) {
      buku.status = "dikunci";
      void this.simpan();
    }
    return buku;
  }

  async buat(isi: Omit<Buku, "id" | "kunciAdmin" | "status" | "ucapan" | "dibuat" | "dibukaPada">): Promise<Buku> {
    const buku: Buku = {
      ...isi,
      id: idAcak(6),
      kunciAdmin: idAcak(18),
      status: "terbuka",
      ucapan: [],
      dibuat: new Date().toISOString(),
      dibukaPada: null,
    };
    this.data.buku[buku.id] = buku;
    await this.simpan();
    return buku;
  }

  async ubah(buku: Buku): Promise<void> {
    this.data.buku[buku.id] = buku;
    await this.simpan();
  }

  // Menulis ke file sementara lalu rename, berurutan, supaya file tidak rusak
  // kalau dua permintaan datang bersamaan.
  private simpan(): Promise<void> {
    this.antrian = this.antrian.then(async () => {
      const tmp = `${this.dbFile}.tmp`;
      await fs.promises.writeFile(tmp, JSON.stringify(this.data, null, 2));
      await fs.promises.rename(tmp, this.dbFile);
    });
    return this.antrian;
  }

  // Simpan file dari data URL. Mengembalikan nama file, atau melempar error
  // kalau jenis atau ukurannya tidak diizinkan.
  async simpanMedia(dataUrl: string, jenis: "foto" | "suara"): Promise<string> {
    const cocok = /^data:([a-z0-9.+/-]+)(?:;[a-z0-9=.+-]+)*;base64,(.+)$/i.exec(dataUrl);
    if (!cocok) throw new Error(`Format ${jenis} tidak dikenali`);
    const mime = cocok[1].toLowerCase();
    const ekstensi = (jenis === "foto" ? MIME_FOTO : MIME_SUARA)[mime];
    if (!ekstensi) throw new Error(`Jenis ${jenis} tidak didukung: ${mime}`);
    const isi = Buffer.from(cocok[2], "base64");
    const batas = jenis === "foto" ? BATAS_FOTO : BATAS_SUARA;
    if (isi.length > batas) throw new Error(`Ukuran ${jenis} terlalu besar`);
    const nama = `${idAcak(12)}.${ekstensi}`;
    await fs.promises.writeFile(path.join(this.mediaDir, nama), isi);
    return nama;
  }
}

const MIME_FOTO: Record<string, string> = {
  "image/jpeg": "jpg",
  "image/png": "png",
  "image/webp": "webp",
};

const MIME_SUARA: Record<string, string> = {
  "audio/webm": "webm",
  "audio/mp4": "m4a",
  "audio/aac": "aac",
  "audio/mpeg": "mp3",
  "audio/ogg": "ogg",
};

const BATAS_FOTO = 3 * 1024 * 1024;
const BATAS_SUARA = 4 * 1024 * 1024;

// Tanpa huruf/angka yang mirip (0/o, 1/l) supaya mudah dibaca dari tautan.
const ABJAD = "abcdefghijkmnpqrstuvwxyz23456789";

export function idAcak(panjang: number): string {
  const bytes = crypto.randomBytes(panjang);
  return Array.from(bytes, (b) => ABJAD[b % ABJAD.length]).join("");
}

// Batas tulis berlaku sampai akhir hari itu, waktu Indonesia Barat (UTC+7).
export function lewatBatas(batasTulis: string, sekarang = new Date()): boolean {
  const akhir = Date.parse(`${batasTulis}T23:59:59+07:00`);
  return !Number.isNaN(akhir) && sekarang.getTime() > akhir;
}
