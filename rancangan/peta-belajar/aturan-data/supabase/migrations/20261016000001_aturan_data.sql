-- =====================================================================
-- Peta Belajar: aturan data pribadi yang ditegakkan oleh database
-- Dasar: UU 27/2022 tentang Pelindungan Data Pribadi (rangkuman di
-- rancangan-sistem.md, bab Batasan Hukum Data Pribadi).
--
-- Prinsip:
--   1. Pengguna hanya bisa melihat dan mengubah datanya sendiri.
--   2. Pengelola (Acut, Acut2, kurator) TIDAK punya akses langsung ke
--      tabel data pribadi. Mereka hanya melihat angka gabungan.
--   3. Isi catatan hanya bisa dibuka pengelola kalau pengguna sendiri
--      memberi izin, paling lama 72 jam, dan setiap percobaan dicatat.
--   4. Data untuk tujuan tambahan hanya dipakai kalau ada persetujuan
--      yang masih berlaku.
--   5. Catatan akses hanya bisa ditambah, tidak bisa diubah atau dihapus.
--   6. Data dihapus otomatis sesuai masa simpan.
--
-- Batas yang jujur: pemilik proyek Supabase (peran postgres dan kunci
-- service_role) secara teknis tetap bisa melewati aturan ini. Karena
-- itu akses tersebut hanya dipakai untuk pemeliharaan, dicatat oleh
-- pgaudit (berkas 20261016000002), dan dijaga verifikasi dua langkah.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Peran
-- ---------------------------------------------------------------------
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'penjaga_data') then
    -- Pemilik fungsi resmi. Tidak bisa dipakai untuk masuk (nologin),
    -- dan tidak diberikan kepada siapa pun.
    create role penjaga_data nologin;
  end if;
  if not exists (select 1 from pg_roles where rolname = 'pengelola_laporan') then
    create role pengelola_laporan nologin;  -- hanya angka gabungan
  end if;
  if not exists (select 1 from pg_roles where rolname = 'pengelola_kurator') then
    create role pengelola_kurator nologin;  -- jalur, judul, video
  end if;
  if not exists (select 1 from pg_roles where rolname = 'pengelola_bantuan') then
    create role pengelola_bantuan nologin;  -- membantu pengguna, dengan izin
  end if;
end $$;

-- Di Supabase, peran postgres bukan superuser. Supaya bisa menjadikan
-- penjaga_data pemilik fungsi, postgres perlu keanggotaan peran itu.
do $$
begin
  if not (select rolsuper from pg_roles where rolname = current_user) then
    execute format('grant penjaga_data to %I', current_user);
  end if;
end $$;

-- Akun login manusia diberi peran di atas, misalnya:
--   create role acut_laporan login password '...';
--   grant pengelola_laporan to acut_laporan;
-- Jangan pernah memberikan penjaga_data kepada akun login.

-- ---------------------------------------------------------------------
-- Skema
-- ---------------------------------------------------------------------
create schema if not exists pribadi;  -- data pribadi pengguna
create schema if not exists publik;   -- jalur, judul, video: tanpa data pribadi
create schema if not exists laporan;  -- angka gabungan untuk pengelola
create schema if not exists bantuan;  -- akses dengan izin pengguna
create schema if not exists layanan;  -- dipakai fungsi server (service_role)
create schema if not exists audit;    -- catatan akses

revoke all on schema pribadi, publik, laporan, bantuan, layanan, audit from public;
grant usage on schema pribadi to authenticated, penjaga_data;
grant usage on schema publik  to anon, authenticated, pengelola_kurator, penjaga_data;
grant usage on schema laporan to pengelola_laporan, pengelola_kurator;
grant usage on schema bantuan to pengelola_bantuan;
grant usage on schema layanan, pribadi, publik to service_role;
grant usage on schema audit   to penjaga_data;
grant create on schema pribadi, publik, laporan, bantuan, layanan, audit to penjaga_data;

-- Fungsi baru tidak otomatis bisa dijalankan semua orang.
alter default privileges revoke execute on functions from public;

