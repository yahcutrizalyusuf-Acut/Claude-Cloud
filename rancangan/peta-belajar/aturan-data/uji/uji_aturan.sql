-- =====================================================================
-- Uji aturan data. Setiap uji mencetak LULUS, atau berhenti dengan GAGAL.
-- Jalankan: psql -v ON_ERROR_STOP=1 -f 00_tiruan_supabase.sql
--           psql -v ON_ERROR_STOP=1 -f ../supabase/migrations/20261016000001_aturan_data.sql
--           psql -v ON_ERROR_STOP=1 -f uji_aturan.sql
-- =====================================================================
\set QUIET on
set client_min_messages = notice;

-- ---------- Data contoh (dimasukkan oleh pemilik database) ----------
create or replace function pg_temp.u(i int) returns uuid language sql immutable as
$$ select ('00000000-0000-0000-0000-' || lpad(i::text, 12, '0'))::uuid $$;

insert into auth.users (id, email) select pg_temp.u(i), 'pengguna' || i || '@contoh.id' from generate_series(1, 25) i;
insert into pribadi.pengguna (id, nama_tampilan, umur_18) select pg_temp.u(i), 'Pengguna ' || i, true from generate_series(1, 25) i;
insert into pribadi.kontak (pengguna_id, email) select pg_temp.u(i), 'pengguna' || i || '@contoh.id' from generate_series(1, 25) i;
insert into pribadi.persetujuan (pengguna_id, tujuan, versi_teks) select pg_temp.u(i), 'perbaikan_mesin', 'v1' from generate_series(1, 22) i;
insert into pribadi.persetujuan (pengguna_id, tujuan, versi_teks) select pg_temp.u(i), 'promosi', 'v1' from generate_series(1, 3) i;
insert into pribadi.profil_belajar (pengguna_id, topik) select pg_temp.u(i), 'Belajar Excel' from generate_series(1, 21) i;
insert into pribadi.profil_belajar (pengguna_id, topik) select pg_temp.u(i), 'cara berhenti judi online' from generate_series(22, 23) i;
insert into publik.rencana (id, topik, susunan) values ('11111111-1111-1111-1111-111111111111', 'belajar excel', '{}');
insert into publik.video (id_youtube, judul, kanal, durasi_detik) values ('vid1', 'Excel dasar', 'Kanal A', 600);
insert into publik.video (id_youtube, judul, kanal, durasi_detik, diambil_pada) values ('vidlama', 'Video lama', 'Kanal B', 300, now() - interval '31 days');
insert into publik.judul (id, rencana_id, urutan, nama, video_utama) values ('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', 1, 'Kenal Excel', 'vid1');
insert into pribadi.catatan (pengguna_id, jenis, isi) values
  (pg_temp.u(1), 'catatan', 'catatan rahasia pengguna 1'),
  (pg_temp.u(2), 'catatan', 'catatan rahasia pengguna 2'),
  (pg_temp.u(3), 'tanya',   'kenapa rumus saya error?');
insert into pribadi.penilaian (pengguna_id, video_id, nilai) select pg_temp.u(i), 'vid1', case when i <= 15 then 'membantu' else 'tidak_sesuai' end from generate_series(1, 22) i;

-- ================= Pengguna =================
set role authenticated;
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000001', false);

do $$ declare n int; begin
  select count(*) into n from pribadi.catatan;
  assert n = 1, 'GAGAL 1: pengguna 1 melihat ' || n || ' catatan, seharusnya 1';
  raise notice 'LULUS 1: pengguna hanya melihat catatannya sendiri';
end $$;

do $$ begin
  begin
    insert into pribadi.catatan (pengguna_id, jenis, isi) values ('00000000-0000-0000-0000-000000000002', 'catatan', 'menyusup');
    raise exception 'GAGAL 2: pengguna bisa menulis atas nama orang lain';
  exception when insufficient_privilege then
    raise notice 'LULUS 2: pengguna tidak bisa menulis atas nama orang lain';
  end;
