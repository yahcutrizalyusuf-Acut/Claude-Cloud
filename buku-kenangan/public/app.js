"use strict";

// Buku Kenangan Bersama — tampilan satu halaman tanpa kerangka (framework),
// supaya ringan dibuka dari tautan WA di HP apa pun.

const app = document.getElementById("app");

// ─── Bantuan ──────────────────────────────────────────────────────────────────

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

const BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
function tgl(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${BULAN[m - 1]} ${y}`;
}

function hariIni(tambahHari = 0) {
  const d = new Date();
  d.setDate(d.getDate() + tambahHari);
  return d.toISOString().slice(0, 10);
}

async function api(path, { method = "GET", body, kunci } = {}) {
  const headers = {};
  if (body) headers["Content-Type"] = "application/json";
  if (kunci) headers["X-Kunci"] = kunci;
  const res = await fetch(path, { method, headers, body: body && JSON.stringify(body) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Gagal terhubung ke server");
  return data;
}

const simpanLokal = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* mode pribadi */ } },
};

const asal = location.origin;
const tautanTulis = (id) => `${asal}/b/${id}`;
const tautanPenerima = (id) => `${asal}/buku/${id}`;
const tautanKelola = (id, kunci) => `${asal}/kelola/${id}#k=${kunci}`;
const waShare = (teks) => `https://wa.me/?text=${encodeURIComponent(teks)}`;

function ajakanWa(buku) {
  return `Assalamu'alaikum, kita sedang mengumpulkan ucapan dan doa untuk ${buku.untuk} (${buku.acara}). ` +
    `Yuk tulis ucapanmu, bisa tambah foto dan rekaman suara juga. Cukup buka tautan ini, tidak perlu daftar:\n` +
    `${tautanTulis(buku.id)}\n\nBatas menulis: ${tgl(buku.batasTulis)}. Terima kasih 🙏`;
}

function sampulHtml(buku, kelas = "") {
  if (buku.sampul) return `<img class="sampul ${kelas}" src="${esc(buku.sampul)}" alt="Foto ${esc(buku.untuk)}">`;
  return `<div class="sampul kosong ${kelas}" aria-hidden="true">${esc(buku.untuk.trim()[0] || "♥")}</div>`;
}

async function salin(teks, tombol) {
  try {
    await navigator.clipboard.writeText(teks);
    const lama = tombol.textContent;
    tombol.textContent = "Tersalin ✓";
    setTimeout(() => (tombol.textContent = lama), 1500);
  } catch {
    prompt("Salin tautan ini:", teks);
  }
}

// Perkecil foto di HP sebelum dikirim: hemat kuota dan cepat diunggah.
function kecilkanFoto(file, sisiMaks = 1280) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const skala = Math.min(1, sisiMaks / Math.max(img.width, img.height));
      const c = document.createElement("canvas");
      c.width = Math.round(img.width * skala);
      c.height = Math.round(img.height * skala);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url);
      resolve(c.toDataURL("image/jpeg", 0.82));
    };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("Foto tidak bisa dibaca")); };
    img.src = url;
  });
}

const blobKeDataUrl = (blob) =>
  new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = () => reject(r.error);
    r.readAsDataURL(blob);
  });

// ─── Router ───────────────────────────────────────────────────────────────────

function rute() {
  document.body.classList.remove("mode-buku");
  app.onclick = null;
  document.onkeydown = null;
  const [, bagian, id] = location.pathname.split("/");
  if (bagian === "b" && id) return halamanTulis(id);
  if (bagian === "kelola" && id) return halamanKelola(id);
  if (bagian === "buku" && id) return halamanPenerima(id);
  return halamanBeranda();
}

function galat(pesan) {
  app.innerHTML = `<div class="kartu tengah"><h2>Waduh</h2><p class="pudar">${esc(pesan)}</p>
    <a class="tombol kedua" href="/">Ke beranda</a></div>`;
}

// ─── Beranda: buat buku ───────────────────────────────────────────────────────

