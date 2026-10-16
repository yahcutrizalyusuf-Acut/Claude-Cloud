-- =====================================================================
-- Khusus Supabase: jadwal otomatis dan catatan akses pemilik proyek.
-- Berkas ini tidak dijalankan di database uji lokal.
-- =====================================================================

-- Jadwal masa simpan (pg_cron).
create extension if not exists pg_cron;

select cron.schedule('masa-simpan-akun',      '15 2 * * *',   $$select pribadi.proses_akun_tidak_aktif()$$);
select cron.schedule('hapus-izin-kedaluwarsa', '*/30 * * * *', $$select pribadi.hapus_izin_kedaluwarsa()$$);
select cron.schedule('bersihkan-data-youtube', '30 3 * * *',   $$select publik.bersihkan_data_youtube()$$);

-- Catat semua perintah yang dijalankan pemilik proyek, termasuk lewat
-- dasbor Supabase. Peran postgres bisa melewati Row Level Security,
-- jadi jejaknya harus selalu ada.
create extension if not exists pgaudit;
alter role postgres set pgaudit.log to 'read, write, ddl, role';
alter role service_role set pgaudit.log to 'write, ddl, role';

-- Catatan: penyimpanan log di paket gratis Supabase sangat pendek.
-- Log perlu diekspor rutin bersama cadangan mingguan.