end $$;

do $$ declare n int; begin
  update pribadi.catatan set isi = 'diubah' where pengguna_id = '00000000-0000-0000-0000-000000000002';
  get diagnostics n = row_count;
  assert n = 0, 'GAGAL 3: pengguna bisa mengubah catatan orang lain';
  raise notice 'LULUS 3: pengguna tidak bisa mengubah catatan orang lain';
end $$;

do $$ declare d jsonb; begin
  d := pribadi.unduh_dataku();
  assert jsonb_array_length(d->'catatan') = 1, 'GAGAL 4: unduhan berisi catatan orang lain';
  assert d->'pengguna'->>'id' = '00000000-0000-0000-0000-000000000001', 'GAGAL 4: unduhan salah orang';
  raise notice 'LULUS 4: Unduh dataku hanya berisi data milik sendiri';
end $$;

do $$ begin
  begin
    perform 1 from audit.akses_data limit 1;
    raise exception 'GAGAL 5: pengguna bisa membaca catatan akses';
  exception when insufficient_privilege then
    raise notice 'LULUS 5: pengguna tidak bisa membaca catatan akses';
  end;
end $$;

-- Pengguna 1 dan 2 menarik persetujuan perbaikan mesin.
select pribadi.tarik_persetujuan('perbaikan_mesin');
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000002', false);
select pribadi.tarik_persetujuan('perbaikan_mesin');
reset role;

-- ================= Tamu =================
set role anon;
do $$ begin
  begin
    perform 1 from pribadi.catatan limit 1;
    raise exception 'GAGAL 6: tamu bisa membaca data pribadi';
  exception when insufficient_privilege then
    raise notice 'LULUS 6: tamu tidak bisa membaca data pribadi';
  end;
end $$;
do $$ declare n int; begin
  select count(*) into n from publik.video;
  assert n = 2, 'GAGAL 7: tamu tidak bisa membaca jalur publik';
  raise notice 'LULUS 7: tamu tetap bisa membaca jalur dan video publik';
end $$;
reset role;

-- ================= Pengelola laporan =================
set role pengelola_laporan;
do $$ declare t text; begin
  foreach t in array array['pengguna','kontak','catatan','penilaian','profil_belajar','persetujuan','izin_akses'] loop
    begin
      execute format('select 1 from pribadi.%I limit 1', t);
      raise exception 'GAGAL 8: pengelola laporan bisa membaca pribadi.%', t;
    exception when insufficient_privilege then null;
    end;
  end loop;
  raise notice 'LULUS 8: pengelola laporan tidak bisa membuka satu pun tabel data pribadi';
end $$;

do $$ declare n int; begin
  select count(*) into n from laporan.topik_populer;
  assert n = 0, 'GAGAL 9: laporan menampilkan topik dengan kurang dari 20 orang';
  raise notice 'LULUS 9: "belajar excel" turun ke 19 orang setelah 2 menarik persetujuan, jadi disembunyikan; "judi online" (2 orang) juga disembunyikan';
end $$;

do $$ declare r record; begin
  select * into r from laporan.nilai_video where video_id = 'vid1';
  assert r.jumlah_penilai = 20, 'GAGAL 10: jumlah penilai salah: ' || coalesce(r.jumlah_penilai::text, 'kosong');
  assert r.persen_membantu = 65.0, 'GAGAL 10: persen membantu salah: ' || r.persen_membantu;
  raise notice 'LULUS 10: nilai video hanya dari 20 orang yang masih setuju (65%% membantu)';
end $$;

do $$ begin
  begin
    perform * from layanan.penerima_promosi();
    raise exception 'GAGAL 11: pengelola laporan bisa mengambil email';
  exception when insufficient_privilege then
    raise notice 'LULUS 11: pengelola laporan tidak bisa mengambil daftar email';
  end;
end $$;
reset role;