function halamanBeranda() {
  document.title = "Buku Kenangan Bersama";
  app.innerHTML = `
    <section class="hero">
      <img class="ikon" src="/ikon.svg" alt="">
      <h1>Buku Kenangan Bersama</h1>
      <p class="pudar">Kumpulkan ucapan, doa, foto, dan suara dari banyak orang untuk satu orang istimewa. Tanpa ada yang repot merangkum.</p>
    </section>
    <ol class="langkah-singkat">
      <li><span class="no">1</span><span>Buat buku untuk orang yang mau dikenang</span></li>
      <li><span class="no">2</span><span>Sebar satu tautan ke grup WA</span></li>
      <li><span class="no">3</span><span>Semua menulis dari HP masing-masing, tanpa daftar</span></li>
      <li><span class="no">4</span><span>Buka bukunya bersama di hari acara</span></li>
    </ol>
    <form class="kartu" id="form-buat" novalidate>
      <h2>Buat buku baru</h2>
      <label for="untuk">Untuk siapa?</label>
      <input type="text" id="untuk" name="untuk" maxlength="80" placeholder="cth. Pak Hasan" required>
      <label for="acara">Acaranya apa?</label>
      <input type="text" id="acara" name="acara" maxlength="80" list="daftar-acara" placeholder="cth. Pensiun" required>
      <datalist id="daftar-acara">
        <option value="Pensiun"><option value="Perpisahan guru"><option value="Rekan pindah tugas">
        <option value="Lepas haji"><option value="Pernikahan"><option value="Ulang tahun">
      </datalist>
      <div class="baris">
        <div>
          <label for="tanggalAcara">Tanggal acara</label>
          <input type="date" id="tanggalAcara" name="tanggalAcara" min="${hariIni()}" value="${hariIni(14)}" required>
        </div>
        <div>
          <label for="batasTulis">Batas menulis</label>
          <input type="date" id="batasTulis" name="batasTulis" min="${hariIni()}" value="${hariIni(12)}" required>
        </div>
      </div>
      <label for="sampul">Foto orangnya <span class="opsional">(tidak wajib, tampil di tautan WA)</span></label>
      <input type="file" id="sampul" accept="image/*">
      <label for="pembuat">Nama kamu (pembuat buku)</label>
      <input type="text" id="pembuat" name="pembuat" maxlength="80" placeholder="cth. Seksi acara kantor" required>
      <label class="centang"><input type="checkbox" id="rahasia" checked>
        <span><strong>Mode rahasia</strong><br><span class="pudar kecil">Isi ucapan disembunyikan sampai buku dibuka di hari acara. Penulis hanya melihat siapa saja yang sudah menulis.</span></span>
      </label>
      <button class="tombol penuh" type="submit" style="margin-top:20px">Buat buku</button>
      <p class="galat" id="galat" role="alert"></p>
    </form>`;

  const form = document.getElementById("form-buat");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const tombol = form.querySelector("button[type=submit]");
    const pesanGalat = document.getElementById("galat");
    pesanGalat.textContent = "";
    tombol.disabled = true;
    tombol.textContent = "Membuat…";
    try {
      const f = document.getElementById("sampul").files[0];
      const body = {
        untuk: form.untuk.value,
        acara: form.acara.value,
        tanggalAcara: form.tanggalAcara.value,
        batasTulis: form.batasTulis.value,
        pembuat: form.pembuat.value,
        rahasia: document.getElementById("rahasia").checked,
        sampul: f ? await kecilkanFoto(f, 800) : null,
      };
      const { id, kunciAdmin } = await api("/api/buku", { method: "POST", body });
      simpanLokal.set(`bk-admin-${id}`, kunciAdmin);
      history.pushState(null, "", `/kelola/${id}?baru=1`);
      rute();
    } catch (err) {
      pesanGalat.textContent = err.message;
      tombol.disabled = false;
      tombol.textContent = "Buat buku";
    }
  });
}

// ─── Penulis: tulis ucapan ────────────────────────────────────────────────────