-- ---------------------------------------------------------------------
-- Catatan akses: hanya bisa ditambah
-- ---------------------------------------------------------------------
create table if not exists audit.akses_data (
  id          bigserial primary key,
  waktu       timestamptz not null default now(),
  pelaku      text not null default session_user,  -- akun yang masuk
  peran       text not null default current_user,  -- peran yang dipakai
  tindakan    text not null,
  pengguna_id uuid,
  alasan      text,
  tiket       text,
  jumlah_baris integer
);
revoke all on audit.akses_data from public;
grant insert on audit.akses_data to penjaga_data;
grant usage on sequence audit.akses_data_id_seq to penjaga_data;

create or replace function audit.tolak_ubah() returns trigger
language plpgsql as $$
begin
  raise exception 'Catatan akses tidak boleh diubah atau dihapus';
end $$;

drop trigger if exists jaga_audit on audit.akses_data;
create trigger jaga_audit before update or delete on audit.akses_data
  for each row execute function audit.tolak_ubah();
drop trigger if exists jaga_audit_truncate on audit.akses_data;
create trigger jaga_audit_truncate before truncate on audit.akses_data
  for each statement execute function audit.tolak_ubah();

-- Hanya pemilik akun Supabase yang membaca catatan akses, untuk pemeriksaan.

-- ---------------------------------------------------------------------
-- Data publik (tanpa data pribadi)
-- ---------------------------------------------------------------------
create table if not exists publik.rencana (
  id         uuid primary key default gen_random_uuid(),
  topik      text not null,
  susunan    jsonb not null,           -- modul dan judul
  status     text not null default 'otomatis' check (status in ('otomatis','teruji')),
  dibuat_pada timestamptz not null default now()
);

create table if not exists publik.video (
  id_youtube  text primary key,
  judul       text,
  kanal       text,
  durasi_detik integer,
  diambil_pada timestamptz not null default now()  -- wajib disegarkan tiap 30 hari
);

create table if not exists publik.judul (
  id         uuid primary key default gen_random_uuid(),
  rencana_id uuid not null references publik.rencana(id) on delete cascade,
  urutan     integer not null,
  nama       text not null,
  video_utama text references publik.video(id_youtube) on delete set null
);

grant select on publik.rencana, publik.judul, publik.video to anon, authenticated;
grant select, insert, update on publik.rencana, publik.judul, publik.video to pengelola_kurator;
grant select, update on publik.video to penjaga_data;

-- ---------------------------------------------------------------------
-- Data pribadi
-- ---------------------------------------------------------------------
create table if not exists pribadi.pengguna (
  id            uuid primary key references auth.users(id) on delete cascade,
  nama_tampilan text,
  umur_18       boolean not null check (umur_18),   -- Pasal 25: tidak menerima anak
  dibuat_pada   timestamptz not null default now(),
  terakhir_aktif timestamptz not null default now(),
  diberi_tahu_tidak_aktif timestamptz
);

-- Email dipisah supaya tidak ikut terbaca di mana pun kecuali fungsi pemberitahuan.
create table if not exists pribadi.kontak (
  pengguna_id uuid primary key references pribadi.pengguna(id) on delete cascade,
  email       text not null
);

create table if not exists pribadi.persetujuan (
  id          bigserial primary key,
  pengguna_id uuid not null references pribadi.pengguna(id) on delete cascade,
  tujuan      text not null check (tujuan in
                ('perbaikan_mesin','promosi','testimoni','laporan_lembaga','hubungkan_pelatihan')),
  versi_teks  text not null,                -- versi teks yang disetujui (Pasal 22)
  diberikan_pada timestamptz not null default now(),
  ditarik_pada   timestamptz
);
create unique index if not exists persetujuan_satu_aktif
  on pribadi.persetujuan (pengguna_id, tujuan) where ditarik_pada is null;

