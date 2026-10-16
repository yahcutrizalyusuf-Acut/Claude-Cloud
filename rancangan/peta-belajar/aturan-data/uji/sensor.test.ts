// Jalankan: node --experimental-strip-types --test uji/sensor.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { sensor, siapkanKeinginan } from "../supabase/functions/_shared/sensor.ts";

test("email disensor", () => {
  const h = sensor("belajar excel, kirim ke rahmat.kopi@gmail.com ya");
  assert.equal(h.teks, "belajar excel, kirim ke [disensor] ya");
  assert.equal(h.jumlahDisensor, 1);
});

test("nomor HP Indonesia dalam berbagai bentuk disensor", () => {
  for (const nomor of ["081234567890", "0812-3456-7890", "+6281234567890", "62 812 3456 789"]) {
    const h = sensor(`hubungi ${nomor} kalau ada kelas`);
    assert.equal(h.teks, "hubungi [disensor] kalau ada kelas", nomor);
  }
});

test("NIK dan nomor rekening disensor", () => {
  assert.equal(sensor("NIK saya 1171012345678901").teks, "NIK saya [disensor]");
  assert.equal(sensor("rekening BSI 7123 4567 89").teks, "rekening BSI [disensor]");
});

test("angka biasa dalam topik belajar tidak ikut disensor", () => {
  const teks = "belajar AutoCAD 2026 untuk rumah tipe 36, 3 kamar, 10 jam";
  assert.equal(sensor(teks).teks, teks);
  assert.equal(sensor(teks).jumlahDisensor, 0);
});

test("keinginan dirapikan dan dipotong 300 huruf", () => {
  const h = siapkanKeinginan("  bikin   video\n\npromosi  " + "a".repeat(400));
  assert.ok(h.teks.startsWith("bikin video promosi "));
  assert.equal(h.teks.length, 300);
});