async function halamanTulis(id) {
  let buku;
  try { buku = await api(`/api/buku/${id}`); } catch (err) { return galat(err.message); }
  document.title = `Ucapan untuk ${buku.untuk}`;

  const sudahMenulis = simpanLokal.get(`bk-tulis-${id}`);
  const kepala = `
    <section class="hero">
      ${sampulHtml(buku)}
      <div class="label-kecil">${esc(buku.acara)}</div>
      <h1>Untuk ${esc(buku.untuk)}</h1>
      <p class="pudar kecil">Dibuka ${tgl(buku.tanggalAcara)} · Dikumpulkan oleh ${esc(buku.pembuat)}</p>
      ${buku.jumlahUcapan ? `<p class="kecil"><strong>${buku.jumlahUcapan} orang</strong> sudah menulis</p>
        <div class="penulis-lain">${buku.penulis.slice(-12).map((n) => `<span class="chip">${esc(n)}</span>`).join("")}</div>` : ""}
    </section>`;

  if (buku.status !== "terbuka") {
    app.innerHTML = `${kepala}<div class="kartu tengah"><h2>Buku sudah ditutup</h2>
      <p class="pudar">Batas menulis sudah lewat. Terima kasih sudah mampir 🙏</p></div>`;
    return;
  }

  app.innerHTML = `${kepala}
    ${sudahMenulis ? `<div class="kartu tengah"><p class="sukses"><strong>Ucapanmu sudah terkirim ✓</strong></p>
      <p class="pudar kecil">Mau menambah satu lagi? Isi lagi di bawah.</p></div>` : ""}
    <form class="kartu" id="form-tulis" novalidate>
      <h2>Tulis ucapanmu</h2>
      <label for="nama">Nama kamu</label>
      <input type="text" id="nama" maxlength="60" autocomplete="name" required>
      <label for="hubungan">Hubunganmu dengan ${esc(buku.untuk)} <span class="opsional">(tidak wajib)</span></label>
      <input type="text" id="hubungan" maxlength="60" placeholder="cth. rekan satu ruangan, murid angkatan 2015">
      <label for="pesan">Ucapan atau doa</label>
      <textarea id="pesan" maxlength="2000" placeholder="Tulis kenangan, terima kasih, atau doa…"></textarea>
      ${buku.aiAktif ? `
      <button class="tombol tipis" type="button" id="buka-ai">✨ Bingung mau menulis apa? Minta bantuan</button>
      <div class="panel-ai" id="panel-ai" hidden>
        <label>Pilih nada</label>
        <div class="pilihan-nada" role="radiogroup">
          <label><input type="radio" name="nada" value="resmi" checked><span>Sopan</span></label>
          <label><input type="radio" name="nada" value="santai"><span>Santai</span></label>
          <label><input type="radio" name="nada" value="aceh"><span>Bahasa Aceh</span></label>
        </div>
        <label for="poin">Satu-dua hal yang mau disampaikan <span class="opsional">(tidak wajib)</span></label>
        <input type="text" id="poin" maxlength="500" placeholder="cth. beliau sabar mengajari saya waktu baru masuk">
        <button class="tombol kedua penuh" type="button" id="minta-draf" style="margin-top:12px">Buatkan draf</button>
        <p class="pudar kecil" style="margin-top:8px">Draf masuk ke kotak ucapan, lalu bisa kamu ubah sesukanya.</p>
      </div>` : ""}

      <label>Foto <span class="opsional">(paling banyak 3)</span></label>
      <input type="file" id="foto" accept="image/*" multiple>
      <div class="foto-pratinjau" id="foto-pratinjau"></div>

      <label>Ucapan suara <span class="opsional">(paling lama 60 detik)</span></label>
      <div class="perekam" id="perekam"></div>

      <button class="tombol penuh" type="submit" style="margin-top:24px">Kirim ucapan</button>
      <p class="galat" id="galat" role="alert"></p>
      ${buku.rahasia ? `<p class="pudar kecil tengah" style="margin-top:10px">🔒 Ucapanmu dirahasiakan sampai buku dibuka di hari acara.</p>` : ""}
    </form>`;

  const form = document.getElementById("form-tulis");
  const pesanGalat = document.getElementById("galat");

  // Foto
  let foto = [];
  const wadahFoto = document.getElementById("foto-pratinjau");
  const gambarFoto = () => {
    wadahFoto.innerHTML = foto.map((src, i) =>
      `<figure><img src="${src}" alt="Foto ${i + 1}"><button type="button" data-hapus="${i}" aria-label="Hapus foto">✕</button></figure>`).join("");
  };
  document.getElementById("foto").addEventListener("change", async (e) => {
    pesanGalat.textContent = "";
    for (const f of [...e.target.files]) {
      if (foto.length >= 3) { pesanGalat.textContent = "Foto paling banyak 3"; break; }
      try { foto.push(await kecilkanFoto(f)); } catch (err) { pesanGalat.textContent = err.message; }
    }
    e.target.value = "";
    gambarFoto();
  });
  wadahFoto.addEventListener("click", (e) => {
    const i = e.target.dataset.hapus;
    if (i !== undefined) { foto.splice(Number(i), 1); gambarFoto(); }
  });

  // Suara
  const perekam = pasangPerekam(document.getElementById("perekam"), (pesan) => (pesanGalat.textContent = pesan));

  // Bantu tulis AI
  if (buku.aiAktif) {
    const panel = document.getElementById("panel-ai");
    document.getElementById("buka-ai").addEventListener("click", () => (panel.hidden = !panel.hidden));
    document.getElementById("minta-draf").addEventListener("click", async (e) => {
      const tombol = e.currentTarget;
      pesanGalat.textContent = "";
      tombol.disabled = true;
      tombol.textContent = "Sedang menulis draf…";
      try {
        const { draf } = await api(`/api/buku/${id}/draf`, {
          method: "POST",
          body: {
            hubungan: form.hubungan.value,
            nada: form.querySelector("input[name=nada]:checked").value,
            poin: document.getElementById("poin").value,
          },
        });
        form.pesan.value = draf;
        form.pesan.focus();
      } catch (err) {
        pesanGalat.textContent = err.message;
      } finally {
        tombol.disabled = false;
        tombol.textContent = "Buatkan draf lain";
      }
    });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    pesanGalat.textContent = "";
    const suara = perekam.hasil();
    if (!form.nama.value.trim()) return (pesanGalat.textContent = "Nama wajib diisi");
    if (!form.pesan.value.trim() && !suara) return (pesanGalat.textContent = "Tulis ucapan atau rekam suara dulu");
    const tombol = form.querySelector("button[type=submit]");
    tombol.disabled = true;
    tombol.textContent = "Mengirim…";
    try {
      await api(`/api/buku/${id}/ucapan`, {
        method: "POST",
        body: {
          nama: form.nama.value,
          hubungan: form.hubungan.value,
          pesan: form.pesan.value,
          foto,
          suara: suara && (await blobKeDataUrl(suara)),
        },
      });
      simpanLokal.set(`bk-tulis-${id}`, "1");
      tampilTerimaKasih(buku);
    } catch (err) {
      pesanGalat.textContent = err.message;
      tombol.disabled = false;
      tombol.textContent = "Kirim ucapan";
    }
  });
}