create table if not exists pribadi.profil_belajar (
  id          uuid primary key default gen_random_uuid(),
  pengguna_id uuid not null references pribadi.pengguna(id) on delete cascade,
  topik       text not null,
  jawaban     jsonb not null default '{}',
  rencana_id  uuid references publik.rencana(id) on delete set null,
  dibuat_pada timestamptz not null default now()
);

create table if not exists pribadi.kemajuan (
  id          uuid primary key default gen_random_uuid(),
  pengguna_id uuid not null references pribadi.pengguna(id) on delete cascade,
  judul_id    uuid not null references publik.judul(id) on delete cascade,
  persen_tonton integer not null default 0 check (persen_tonton between 0 and 100),
  selesai     boolean not null default false,
  diperbarui  timestamptz not null default now()
);

create table if not exists pribadi.catatan (
  id          uuid primary key default gen_random_uuid(),
  pengguna_id uuid not null references pribadi.pengguna(id) on delete cascade,
  judul_id    uuid references publik.judul(id) on delete set null,
  jenis       text not null check (jenis in ('catatan','tanya','jawaban','kesimpulan')),
  detik       integer,
  isi         text not null check (length(isi) <= 4000),
  dibuat_pada timestamptz not null default now()
);

create table if not exists pribadi.penilaian (
  id          uuid primary key default gen_random_uuid(),
  pengguna_id uuid not null references pribadi.pengguna(id) on delete cascade,
  video_id    text not null references publik.video(id_youtube) on delete cascade,
  nilai       text not null check (nilai in ('membantu','tidak_sesuai')),
  persen_tonton integer check (persen_tonton between 0 and 100),
  dibuat_pada timestamptz not null default now()
);

create table if not exists pribadi.izin_akses (
  id          uuid primary key default gen_random_uuid(),
  pengguna_id uuid not null references pribadi.pengguna(id) on delete cascade,
  tiket       text not null,
  alasan      text not null,
  diberikan_pada timestamptz not null default now(),
  berlaku_sampai timestamptz not null
);

-- Izin paling lama 72 jam.
create or replace function pribadi.batasi_izin() returns trigger
language plpgsql as $$
begin
  if new.berlaku_sampai > now() + interval '72 hours' then
    raise exception 'Izin akses paling lama 72 jam';
  end if;
  if new.berlaku_sampai <= now() then
    raise exception 'Izin akses harus berlaku ke depan';
  end if;
  return new;
end $$;
drop trigger if exists jaga_izin on pribadi.izin_akses;
create trigger jaga_izin before insert or update on pribadi.izin_akses
  for each row execute function pribadi.batasi_izin();

-- ---------------------------------------------------------------------
-- Kunci baris: Row Level Security, juga berlaku untuk pemilik tabel
-- ---------------------------------------------------------------------
do $$
declare t text;
begin
  foreach t in array array['pengguna','kontak','persetujuan','profil_belajar',
                           'kemajuan','catatan','penilaian','izin_akses'] loop
    execute format('alter table pribadi.%I enable row level security', t);
    execute format('alter table pribadi.%I force row level security', t);
    execute format('revoke all on pribadi.%I from public, anon', t);
  end loop;
end $$;

-- Pengguna: hanya baris miliknya sendiri.
drop policy if exists milik_sendiri on pribadi.pengguna;
create policy milik_sendiri on pribadi.pengguna for all to authenticated
  using (id = auth.uid()) with check (id = auth.uid());

