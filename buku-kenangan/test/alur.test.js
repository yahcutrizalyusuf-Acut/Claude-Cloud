// Tes alur utama: buat buku → tulis ucapan → mode rahasia → kunci → buka.
// Jalankan dengan `npm test` (build dulu, lalu memakai dist/).

const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const os = require("os");
const path = require("path");

const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), "bk-test-"));
process.env.DATA_DIR = dataDir;
delete process.env.ANTHROPIC_API_KEY;

const { app } = require("../dist/server");
const { lewatBatas } = require("../dist/store");

let server, base;
before(async () => {
  server = app.listen(0);
  await new Promise((r) => server.once("listening", r));
  base = `http://127.0.0.1:${server.address().port}`;
});
after(() => {
  server.close();
  fs.rmSync(dataDir, { recursive: true, force: true });
});

async function minta(p, { method = "GET", body, kunci } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (kunci) headers["X-Kunci"] = kunci;
  const res = await fetch(base + p, { method, headers, body: body && JSON.stringify(body) });
  const ct = res.headers.get("content-type") || "";
  return { status: res.status, data: ct.includes("json") ? await res.json() : await res.text() };
}

// 1x1 piksel JPEG dan potongan audio kecil, cukup untuk menguji penyimpanan.
const JPEG = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=";
const AUDIO = `data:audio/mp4;base64,${Buffer.from("suara-uji").toString("base64")}`;

const besok = (n) => new Date(Date.now() + n * 864e5).toISOString().slice(0, 10);
const bukuBaru = (lain = {}) => ({
  untuk: "Pak Hasan", acara: "Pensiun", pembuat: "Seksi acara",
  tanggalAcara: besok(10), batasTulis: besok(8), ...lain,
});

test("alur lengkap mode rahasia", async () => {
  const buat = await minta("/api/buku", { method: "POST", body: bukuBaru({ sampul: JPEG }) });
  assert.equal(buat.status, 201);
  const { id, kunciAdmin } = buat.data;

  const tulis = await minta(`/api/buku/${id}/ucapan`, {
    method: "POST",
    body: { nama: "Ani", hubungan: "rekan", pesan: "Selamat pensiun, Pak!", foto: [JPEG], suara: AUDIO },
  });
  assert.equal(tulis.status, 201);

  // Sebelum dibuka: penulis lain hanya melihat nama, bukan isi.
  const publik = await minta(`/api/buku/${id}`);
  assert.equal(publik.data.jumlahUcapan, 1);
  assert.deepEqual(publik.data.penulis, ["Ani"]);
  assert.equal(publik.data.ucapan, null);
  assert.equal(publik.data.kunciAdmin, undefined);

  // Pembuat melihat isi lengkap, termasuk file media yang bisa diambil.
  const kelola = await minta(`/api/kelola/${id}`, { kunci: kunciAdmin });
  assert.equal(kelola.status, 200);
  const u = kelola.data.ucapan[0];
  assert.equal(u.pesan, "Selamat pensiun, Pak!");
  assert.equal(u.foto.length, 1);
  assert.match(u.suara, /\.m4a$/);
  const fotoRes = await fetch(base + u.foto[0]);
  assert.equal(fotoRes.headers.get("content-type"), "image/jpeg");

  // Kunci: ucapan baru ditolak.
  await minta(`/api/kelola/${id}/status`, { method: "POST", kunci: kunciAdmin, body: { status: "dikunci" } });
  const telat = await minta(`/api/buku/${id}/ucapan`, { method: "POST", body: { nama: "Budi", pesan: "Halo" } });
  assert.equal(telat.status, 400);

  // Buka: isi tampil untuk semua yang punya tautan.
  await minta(`/api/kelola/${id}/status`, { method: "POST", kunci: kunciAdmin, body: { status: "dibuka" } });
  const dibuka = await minta(`/api/buku/${id}`);
  assert.equal(dibuka.data.status, "dibuka");
  assert.equal(dibuka.data.ucapan[0].nama, "Ani");
});