function tampilTerimaKasih(buku) {
  app.innerHTML = `
    <section class="hero">
      ${sampulHtml(buku)}
      <h1>Terima kasih 🙏</h1>
      <p class="pudar">Ucapanmu untuk ${esc(buku.untuk)} sudah masuk ke buku. ${buku.rahasia
        ? `Isinya akan dibuka di hari acara, ${tgl(buku.tanggalAcara)}.` : ""}</p>
    </section>
    <div class="kartu tengah">
      <p>Ajak yang lain ikut menulis, makin banyak makin berkesan.</p>
      <a class="tombol wa penuh" href="${waShare(ajakanWa(buku))}" target="_blank" rel="noopener">Bagikan ke WA</a>
      <button class="tombol tipis" type="button" id="lagi" style="margin-top:8px">Tulis satu lagi</button>
    </div>`;
  document.getElementById("lagi").addEventListener("click", rute);
}

// Perekam suara. iPhone (Safari) merekam audio/mp4, Android/Chrome audio/webm.
function pasangPerekam(wadah, tampilGalat) {
  const MAKS_DETIK = 60;
  let rekaman = null, recorder = null, stream = null, timer = null, mulai = 0;

  const bisa = typeof MediaRecorder !== "undefined" && navigator.mediaDevices?.getUserMedia;
  const pilihMime = () =>
    ["audio/mp4", "audio/webm;codecs=opus", "audio/webm", "audio/ogg"].find((m) => MediaRecorder.isTypeSupported(m)) || "";

  function gambar(keadaan) {
    if (!bisa) {
      wadah.innerHTML = `<p class="pudar kecil">HP ini belum bisa merekam suara dari peramban. Coba buka di Safari (iPhone) atau Chrome (Android).</p>`;
      return;
    }
    if (keadaan === "merekam") {
      wadah.innerHTML = `<span class="titik-rekam"></span><span class="waktu" id="waktu">0:00</span>
        <button class="tombol kedua" type="button" id="stop">⏹ Selesai</button>`;
      wadah.querySelector("#stop").onclick = berhenti;
    } else if (rekaman) {
      wadah.innerHTML = `<audio controls src="${URL.createObjectURL(rekaman)}"></audio>
        <button class="tombol tipis" type="button" id="hapus-suara">Hapus dan rekam ulang</button>`;
      wadah.querySelector("#hapus-suara").onclick = () => { rekaman = null; gambar(); };
    } else {
      wadah.innerHTML = `<button class="tombol kedua" type="button" id="rekam">🎙️ Rekam suara</button>`;
      wadah.querySelector("#rekam").onclick = rekam;
    }
  }

  async function rekam() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      tampilGalat("Izin mikrofon ditolak. Aktifkan izin mikrofon untuk situs ini.");
      return;
    }
    const mimeType = pilihMime();
    recorder = new MediaRecorder(stream, mimeType ? { mimeType, audioBitsPerSecond: 64000 } : undefined);
    const potongan = [];
    recorder.ondataavailable = (e) => e.data.size && potongan.push(e.data);
    recorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      // Buang parameter codecs: server mencocokkan jenis dasarnya saja.
      const jenis = (recorder.mimeType || mimeType || "audio/webm").split(";")[0];
      rekaman = new Blob(potongan, { type: jenis });
      gambar();
    };
    recorder.start();
    mulai = Date.now();
    gambar("merekam");
    timer = setInterval(() => {
      const detik = Math.floor((Date.now() - mulai) / 1000);
      const el = document.getElementById("waktu");
      if (el) el.textContent = `${Math.floor(detik / 60)}:${String(detik % 60).padStart(2, "0")}`;
      if (detik >= MAKS_DETIK) berhenti();
    }, 250);
  }

  function berhenti() {
    clearInterval(timer);
    if (recorder && recorder.state !== "inactive") recorder.stop();
  }

  gambar();
  return { hasil: () => rekaman };
}