do $$
declare t text;
begin
  foreach t in array array['kontak','persetujuan','profil_belajar','kemajuan',
                           'catatan','penilaian','izin_akses'] loop
    execute format('drop policy if exists milik_sendiri on pribadi.%I', t);
    execute format('create policy milik_sendiri on pribadi.%I for all to authenticated
                    using (pengguna_id = auth.uid()) with check (pengguna_id = auth.uid())', t);
    -- Fungsi resmi berjalan sebagai penjaga_data.
    execute format('drop policy if exists fungsi_resmi on pribadi.%I', t);
    execute format('create policy fungsi_resmi on pribadi.%I for all to penjaga_data
                    using (true) with check (true)', t);
  end loop;
end $$;
drop policy if exists fungsi_resmi on pribadi.pengguna;
create policy fungsi_resmi on pribadi.pengguna for all to penjaga_data using (true) with check (true);

grant select, insert, update, delete on all tables in schema pribadi to authenticated;
grant usage on all sequences in schema pribadi to authenticated;
grant select, insert, update, delete on all tables in schema pribadi to penjaga_data;

-- Persetujuan tidak dihapus atau ditimpa oleh pengguna: hanya ditarik.
revoke delete on pribadi.persetujuan from authenticated;

-- Pengelola sengaja tidak diberi hak apa pun di skema pribadi.

-- ---------------------------------------------------------------------
-- Hak pengguna (dipanggil dari aplikasi)
-- ---------------------------------------------------------------------

-- Unduh dataku: semua data milik pemanggil, sebagai satu berkas JSON.
create or replace function pribadi.unduh_dataku() returns jsonb
language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object(
    'pengguna',       (select to_jsonb(p) from pribadi.pengguna p where p.id = auth.uid()),
    'kontak',         (select to_jsonb(k) from pribadi.kontak k where k.pengguna_id = auth.uid()),
    'persetujuan',    (select coalesce(jsonb_agg(s), '[]') from pribadi.persetujuan s where s.pengguna_id = auth.uid()),
    'profil_belajar', (select coalesce(jsonb_agg(b), '[]') from pribadi.profil_belajar b where b.pengguna_id = auth.uid()),
    'kemajuan',       (select coalesce(jsonb_agg(m), '[]') from pribadi.kemajuan m where m.pengguna_id = auth.uid()),
    'catatan',        (select coalesce(jsonb_agg(c), '[]') from pribadi.catatan c where c.pengguna_id = auth.uid()),
    'penilaian',      (select coalesce(jsonb_agg(n), '[]') from pribadi.penilaian n where n.pengguna_id = auth.uid()),
    'diunduh_pada',   now()
  );
$$;
grant execute on function pribadi.unduh_dataku() to authenticated;

-- Tarik persetujuan untuk satu tujuan.
create or replace function pribadi.tarik_persetujuan(p_tujuan text) returns void
language sql security invoker set search_path = '' as $$
  update pribadi.persetujuan set ditarik_pada = now()
   where pengguna_id = auth.uid() and tujuan = p_tujuan and ditarik_pada is null;
$$;
grant execute on function pribadi.tarik_persetujuan(text) to authenticated;

-- Beri izin pengelola melihat catatan untuk satu laporan masalah.
create or replace function pribadi.beri_izin_akses(p_tiket text, p_alasan text, p_jam integer default 72)
returns uuid language sql security invoker set search_path = '' as $$
  insert into pribadi.izin_akses (pengguna_id, tiket, alasan, berlaku_sampai)
  values (auth.uid(), p_tiket, p_alasan, now() + make_interval(hours => p_jam))
  returning id;
$$;
grant execute on function pribadi.beri_izin_akses(text, text, integer) to authenticated;

-- Hapus akunku: seluruh data pribadi terhapus. Akun login di auth.users
-- dihapus oleh fungsi server setelah fungsi ini berhasil.
-- Pencatatan memakai fungsi kecil milik penjaga_data, sebab pengguna
-- tidak punya hak menulis langsung ke catatan akses.
create or replace function audit.catat_hapus_akun(p_pengguna uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if exists (select 1 from pribadi.pengguna where id = p_pengguna) then
    raise exception 'Akun masih ada, penghapusan belum terjadi';
  end if;
  insert into audit.akses_data (tindakan, pengguna_id, alasan)
  values ('hapus_akun', p_pengguna, 'permintaan pengguna');
end $$;
alter function audit.catat_hapus_akun(uuid) owner to penjaga_data;
grant usage on schema audit to authenticated;
grant execute on function audit.catat_hapus_akun(uuid) to authenticated;

create or replace function pribadi.hapus_akunku() returns void
language plpgsql security invoker set search_path = '' as $$
declare v_id uuid := auth.uid();
begin
  if v_id is null then
    raise exception 'Harus masuk dulu';
  end if;
  delete from pribadi.pengguna where id = v_id;  -- tabel lain ikut terhapus
  if not found then
    raise exception 'Akun tidak ditemukan';
  end if;
  perform audit.catat_hapus_akun(v_id);
end $$;
grant execute on function pribadi.hapus_akunku() to authenticated;

-- ---------------------------------------------------------------------
-- Akses bantuan: hanya dengan izin pengguna, selalu dicatat
-- ---------------------------------------------------------------------
create or replace function bantuan.lihat_catatan_dengan_izin(p_pengguna uuid, p_tiket text)
returns table (jenis text, detik integer, isi text, dibuat_pada timestamptz)
language plpgsql security definer set search_path = '' as $$
declare v_ada boolean; v_jumlah integer;
begin
  select exists (
    select 1 from pribadi.izin_akses i
     where i.pengguna_id = p_pengguna and i.tiket = p_tiket and i.berlaku_sampai > now()
  ) into v_ada;

  if not v_ada then
    -- Percobaan tanpa izin tetap dicatat, lalu tidak ada data yang dikembalikan.
    insert into audit.akses_data (tindakan, pengguna_id, tiket, alasan, jumlah_baris)
    values ('lihat_catatan_ditolak', p_pengguna, p_tiket, 'tidak ada izin yang berlaku', 0);
    return;
  end if;

  select count(*) into v_jumlah from pribadi.catatan c where c.pengguna_id = p_pengguna;
  insert into audit.akses_data (tindakan, pengguna_id, tiket, alasan, jumlah_baris)
  values ('lihat_catatan_diizinkan', p_pengguna, p_tiket, 'izin pengguna', v_jumlah);

  return query
    select c.jenis, c.detik, c.isi, c.dibuat_pada
      from pribadi.catatan c where c.pengguna_id = p_pengguna
     order by c.dibuat_pada;
end $$;
alter function bantuan.lihat_catatan_dengan_izin(uuid, text) owner to penjaga_data;
grant execute on function bantuan.lihat_catatan_dengan_izin(uuid, text) to pengelola_bantuan;

-- ---------------------------------------------------------------------
-- Laporan: hanya angka gabungan, minimal 20 orang per angka
-- ---------------------------------------------------------------------
create or replace function laporan.ambang() returns integer
language sql immutable as $$ select 20 $$;
grant execute on function laporan.ambang() to penjaga_data, pengelola_laporan, pengelola_kurator;

-- Topik yang dicari, hanya dari pengguna yang setuju membantu memperbaiki mesin.
create or replace view laporan.topik_populer with (security_barrier) as
  select lower(btrim(b.topik)) as topik,
         count(distinct b.pengguna_id) as jumlah_pengguna
    from pribadi.profil_belajar b
    join pribadi.persetujuan s
      on s.pengguna_id = b.pengguna_id and s.tujuan = 'perbaikan_mesin' and s.ditarik_pada is null
   group by lower(btrim(b.topik))
  having count(distinct b.pengguna_id) >= laporan.ambang();
alter view laporan.topik_populer owner to penjaga_data;

-- Nilai video dari pengguna yang setuju.
create or replace view laporan.nilai_video with (security_barrier) as
  select n.video_id,
         count(distinct n.pengguna_id) as jumlah_penilai,
         round(100.0 * count(*) filter (where n.nilai = 'membantu') / count(*), 1) as persen_membantu
    from pribadi.penilaian n
    join pribadi.persetujuan s
      on s.pengguna_id = n.pengguna_id and s.tujuan = 'perbaikan_mesin' and s.ditarik_pada is null
   group by n.video_id
  having count(distinct n.pengguna_id) >= laporan.ambang();
alter view laporan.nilai_video owner to penjaga_data;

-- Ringkasan bulanan: hanya jumlah, tanpa isi apa pun.
create or replace view laporan.ringkasan_bulanan with (security_barrier) as
  select date_trunc('month', p.terakhir_aktif)::date as bulan,
         count(*) as pengguna_aktif
    from pribadi.pengguna p
   group by 1;
alter view laporan.ringkasan_bulanan owner to penjaga_data;

grant select on laporan.topik_populer, laporan.nilai_video, laporan.ringkasan_bulanan to pengelola_laporan;
grant select on laporan.nilai_video to pengelola_kurator;

-- ---------------------------------------------------------------------
-- Pemakaian sesuai persetujuan (dipanggil fungsi server)
-- ---------------------------------------------------------------------
create or replace function layanan.penerima_promosi() returns table (pengguna_id uuid, email text)
language plpgsql security definer set search_path = '' as $$
declare v_jumlah integer;
begin
  select count(*) into v_jumlah
    from pribadi.kontak k
    join pribadi.persetujuan s on s.pengguna_id = k.pengguna_id
   where s.tujuan = 'promosi' and s.ditarik_pada is null;
  insert into audit.akses_data (tindakan, alasan, jumlah_baris)
  values ('ambil_penerima_promosi', 'kirim promosi kepada yang setuju', v_jumlah);
  return query
    select k.pengguna_id, k.email
      from pribadi.kontak k
      join pribadi.persetujuan s on s.pengguna_id = k.pengguna_id
     where s.tujuan = 'promosi' and s.ditarik_pada is null;
end $$;
alter function layanan.penerima_promosi() owner to penjaga_data;
grant execute on function layanan.penerima_promosi() to service_role;

-- ---------------------------------------------------------------------
-- Masa simpan (dijalankan terjadwal, lihat berkas 20261016000002)
-- ---------------------------------------------------------------------

-- Bulan ke-23: tandai untuk diberi tahu. Bulan ke-24: hapus kalau sudah
-- diberi tahu minimal 30 hari dan tetap tidak aktif.
create or replace function pribadi.proses_akun_tidak_aktif() returns table (ditandai integer, dihapus integer)
language plpgsql security definer set search_path = '' as $$
declare v_tandai integer; v_hapus integer;
begin
  update pribadi.pengguna set diberi_tahu_tidak_aktif = now()
   where terakhir_aktif < now() - interval '23 months' and diberi_tahu_tidak_aktif is null;
  get diagnostics v_tandai = row_count;

  delete from pribadi.pengguna
   where terakhir_aktif < now() - interval '24 months'
     and diberi_tahu_tidak_aktif is not null
     and diberi_tahu_tidak_aktif < now() - interval '30 days';
  get diagnostics v_hapus = row_count;

  insert into audit.akses_data (tindakan, alasan, jumlah_baris)
  values ('masa_simpan_akun', format('ditandai %s, dihapus %s', v_tandai, v_hapus), v_hapus);
  return query select v_tandai, v_hapus;
end $$;
alter function pribadi.proses_akun_tidak_aktif() owner to penjaga_data;

create or replace function pribadi.hapus_izin_kedaluwarsa() returns integer
language plpgsql security definer set search_path = '' as $$
declare v integer;
begin
  delete from pribadi.izin_akses where berlaku_sampai <= now();
  get diagnostics v = row_count;
  return v;
end $$;
alter function pribadi.hapus_izin_kedaluwarsa() owner to penjaga_data;

-- Data YouTube yang lebih dari 30 hari tidak disegarkan: judul, kanal,
-- dan durasi dikosongkan sampai disegarkan lagi.
create or replace function publik.bersihkan_data_youtube() returns integer
language plpgsql security definer set search_path = '' as $$
declare v integer;
begin
  update publik.video set judul = null, kanal = null, durasi_detik = null
   where diambil_pada < now() - interval '30 days' and judul is not null;
  get diagnostics v = row_count;
  return v;
end $$;
alter function publik.bersihkan_data_youtube() owner to penjaga_data;

grant execute on function pribadi.proses_akun_tidak_aktif(), pribadi.hapus_izin_kedaluwarsa(),
  publik.bersihkan_data_youtube() to service_role;
