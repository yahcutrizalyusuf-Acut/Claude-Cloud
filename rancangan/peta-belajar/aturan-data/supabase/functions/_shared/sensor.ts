// Penyensor data pribadi sebelum teks dikirim ke Claude.
//
// Aturan: yang dikirim ke AI hanya keinginan belajar dan jawaban
// pertanyaan pilihan. Nama, email, nomor akun, dan isi catatan tidak
// pernah ikut. Kalau pengguna tanpa sengaja mengetik data pribadi di
// kolom keinginan, data itu disensor dulu di sini.

export type HasilSensor = { teks: string; jumlahDisensor: number };

const TANDA = "[disensor]";

const POLA: { nama: string; pola: RegExp }[] = [
  // Alamat email.
  { nama: "email", pola: /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi },
  // Nomor HP Indonesia: 08xx, 628xx, +628xx, dengan spasi atau tanda hubung.
  { nama: "hp", pola: /(?:\+62|62|0)[\s-]?8[1-9](?:[\s-]?\d){6,11}/g },
  // NIK: 16 angka.
  { nama: "nik", pola: /\b\d{16}\b/g },
  // Nomor rekening atau kartu: 10 sampai 19 angka, boleh dipisah spasi atau tanda hubung.
  { nama: "nomor_panjang", pola: /\b\d(?:[\s-]?\d){9,18}\b/g },
];

export function sensor(teks: string): HasilSensor {
  let hasil = teks;
  let jumlah = 0;
  for (const { pola } of POLA) {
    hasil = hasil.replace(pola, () => {
      jumlah += 1;
      return TANDA;
    });
  }
  return { teks: hasil, jumlahDisensor: jumlah };
}

const PANJANG_MAKSIMAL = 300;

// Menyiapkan keinginan belajar untuk dikirim ke AI: disensor, dirapikan,
// dan dipotong supaya tidak membawa cerita pribadi yang panjang.
export function siapkanKeinginan(keinginan: string): HasilSensor {
  const rapi = keinginan.replace(/\s+/g, " ").trim().slice(0, PANJANG_MAKSIMAL);
  return sensor(rapi);
}