// ─── Pembuat: dasbor kelola ───────────────────────────────────────────────────

async function halamanKelola(id) {
  // Kunci bisa datang dari #k=… (tautan kelola) atau dari penyimpanan HP ini.
  const dariHash = new URLSearchParams(location.hash.slice(1)).get("k");
  if (dariHash) {
    simpanLokal.set(`bk-admin-${id}`, dariHash);
    history.replaceState(null, "", location.pathname + location.search);
  }
  const kunci = simpanLokal.get(`bk-admin-${id}`);
  if (!kunci) return galat("Halaman ini hanya untuk pembuat buku. Buka lewat tautan kelola yang kamu simpan saat membuat buku.");

  let buku;
  try { buku = await api(`/api/kelola/${id}`, { kunci }); } catch (err) { return galat(err.message); }
  const baru = new URLSearchParams(location.search).has("baru");
  gambarKelola(buku, kunci, baru);
}

function gambarKelola(buku, kunci, baru = false) {
  document.title = `Kelola buku ${buku.untuk}`;
  const tampil = buku.ucapan.filter((u) => !u.tersembunyi);
  const adaSuara = tampil.filter((u) => u.suara).length;
  const STATUS = { terbuka: "Menerima ucapan", dikunci: "Dikunci", dibuka: "Sudah dibuka" };

  app.innerHTML = `
    <section class="hero">
      ${sampulHtml(buku)}
      <div class="label-kecil">${esc(buku.acara)} · ${tgl(buku.tanggalAcara)}</div>
      <h1>Buku untuk ${esc(buku.untuk)}</h1>
      <span class="status-pill status-${buku.status}">${STATUS[buku.status]}</span>
    </section>

    ${baru ? `<div class="kartu">
      <h3>Buku sudah jadi 🎉</h3>
      <p class="kecil">Simpan <strong>tautan kelola</strong> ini. Hanya lewat tautan ini kamu bisa mengatur buku dari HP lain.</p>
      <div class="tautan-box"><code>${esc(tautanKelola(buku.id, kunci))}</code></div>
      <div class="tombol-grup"><button class="tombol kedua" type="button" data-salin="${esc(tautanKelola(buku.id, kunci))}">Salin tautan kelola</button></div>
    </div>` : ""}

    <div class="kartu">
      <div class="angka-besar">
        <div><strong>${tampil.length}</strong><span>ucapan</span></div>
        <div><strong>${tampil.reduce((n, u) => n + u.foto.length, 0)}</strong><span>foto</span></div>
        <div><strong>${adaSuara}</strong><span>suara</span></div>
      </div>
      <p class="pudar kecil tengah">Target 30 penulis · batas menulis ${tgl(buku.batasTulis)}</p>
    </div>

    ${buku.status === "terbuka" ? `<div class="kartu">
      <h3>Sebar ke grup WA</h3>
      <p class="pudar kecil">Satu tautan untuk semua penulis. Tidak perlu daftar atau pasang aplikasi.</p>
      <div class="tautan-box"><code>${esc(tautanTulis(buku.id))}</code></div>
      <div class="tombol-grup">
        <a class="tombol wa" href="${waShare(ajakanWa(buku))}" target="_blank" rel="noopener">Kirim ke WA</a>
        <button class="tombol kedua" type="button" data-salin="${esc(tautanTulis(buku.id))}">Salin tautan</button>
      </div>
      ${tampil.length ? `<a class="tombol tipis" href="${waShare(`Sudah ${tampil.length} orang menulis untuk ${buku.untuk} 🙏 Yang belum, masih ada waktu sampai ${tgl(buku.batasTulis)}:\n${tautanTulis(buku.id)}`)}" target="_blank" rel="noopener">Kirim pengingat ke grup →</a>` : ""}
    </div>` : ""}

    <div class="kartu">
      <h3>Hari acara</h3>
      ${buku.status === "dibuka"
        ? `<p class="kecil">Buku sudah dibuka. Kirim tautan ini ke ${esc(buku.untuk)} supaya bisa dibaca kapan saja.</p>
           <div class="tautan-box"><code>${esc(tautanPenerima(buku.id))}</code></div>
           <div class="tombol-grup">
             <a class="tombol" href="/buku/${buku.id}">Lihat buku</a>
             <a class="tombol wa" href="${waShare(`Untuk ${buku.untuk}, ini buku kenangan dari ${tampil.length} orang 💐\n${tautanPenerima(buku.id)}`)}" target="_blank" rel="noopener">Kirim ke penerima</a>
           </div>`
        : `<p class="pudar kecil">Di hari acara, tekan <strong>Buka buku</strong>, lalu tunjukkan layarnya ke ${esc(buku.untuk)} atau tampilkan di proyektor.</p>
           <div class="tombol-grup">
             ${buku.status === "terbuka"
               ? `<button class="tombol kedua" type="button" data-status="dikunci">Kunci, stop ucapan baru</button>`
               : `<button class="tombol kedua" type="button" data-status="terbuka">Buka lagi untuk ucapan</button>`}
             <button class="tombol" type="button" data-status="dibuka">Buka buku</button>
           </div>`}
    </div>

    <div class="kartu">
      <h3>Isi buku (${buku.ucapan.length})</h3>
      <p class="pudar kecil">Hanya kamu yang bisa melihat ini sebelum buku dibuka. Sembunyikan ucapan yang tidak pantas.</p>
      <div class="daftar-ucapan">
        ${buku.ucapan.length ? buku.ucapan.slice().reverse().map((u) => `
          <article class="ucapan-item ${u.tersembunyi ? "tersembunyi" : ""}">
            <header><strong>${esc(u.nama)}</strong><span class="pudar kecil">${esc(u.hubungan)}</span></header>
            ${u.pesan ? `<p class="pesan">${esc(u.pesan)}</p>` : ""}
            ${u.foto.length ? `<div class="foto-kecil">${u.foto.map((f) => `<img src="${esc(f)}" alt="" loading="lazy">`).join("")}</div>` : ""}
            ${u.suara ? `<audio controls preload="none" src="${esc(u.suara)}"></audio>` : ""}
            <button class="tombol tipis" type="button" data-sembunyi="${u.id}" data-nilai="${!u.tersembunyi}">
              ${u.tersembunyi ? "Tampilkan lagi" : "Sembunyikan"}</button>
          </article>`).join("") : `<p class="pudar tengah">Belum ada ucapan. Sebar tautannya dulu 😃</p>`}
      </div>
    </div>
    <p class="galat tengah" id="galat" role="alert"></p>`;

  const pesanGalat = document.getElementById("galat");
  app.onclick = async (e) => {
    const t = e.target.closest("button");
    if (!t) return;
    try {
      if (t.dataset.salin) return salin(t.dataset.salin, t);
      if (t.dataset.status) {
        const s = t.dataset.status;
        if (s === "dibuka" && !confirm(`Buka buku sekarang? Setelah dibuka, ${buku.untuk} dan semua penulis bisa melihat isinya.`)) return;
        t.disabled = true;
        const hasil = await api(`/api/kelola/${buku.id}/status`, { method: "POST", kunci, body: { status: s } });
        if (s === "dibuka") { location.href = `/buku/${buku.id}`; return; }
        return gambarKelola(hasil, kunci);
      }
      if (t.dataset.sembunyi) {
        t.disabled = true;
        const hasil = await api(`/api/kelola/${buku.id}/ucapan/${t.dataset.sembunyi}`, {
          method: "PATCH", kunci, body: { tersembunyi: t.dataset.nilai === "true" },
        });
        return gambarKelola(hasil, kunci);
      }
    } catch (err) {
      pesanGalat.textContent = err.message;
      t.disabled = false;
    }
  };
}