test("ucapan yang disembunyikan tidak ikut tampil", async () => {
  const { data } = await minta("/api/buku", { method: "POST", body: bukuBaru({ rahasia: false }) });
  const { id, kunciAdmin } = data;
  const a = await minta(`/api/buku/${id}/ucapan`, { method: "POST", body: { nama: "A", pesan: "baik" } });
  await minta(`/api/buku/${id}/ucapan`, { method: "POST", body: { nama: "B", pesan: "tidak pantas" } });
  const daftar = await minta(`/api/kelola/${id}`, { kunci: kunciAdmin });
  const b = daftar.data.ucapan.find((x) => x.nama === "B");
  await minta(`/api/kelola/${id}/ucapan/${b.id}`, { method: "PATCH", kunci: kunciAdmin, body: { tersembunyi: true } });
  const publik = await minta(`/api/buku/${id}`);
  assert.equal(a.status, 201);
  assert.deepEqual(publik.data.ucapan.map((x) => x.nama), ["A"]);
  assert.equal(publik.data.jumlahUcapan, 1);
});

test("kunci pembuat yang salah ditolak", async () => {
  const { data } = await minta("/api/buku", { method: "POST", body: bukuBaru() });
  const salah = await minta(`/api/kelola/${data.id}`, { kunci: "salah" });
  assert.equal(salah.status, 403);
  const tanpa = await minta(`/api/kelola/${data.id}/status`, { method: "POST", body: { status: "dibuka" } });
  assert.equal(tanpa.status, 403);
});

test("isian tidak valid ditolak", async () => {
  const kosong = await minta("/api/buku", { method: "POST", body: bukuBaru({ untuk: "" }) });
  assert.equal(kosong.status, 400);
  const terbalik = await minta("/api/buku", { method: "POST", body: bukuBaru({ batasTulis: besok(20) }) });
  assert.equal(terbalik.status, 400);

  const { data } = await minta("/api/buku", { method: "POST", body: bukuBaru() });
  const html = await minta(`/api/buku/${data.id}/ucapan`, {
    method: "POST",
    body: { nama: "X", pesan: "hai", foto: [`data:text/html;base64,${Buffer.from("<script>").toString("base64")}`] },
  });
  assert.equal(html.status, 400);
  const empatFoto = await minta(`/api/buku/${data.id}/ucapan`, {
    method: "POST", body: { nama: "X", pesan: "hai", foto: [JPEG, JPEG, JPEG, JPEG] },
  });
  assert.equal(empatFoto.status, 400);
  const tanpaIsi = await minta(`/api/buku/${data.id}/ucapan`, { method: "POST", body: { nama: "X" } });
  assert.equal(tanpaIsi.status, 400);
  const hanyaSuara = await minta(`/api/buku/${data.id}/ucapan`, { method: "POST", body: { nama: "X", suara: AUDIO } });
  assert.equal(hanyaSuara.status, 201);
});

test("bantu tulis AI nonaktif tanpa kunci API", async () => {
  const { data } = await minta("/api/buku", { method: "POST", body: bukuBaru() });
  const res = await minta(`/api/buku/${data.id}/draf`, { method: "POST", body: { nada: "santai" } });
  assert.equal(res.status, 503);
});

test("halaman tautan buku berisi pratinjau WA", async () => {
  const { data } = await minta("/api/buku", { method: "POST", body: bukuBaru({ untuk: "Bu <Rina>" }) });
  const html = await minta(`/b/${data.id}`);
  assert.match(html.data, /og:title" content="Buku kenangan untuk Bu &#60;Rina&#62;"/);
  assert.equal((await minta("/b/tidakada")).status, 200);
  assert.equal((await minta("/api/buku/tidakada")).status, 404);
});

test("batas tulis berlaku sampai akhir hari (WIB)", () => {
  assert.equal(lewatBatas("2026-10-20", new Date("2026-10-20T16:00:00Z")), false);
  assert.equal(lewatBatas("2026-10-20", new Date("2026-10-20T17:00:01Z")), true);
});