-- ================= Pengelola bantuan =================
set role pengelola_bantuan;
do $$ declare n int; begin
  select count(*) into n from bantuan.lihat_catatan_dengan_izin('00000000-0000-0000-0000-000000000003', 'TIKET-1');
  assert n = 0, 'GAGAL 12: catatan terbuka tanpa izin';
  raise notice 'LULUS 12: tanpa izin pengguna, catatan tidak terbuka';
end $$;
do $$ begin
  begin
    perform 1 from pribadi.catatan limit 1;
    raise exception 'GAGAL 13: pengelola bantuan bisa membaca tabel catatan langsung';
  exception when insufficient_privilege then
    raise notice 'LULUS 13: pengelola bantuan tidak bisa membuka tabel catatan secara langsung';
  end;
end $$;
reset role;

-- Pengguna 3 memberi izin untuk tiket TIKET-1.
set role authenticated;
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000003', false);
do $$ begin
  begin
    perform pribadi.beri_izin_akses('TIKET-1', 'rumus error', 100);
    raise exception 'GAGAL 14: izin lebih dari 72 jam diterima';
  exception when raise_exception then
    if sqlerrm like 'GAGAL%' then raise; end if;
    raise notice 'LULUS 14: izin lebih dari 72 jam ditolak';
  end;
end $$;
select pribadi.beri_izin_akses('TIKET-1', 'rumus error', 72);
reset role;

set role pengelola_bantuan;
do $$ declare n int; begin
  select count(*) into n from bantuan.lihat_catatan_dengan_izin('00000000-0000-0000-0000-000000000003', 'TIKET-1');
  assert n = 1, 'GAGAL 15: dengan izin, catatan tidak terbuka';
  select count(*) into n from bantuan.lihat_catatan_dengan_izin('00000000-0000-0000-0000-000000000003', 'TIKET-LAIN');
  assert n = 0, 'GAGAL 15: izin untuk satu tiket berlaku untuk tiket lain';
  select count(*) into n from bantuan.lihat_catatan_dengan_izin('00000000-0000-0000-0000-000000000001', 'TIKET-1');
  assert n = 0, 'GAGAL 15: izin pengguna 3 membuka catatan pengguna 1';
  raise notice 'LULUS 15: izin hanya membuka catatan pengguna itu, untuk tiket itu';
end $$;
reset role;

-- ================= Layanan (fungsi server) =================
set role service_role;
do $$ declare n int; begin
  select count(*) into n from layanan.penerima_promosi();
  assert n = 3, 'GAGAL 16: penerima promosi bukan hanya yang setuju: ' || n;
  raise notice 'LULUS 16: email promosi hanya untuk 3 orang yang setuju';
end $$;
reset role;

-- ================= Catatan akses =================
do $$ declare n int; begin
  select count(*) into n from audit.akses_data where tindakan = 'lihat_catatan_ditolak';
  assert n = 3, 'GAGAL 17: percobaan ditolak tidak tercatat lengkap: ' || n;
  select count(*) into n from audit.akses_data where tindakan = 'lihat_catatan_diizinkan';
  assert n = 1, 'GAGAL 17: akses berizin tidak tercatat';
  select count(*) into n from audit.akses_data where tindakan = 'ambil_penerima_promosi';
  assert n = 1, 'GAGAL 17: pengambilan email tidak tercatat';
  raise notice 'LULUS 17: setiap percobaan akses tercatat, termasuk yang ditolak';
end $$;

do $$ begin
  begin
    update audit.akses_data set alasan = 'dihapus jejak';
    raise exception 'GAGAL 18: catatan akses bisa diubah';
  exception when raise_exception then
    if sqlerrm like 'GAGAL%' then raise; end if;
  end;
  begin
    delete from audit.akses_data;
    raise exception 'GAGAL 18: catatan akses bisa dihapus';
  exception when raise_exception then
    if sqlerrm like 'GAGAL%' then raise; end if;
  end;
  raise notice 'LULUS 18: catatan akses tidak bisa diubah atau dihapus, bahkan oleh pemilik database';
end $$;