// ─── Penerima: momen buka buku ────────────────────────────────────────────────

async function halamanPenerima(id) {
  let buku;
  try { buku = await api(`/api/buku/${id}`); } catch (err) { return galat(err.message); }
  document.body.classList.add("mode-buku");
  document.title = `Untuk ${buku.untuk}`;

  if (!buku.ucapan) {
    app.innerHTML = `<section class="pembuka">
      ${sampulHtml(buku)}
      <div class="label-kecil">${esc(buku.acara)}</div>
      <h1>Ada kejutan untuk ${esc(buku.untuk)}</h1>
      <p>${buku.jumlahUcapan} orang sudah menitipkan ucapan. Buku ini akan dibuka pada ${tgl(buku.tanggalAcara)}.</p>
    </section>`;
    return;
  }

  app.innerHTML = `<section class="pembuka" id="pembuka">
    ${sampulHtml(buku)}
    <div class="label-kecil">${esc(buku.acara)}</div>
    <h1>Untuk ${esc(buku.untuk)}</h1>
    <p>Dari ${buku.ucapan.length} orang yang menyayangimu</p>
    <button class="tombol" type="button" id="buka">Buka bukunya</button>
  </section>`;

  document.getElementById("buka").addEventListener("click", () => {
    hujanKelopak();
    const pembuka = document.getElementById("pembuka");
    pembuka.classList.add("tutup");
    setTimeout(() => tampilBuku(buku), matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 850);
  });
}