-- ================= Umur =================
do $$ begin
  begin
    insert into auth.users (id) values ('00000000-0000-0000-0000-000000000099');
    insert into pribadi.pengguna (id, umur_18) values ('00000000-0000-0000-0000-000000000099', false);
    raise exception 'GAGAL 19: pengguna di bawah 18 tahun diterima';
  exception when check_violation then
    raise notice 'LULUS 19: pengguna di bawah 18 tahun ditolak';
  end;
end $$;

-- ================= Hapus akun =================
set role authenticated;
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000005', false);
select pribadi.hapus_akunku();
reset role;
do $$ declare n int; begin
  select count(*) into n from pribadi.pengguna where id = '00000000-0000-0000-0000-000000000005';
  assert n = 0, 'GAGAL 20: akun tidak terhapus';
  select (select count(*) from pribadi.kontak where pengguna_id = '00000000-0000-0000-0000-000000000005')
       + (select count(*) from pribadi.persetujuan where pengguna_id = '00000000-0000-0000-0000-000000000005')
       + (select count(*) from pribadi.profil_belajar where pengguna_id = '00000000-0000-0000-0000-000000000005')
       + (select count(*) from pribadi.penilaian where pengguna_id = '00000000-0000-0000-0000-000000000005') into n;
  assert n = 0, 'GAGAL 20: masih ada sisa data akun yang dihapus: ' || n;
  select count(*) into n from audit.akses_data where tindakan = 'hapus_akun' and pengguna_id = '00000000-0000-0000-0000-000000000005';
  assert n = 1, 'GAGAL 20: penghapusan tidak tercatat';
  raise notice 'LULUS 20: Hapus akun menghapus semua data pribadi dan tercatat';
end $$;

-- ================= Masa simpan =================
update pribadi.pengguna set terakhir_aktif = now() - interval '25 months', diberi_tahu_tidak_aktif = now() - interval '40 days' where id = '00000000-0000-0000-0000-000000000006';
update pribadi.pengguna set terakhir_aktif = now() - interval '23 months 10 days' where id = '00000000-0000-0000-0000-000000000007';
set role service_role;
select * from pribadi.proses_akun_tidak_aktif();
select publik.bersihkan_data_youtube();
reset role;
do $$ declare n int; d timestamptz; v text; begin
  select count(*) into n from pribadi.pengguna where id = '00000000-0000-0000-0000-000000000006';
  assert n = 0, 'GAGAL 21: akun tidak aktif 24 bulan tidak terhapus';
  select diberi_tahu_tidak_aktif into d from pribadi.pengguna where id = '00000000-0000-0000-0000-000000000007';
  assert d is not null, 'GAGAL 21: akun tidak aktif 23 bulan tidak ditandai';
  select judul into v from publik.video where id_youtube = 'vidlama';
  assert v is null, 'GAGAL 21: data YouTube lebih dari 30 hari tidak dibersihkan';
  select judul into v from publik.video where id_youtube = 'vid1';
  assert v is not null, 'GAGAL 21: data YouTube yang masih baru ikut terhapus';
  raise notice 'LULUS 21: masa simpan berjalan (akun 24 bulan dihapus, 23 bulan diberi tahu, data YouTube lama dibersihkan)';
end $$;

-- ================= Kurator =================
set role pengelola_kurator;
do $$ declare n int; begin
  begin
    perform 1 from pribadi.penilaian limit 1;
    raise exception 'GAGAL 22: kurator bisa membaca penilaian perorangan';
  exception when insufficient_privilege then null;
  end;
  select count(*) into n from laporan.nilai_video;
  assert n = 0, 'GAGAL 22: nilai video dengan kurang dari 20 penilai ikut tampil';
  raise notice 'LULUS 22: kurator hanya melihat nilai gabungan, dan setelah 2 akun terhapus (penilai tinggal 18) angkanya ikut disembunyikan';
end $$;
reset role;

\echo
\echo 'SEMUA UJI LULUS'