function hujanKelopak() {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const warna = ["#e8c27a", "#f3b6c0", "#ffffff", "#d98a96"];
  for (let i = 0; i < 40; i++) {
    const k = document.createElement("span");
    k.className = "kelopak";
    k.style.left = `${Math.random() * 100}vw`;
    k.style.background = warna[i % warna.length];
    k.style.animationDuration = `${2.5 + Math.random() * 2.5}s`;
    k.style.animationDelay = `${Math.random() * 0.8}s`;
    document.body.appendChild(k);
    setTimeout(() => k.remove(), 6000);
  }
}

function tampilBuku(buku) {
  const halaman = [
    `<div class="lembar judul">${sampulHtml(buku)}<div class="label-kecil">${esc(buku.acara)}</div>
      <h1>Untuk ${esc(buku.untuk)}</h1><p class="pudar">${tgl(buku.tanggalAcara)}</p>
      <p class="pudar kecil">Geser untuk membaca →</p></div>`,
    ...buku.ucapan.map((u) => `<div class="lembar">
      ${u.foto.length ? `<div class="foto-besar ${u.foto.length > 1 ? "dua" : ""}">${u.foto.map((f) => `<img src="${esc(f)}" alt="" loading="lazy">`).join("")}</div>` : ""}
      <div class="pesan">${esc(u.pesan)}</div>
      ${u.suara ? `<audio controls preload="none" src="${esc(u.suara)}"></audio>` : ""}
      <div class="dari"><strong>— ${esc(u.nama)}</strong>${u.hubungan ? esc(u.hubungan) : ""}</div>
    </div>`),
    `<div class="lembar judul"><h2>Terima kasih</h2>
      <p class="pudar">Dikumpulkan dengan sayang oleh ${esc(buku.pembuat)}</p>
      <div class="penulis-lain">${buku.ucapan.map((u) => `<span class="chip">${esc(u.nama)}</span>`).join("")}</div></div>`,
  ];

  app.innerHTML = `<section class="buku">
    <div class="halaman-wadah" id="wadah">${halaman.map((h) => `<div class="halaman">${h}</div>`).join("")}</div>
    <nav class="navigasi-buku">
      <button type="button" id="mundur" aria-label="Halaman sebelumnya">‹</button>
      <span id="nomor">1 / ${halaman.length}</span>
      <button type="button" id="maju" aria-label="Halaman berikutnya">›</button>
    </nav>
  </section>`;

  const wadah = document.getElementById("wadah");
  const nomor = document.getElementById("nomor");
  const mundur = document.getElementById("mundur");
  const maju = document.getElementById("maju");
  const sekarang = () => Math.round(wadah.scrollLeft / wadah.clientWidth);
  const ke = (i) => wadah.scrollTo({ left: i * wadah.clientWidth, behavior: "smooth" });
  const perbarui = () => {
    const i = sekarang();
    nomor.textContent = `${i + 1} / ${halaman.length}`;
    mundur.disabled = i === 0;
    maju.disabled = i === halaman.length - 1;
  };
  wadah.addEventListener("scroll", perbarui, { passive: true });
  mundur.onclick = () => ke(sekarang() - 1);
  maju.onclick = () => ke(sekarang() + 1);
  document.onkeydown = (e) => {
    if (e.key === "ArrowRight") ke(sekarang() + 1);
    if (e.key === "ArrowLeft") ke(sekarang() - 1);
  };
  perbarui();
}

// ─── Mulai ────────────────────────────────────────────────────────────────────

window.addEventListener("popstate", rute);
rute();

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
}
