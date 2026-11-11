# BUKU PANDUAN PENGGUNA (MANUAL BOOK)
# SILATTRACK: SISTEM ABSENSI & MANAJEMEN ESKUL PENCAK SILAT MULTI-SEKOLAH

> **Versi Dokumen:** 1.2.0  
> **Target Pengguna:** Administrator (Pembina), Pelatih (Coach), Anggota (Pesilat), dan Orang Tua (Wali Murid)  
> **Teknologi:** DATH Stack (Django 5.2, Alpine.js 3, Tailwind CSS M3, HTMX 2, face-api.js)  
> **Tanggal Rilis:** November 2026  

---

## DAFTAR ISI
1. [Tentang SilatTrack](#1-tentang-silattrack)
2. [Persyaratan Sistem & Cara Menjalankan Aplikasi](#2-persyaratan-sistem--cara-menjalankan-aplikasi)
3. [Daftar Akun Pengguna Bawaan (Default Demo Credentials)](#3-daftar-akun-pengguna-bawaan-default-demo-credentials)
4. [Panduan Pengguna: Administrator / Pembina Eskul](#4-panduan-pengguna-administrator--pembina-eskul)
   - 4.1 Login & Dashboard Admin
   - 4.2 Manajemen Multi-Sekolah & Tanda Tangan Resmi
   - 4.3 Manajemen Akun Pelatih & Pesilat (Validasi NISN 10 Digit)
   - 4.4 Persetujuan Usulan Jadwal & Sesi Fleksibel
   - 4.5 Persetujuan Permohonan Hapus Anggota
   - 4.6 Rekapitulasi & Cetak Laporan Presensi Resmi (Kop Sekolah & Perguruan Ganda)
   - 4.7 Manajemen Identitas Perguruan & Kustomisasi Logo Aplikasi & Sekolah
5. [Panduan Pengguna: Pelatih / Coach (Instruktur)](#5-panduan-pengguna-pelatih--coach-instruktur)
   - 5.1 Login & Dashboard Pelatih
   - 5.2 Membuat & Mengusulkan Sesi Latihan (Rutin & Fleksibel)
   - 5.3 Membuka Sesi & Unggah Foto Dokumentasi Latihan
   - 5.4 Pelaksanaan Presensi di Lapangan (4 Metode)
     - Mode A: AI Face Recognition Scanner (Audit Wajah & Jarak Euclidean)
     - Mode B: Dynamic Rolling QR Code Fullscreen
     - Mode C: Quick Toggle HTMX (Satu Klik)
     - Mode D: Presensi Massal (Tandai Semua Hadir)
   - 5.5 Validasi Surat Izin & Sakit Siswa
   - 5.6 Manajemen Profil Pesilat, Registrasi Wajah & Cetak KTA Fisik
   - 5.7 Mengajukan Mutasi / Hapus Anggota ke Admin
   - 5.8 Menutup Sesi Latihan
   - 5.9 Sertifikat Lisensi Kepelatihan Resmi & Sertifikat Prestasi Siswa
6. [Panduan Pengguna: Anggota / Siswa Pesilat](#6-panduan-pengguna-anggota--siswa-pesilat)
   - 6.1 Login & Dashboard Siswa
   - 6.2 Registrasi Wajah Pertama Kali (*Face Enrollment*)
   - 6.3 Presensi Wajah Mandiri & Pemindaian QR
   - 6.4 Klaim Presensi Darurat Manual
   - 6.5 Pengajuan Surat Izin & Sakit (Lampiran Foto)
   - 6.6 Memantau Syarat Ujian Sabuk (UKT) & Attendance Streak
   - 6.7 Melihat Kartu Tanda Anggota (KTA) Digital (Kebijakan Akses Pratinjau)
   - 6.8 Mengakses & Mencetak Sertifikat Kompetensi Ekstrakurikuler Resmi
7. [Panduan Pengguna: Orang Tua / Wali Murid (Portal Transparansi)](#7-panduan-pengguna-orang-tua--wali-murid-portal-transparansi)
   - 7.1 Mengakses Portal Wali Murid Tanpa Login
   - 7.2 Melakukan Pencarian Siswa (NISN 10 Digit & Tanggal Lahir)
   - 7.3 Memantau Keaktifan, Sabuk, dan Riwayat Kehadiran Anak
8. [Panduan Mengatasi Kendala (Troubleshooting & FAQ)](#8-panduan-mengatasi-kendala-troubleshooting--faq)

---

## 1. TENTANG SILATTRACK

**SilatTrack** adalah sistem aplikasi web modern responsif (PWA-ready) yang dirancang khusus untuk digitalisasi manajemen kehadiran, kurikulum materi, dan portofolio keaktifan ekstrakurikuler pencak silat. 

### Fitur-Fitur Unggulan Sistem:
1. **Multi-School & Multi-Tenant Support**: Satu instalasi aplikasi dapat mengelola ekstrakurikuler pencak silat di berbagai sekolah mitra sekaligus, lengkap dengan data NPSN, alamat, dan pejabat kepala sekolah.
2. **AI Biometric Face Recognition**: Presensi cerdas menggunakan kamera smartphone/laptop yang dijalankan langsung di peramban pengguna (*on-device WebGL via face-api.js*) tanpa kuota API mahal.
3. **Audit Trail Anti-Fraud**: Setiap presensi wajah otomatis merekam snapshot foto aktual dan nilai metrik jarak kemiripan (*Euclidean distance*) untuk mencegah manipulasi.
4. **Dynamic Anti-Cheat QR Code**: Kode QR interaktif bertanda tangan kriptografi HMAC yang divalidasi ke rahasia sesi dan berganti berkala untuk mencegah screenshot titip absen.
5. **Standarisasi NISN 10 Digit**: Format identitas resmi siswa yang tervalidasi ketat sesuai standar Kementerian Pendidikan (Kemdikbudristek) untuk sinkronisasi nilai e-Rapor.
6. **Alur Persetujuan Kegiatan & Keanggotaan (*Approval Workflows*)**: Usulan jadwal latihan baru, sesi ad-hoc fleksibel, dan permohonan mutasi/hapus anggota dilindungi alur persetujuan Admin/Pembina sekolah.
7. **Portal Transparansi Wali Murid**: Orang tua murid dapat mengecek kehadiran anaknya secara instan menggunakan NISN dan tanggal lahir tanpa akun login.
8. **Kartu Tanda Anggota (KTA) Digital**: Kartu identitas pesilat interaktif siap unduh dan cetak lengkap dengan barcode/QR ID.
9. **Cetak Dokumen Resmi Ber-Kop Sekolah**: Format cetak laporan PDF/Print otomatis menyusun kop surat sekolah mitra, rekapitulasi presensi, dan kolom tanda tangan kepala sekolah serta pelatih.

---

## 2. PERSYARATAN SISTEM & CARA MENJALANKAN APLIKASI

### 2.1 Persyaratan Perangkat Keras & Perangkat Lunak
- **Server / Komputer Pengembang**:
  - Sistem Operasi: Windows 10/11, macOS, atau Linux (Ubuntu 20.04+).
  - Python: Versi **3.10** s/d **3.14** (terpasang modul `django`, `django-htmx`, `pillow`, `qrcode`, `reportlab`, `openpyxl`, `whitenoise`).
  - Basis Data: SQLite 3 (bawaan pengembangan) atau PostgreSQL 15+ (produksi).
- **Perangkat Klien (Pengguna)**:
  - Smartphone Android / iOS, Tablet, atau Laptop/PC.
  - Peramban Modern: Google Chrome, Apple Safari, Mozilla Firefox, atau Microsoft Edge.
  - Modul Kamera Fisik (untuk fitur pemindaian wajah & QR Code) dengan izin peramban (*Allow Camera Access*).

### 2.2 Cara Menjalankan Server Aplikasi (Local Development)
Buka terminal (PowerShell atau Bash) pada direktori proyek:
```bash
# Masuk ke folder proyek
cd "c:\absensi eskul pencak silat"

# Pastikan migrasi basis data sudah mutakhir
python manage.py migrate

# Jalankan server pengembangan
python manage.py runserver 127.0.0.1:8000
```
Server web akan aktif dan dapat diakses melalui browser pada alamat:  
👉 **`http://127.0.0.1:8000/`**

---

## 3. DAFTAR AKUN PENGGUNA BAWAAN (DEFAULT DEMO CREDENTIALS)

Untuk mempermudah demonstrasi dan pengujian sistem, telah disediakan akun contoh untuk setiap peran:

| Peran Pengguna | Username | Password | Deskripsi / Nama Pejabat |
| :--- | :--- | :--- | :--- |
| **Super Admin / Pembina** | `admin` | `admin123` | Pak Hendra Kurniawan, S.Pd (Pembina Eskul Sekolah) |
| **Pelatih / Coach** | `pelatih1` | `pelatih123` | Joko Pratama, S.Or (Pelatih Utama IPSI) |
| **Anggota / Pesilat 1** | `pesilat1` | `pesilat123` | Ahmad Rayhan (NISN: `0081122331`, Sabuk Kuning, X PPLG 1) |
| **Anggota / Pesilat 2** | `pesilat2` | `pesilat123` | Siti Nurhaliza (NISN: `0081122332`, Sabuk Hijau, X PPLG 2) |
| **Anggota / Pesilat 3** | `pesilat3` | `pesilat123` | Budi Santoso (NISN: `0081122333`, Sabuk Putih, XI TJKT 1) |
| **Portal Wali Murid** | *(Tanpa Login)* | *(Tanpa Login)* | Akses langsung di `/members/transparansi-wali/` menggunakan NISN & Tanggal Lahir |

---

## 4. PANDUAN PENGGUNA: ADMINISTRATOR / PEMBINA ESKUL

### 4.1 Login & Dashboard Admin
1. Buka halaman login di `http://127.0.0.1:8000/auth/login/`.
2. Masukkan username `admin` dan password `admin123`.
3. Setelah berhasil masuk, Anda akan diarahkan ke **Dashboard Utama Pembina/Admin**.
4. Halaman ini menyajikan:
   - Total anggota aktif, total pelatih, dan total sesi latihan yang diselenggarakan.
   - Grafik persentase tingkat kehadiran bulanan.
   - Kotak notifikasi persetujuan usulan jadwal/sesi dan permohonan hapus pesilat.

### 4.2 Manajemen Multi-Sekolah & Tanda Tangan Resmi
1. Masuk ke panel administrasi data master sekolah (`/admin/core/sekolah/` atau antarmuka master institusi).
2. Anda dapat menambahkan sekolah mitra baru dengan mengisi:
   - **Nama Sekolah**: Misal *SMKN 1 Rongga*, *SMAN 1 Bandung*.
   - **NPSN**: Nomor Pokok Sekolah Nasional resmi.
   - **Alamat Sekolah**: Digunakan pada kop surat laporan resmi.
   - **Nama Kepala Sekolah**: Pejabat penandatangan laporan (e.g. `Drs. H. Mulyadi, M.M`).
   - **NIP Kepala Sekolah**: Nomor Induk Pegawai kepala sekolah (e.g. `19720412 199802 1 003`).
   - **Jabatan Kepala Sekolah**: Format sebutan resmi (e.g. `Kepala Sekolah`).
3. Tekan **Simpan**. Data ini secara otomatis akan menjadi acuan kop surat dan blok tanda tangan cetak dokumen dinas.

### 4.3 Manajemen Akun Pelatih & Pesilat (Validasi NISN 10 Digit)
1. Pilih menu **Anggota** atau **Kelola Pengguna** di sidebar navigasi.
2. Untuk mendaftarkan pesilat baru:
   - Masukkan Username, Nama Lengkap, Email, dan Password awal.
   - Pilih **Sekolah** dari daftar sekolah mitra yang terdaftar.
   - Masukkan **NISN**: Wajib tepat **10 Digit Angka** (misal: `0081122331`). Jika kurang atau lebih dari 10 digit, sistem akan menampilkan validasi penolakan.
   - Tentukan Kelas (misal: `X PPLG 1`), Jenis Kelamin, Tanggal Lahir, Sabuk Awal, dan Kontak Orang Tua.
3. Tekan tombol **Simpan Anggota**.

### 4.4 Persetujuan Usulan Jadwal & Sesi Fleksibel
1. Jika pelatih mengusulkan sesi latihan baru di luar jam reguler atau mengajukan jadwal baru, statusnya akan tercatat **MENUNGGU**.
2. Buka detail sesi atau menu daftar persetujuan:
   - Tinjau usulan nama kegiatan, materi yang direncanakan, jam, dan lokasi latihan.
   - Berikan arahan pada kolom **Catatan Persetujuan Admin**.
   - Klik tombol hijau **Setujui Kegiatan** untuk mengesahkan, atau tombol merah **Tolak** jika jadwal bertabrakan dengan agenda sekolah.
3. Sesi yang telah berstatus **DISETUJUI** dapat langsung dibuka oleh pelatih untuk presensi siswa.

### 4.5 Persetujuan Permohonan Hapus Anggota
1. Pelatih di lapangan tidak dapat langsung menghapus siswa untuk mencegah penghapusan data bersejarah atau sengketa nilai.
2. Pelatih akan mengirimkan **Pengajuan Hapus Anggota** disertai alasan (misal: mutasi pindah sekolah, lulus, atau mengundurkan diri).
3. Admin meninjau permohonan pada daftar permohonan mutasi:
   - Baca alasan pengajuan pelatih.
   - Tulis catatan admin jika diperlukan.
   - Klik **Setujui Hapus** untuk mengeksekusi penghapusan/nonaktifkan anggota, atau **Tolak Pengajuan** untuk membatalkannya.

### 4.6 Rekapitulasi & Cetak Laporan Presensi Resmi (Kop Sekolah & Perguruan Ganda)
1. Masuk ke menu **Laporan Presensi** (`/attendance/reports/`).
2. Pilih filter yang diinginkan:
   - Periode latihan (Laporan Bulanan atau Laporan Tahunan).
   - Filter **Sekolah Mitra**: Pilih sekolah tertentu (misal: *SMKN 1 Rongga*).
   - Penandatangan laporan (Pembina, Pelatih, dan Kepala Sekolah).
3. Klik tombol **Terapkan Filter**.
4. Untuk mengunduh data mentah, klik tombol hijau **Ekspor Excel (.xlsx)**.
5. Untuk mencetak dokumen fisik resmi:
   - Klik tombol merah **Cetak Laporan Resmi** (`/attendance/reports/print/`).
   - Sistem akan membuka halaman cetak berstandar dokumen dinas yang otomatis menyusun:
     - **Logo Sekolah Mitra** di sisi kiri atas kop surat.
     - **Teks Kop Resmi** Pemerintah Daerah, Dinas Pendidikan, nama sekolah, dan alamat lengkap.
     - **Logo Perguruan Pencak Silat** di sisi kanan atas kop surat.
     - Judul rekapitulasi, periode latihan, grafik analitik kehadiran, dan tabel presensi lengkap.
     - Lembar 3 blok tanda tangan: Pembina Eskul, Pelatih Utama, dan Kepala Sekolah (lengkap dengan NIP).
6. **Kustomisasi & Input Manual Logo Laporan**:
   - Jika ingin mengubah logo sekolah atau logo perguruan pada lembar cetak secara langsung, klik tombol **"Atur Logo Kop Surat"** di bilah atas.
   - Anda dapat:
     - Menggunakan logo yang tersimpan di sistem (otomatis sesuai filter sekolah).
     - Mengunggah berkas logo baru (*file upload* JPG/PNG/WebP/SVG dari perangkat).
     - Menempelkan tautan (*URL*) gambar logo secara langsung.
   - Perubahan langsung di-*render* secara *real-time* ke lembar cetak A4.
   - Anda juga dapat mencentang opsi *"Simpan berkas logo ini ke database"* agar menjadi logo permanen sekolah/perguruan.
   - Tekan tombol **Cetak Dokumen / Simpan PDF** (`window.print()`).

### 4.7 Manajemen Identitas Perguruan & Kustomisasi Logo Aplikasi & Sekolah
1. Masuk ke menu **Logo Perguruan** di bilah navigasi atas (`/core/perguruan/`).
2. **Mengatur Identitas & Logo Aplikasi (Perguruan Silat)**:
   - Unggah **Logo Resmi Perguruan Silat** (format PNG, JPG, WebP, atau SVG).
   - Isi **Nama Perguruan**: Nama resmi padepokan silat.
   - Isi **Singkatan / Nama Brand Aplikasi**: Nama pendek (e.g. *SilatTrack*, *PPS-SMI*) yang tampil di navbar aplikasi.
   - Isi **Motto / Semboyan Perguruan**, **Alamat Padepokan**, dan **Kontak Sekretariat**.
   - Klik **Simpan Identitas Perguruan**.
   - Logo dan nama perguruan otomatis tampil di seluruh aplikasi: bilah navigasi atas, halaman login, sertifikat lisensi/prestasi, dan laporan resmi.
3. **Mengatur Logo Sekolah Mitra**:
   - Pada kolom sebelah kanan, terdapat daftar seluruh sekolah mitra yang dibina.
   - Klik tombol **Ubah Logo** pada sekolah yang ingin dikelola.
   - Pilih berkas logo sekolah resmi (e.g. logo SMKN 1 Rongga, SMAN 1 Bandung).
   - Perbarui juga nama dan NIP Kepala Sekolah pejabat penandatangan bila ada pergantian kepala sekolah.
   - Klik **Simpan Perubahan**. Logo sekolah ini akan langsung digunakan pada kop laporan dan sertifikat siswa sekolah tersebut.


---

## 5. PANDUAN PENGGUNA: PELATIH / COACH (INSTRUKTUR)

### 5.1 Login & Dashboard Pelatih
1. Masuk menggunakan akun pelatih (e.g. `pelatih1` / `pelatih123`).
2. Dashboard Pelatih menyajikan:
   - Ringkasan sesi aktif hari ini.
   - Daftar pesilat yang sedang dibina beserta tingkat sabuknya.
   - Tombol aksi cepat: **Buka Sesi Latihan**, **Scanner Kamera**, dan **QR Fullscreen**.

### 5.2 Membuat & Mengusulkan Sesi Latihan (Rutin & Fleksibel)
1. Klik tombol **Buat Sesi Latihan** (`/attendance/session/create/`).
2. Pilih dasar jadwal rutin yang tersedia, atau pilih opsi **Sesi Fleksibel / Ad-Hoc**:
   - Isi **Nama Lokasi Latihan**: Misal *Dojo Utama SMKN 1 Rongga*, *GOR Tenis Indoor*, dll.
   - Isi **Jam Mulai** dan **Jam Selesai** latihan.
   - Pilih **Tipe Sesi**: Latihan Reguler, TC Kejuaraan, Ujian Kenaikan Tingkat (UKT), atau Tes Fisik.
   - Tulis **Menu Materi Latihan**: Misal: *Pemanasan dinamis, Tangkisan atas & luar, Pola langkah ladam, Sambung rintis 3 ronde*.
3. Klik **Simpan & Buat Sesi**.

### 5.3 Membuka Sesi & Unggah Foto Dokumentasi Latihan
1. Buka detail sesi latihan yang telah disetujui.
2. Klik tombol hijau **Buka Sesi (Presensi Aktif)**. Status sesi akan berubah menjadi **DIBUKA**.
3. Di halaman detail sesi, pelatih dapat mengunggah dokumentasi:
   - Pilih file pada formulir **Foto Dokumentasi Latihan**.
   - Tulis keterangan foto (misal: *Latihan teknik bantingan pesilat pemula*).
   - Klik **Unggah Dokumentasi**. Foto ini akan tersimpan permanen sebagai arsip kegiatan.

### 5.4 Pelaksanaan Presensi di Lapangan (4 Metode)

Pelatih memiliki fleksibilitas penuh untuk menggunakan 4 mode presensi sesuai situasi di lapangan:

#### Mode A: AI Face Recognition Scanner (Audit Wajah & Jarak Euclidean)
1. Buka halaman scanner pelatih dengan mengklik tombol **Buka Pemindai Wajah AI** (`/attendance/session/<id>/scanner/`).
2. Izinkan akses kamera peramban (*Allow Camera*).
3. Minta pesilat berdiri di hadapan kamera dalam jarak $0{,}5 - 1$ meter:
   - Reticle pemindai akan mendeteksi kontur wajah (lingkaran kuning).
   - Sistem menahan kestabilan wajah selama 1-2 detik.
   - Jika wajah cocok dengan data acuan (reticle berubah hijau), sistem otomatis mengirimkan data verifikasi ke server.
   - Muncul notifikasi audio/visual: *"Presensi Berhasil: Ahmad Rayhan (Hadir)"*.
   - **Audit Keamanan**: Server otomatis menyimpan foto snapshot kamera (`foto_face_scan`) dan nilai jarak Euclidean (`face_distance`) untuk diaudit sewaktu-waktu.

#### Mode B: Dynamic Rolling QR Code Fullscreen
1. Klik tombol **Tampilkan QR Code** (`/attendance/session/<id>/qr/fullscreen/`).
2. Tampilkan layar ini di proyektor aula atau di layar ponsel/tablet pelatih.
3. Pesilat memindai kode QR tersebut menggunakan kamera smartphone masing-masing melalui aplikasi SilatTrack.
4. Kode QR dilengkapi tanda tangan digital HMAC untuk mencegah kecurangan titip absen via tangkapan layar.

#### Mode C: Quick Toggle HTMX (Satu Sentuhan Tombol)
1. Pada tabel daftar pesilat di detail sesi, pelatih dapat langsung menyentuh tombol status pada baris nama siswa:
   - **H**: Hadir (Hijau)
   - **I**: Izin (Biru)
   - **S**: Sakit (Kuning)
   - **A**: Alpa (Merah)
2. Status presensi akan langsung terbarui secara instan (*zero page reload*) berkat teknologi HTMX, dan total counter hadir otomatis bertambah.

#### Mode D: Presensi Massal (Tandai Semua Hadir)
1. Jika seluruh anggota telah berbaris rapi dan hadir lengkap, pelatih dapat menekan tombol **Tandai Semua Hadir** (*Bulk Action*).
2. Sistem otomatis memperbarui seluruh pesilat menjadi **HADIR** dalam satu kali proses.

### 5.5 Validasi Surat Izin & Sakit Siswa
1. Siswa yang berhalangan hadir dapat mengajukan izin/sakit melalui aplikasi dengan melampirkan foto bukti surat.
2. Di halaman detail sesi atau daftar izin, pelatih dapat mengklik tombol **Tinjau Bukti Surat**.
3. Periksa foto surat dokter atau keterangan orang tua yang diunggah.
4. Klik tombol **Setujui (Approve)** atau **Tolak (Reject)**.

### 5.6 Manajemen Profil Pesilat, Registrasi Wajah & Cetak KTA Fisik
1. Buka menu **Daftar Anggota & Pelatih** (`/members/`).
2. **Cetak ID Card Lisensi Pelatih**:
   - Buka tab **Pelatih**, pada kartu profil pelatih klik tombol **ID Card Pelatih** (`/members/<id>/card/`).
   - Atau klik ikon badge di bilah atas aplikasi / tombol **Lihat ID Card Saya** di halaman profil.
   - Tampil ID Card resmi bergradien Crimson & Gold dengan nomor registrasi, tingkatan pendekar, spesialisasi, nomor SK lisensi, dan kode QR verifikasi resmi.
   - Tersedia dua sisi kartu (Depan & Belakang berisi Kode Etik Kepelatihan Pencak Silat).
   - Klik tombol **Cetak / Simpan PDF** untuk mencetak kartu fisik resmi.
3. **Pendaftaran Wajah Pertama Kali Pesilat (*Face Enrollment*)**:
   - Jika pesilat belum memiliki data wajah, buka profil anggota lalu klik tombol **Daftarkan Wajah Biometrik**.
   - Hadapkan wajah pesilat ke kamera hingga sistem mengekstraksi vektor 128 dimensi dan menyimpannya ke profil siswa.
4. **Wewenang Khusus Cetak Kartu Tanda Anggota (KTA) Fisik Pesilat**:
   - Klik tombol **Kartu Anggota (KTA)** (`/members/<id>/card/`).
   - Tampil kartu digital resmi pesilat dengan foto, NISN 10 digit, kelas, sabuk berwarna asli, kategori tanding, nama sekolah, QR Code verifikasi, dan Panca Prasetya Pendekar di sisi belakang.
   - **Hak Akses Cetak Fisik**: Sesuai kebijakan tata tertib eskul, tombol hijau **Cetak / Simpan PDF** hanya muncul untuk akun **Pelatih** dan **Admin/Pembina**. Hal ini bertujuan menjamin keaslian fisik kartu yang beredar dan mencegah siswa memalsukan kartu anggota secara mandiri.
   - Cetak pada kertas PVC card atau photo paper glossy tebal ($85{,}6\text{ mm} \times 54\text{ mm}$).

### 5.7 Mengajukan Mutasi / Hapus Anggota ke Admin
1. Jika seorang siswa mengundurkan diri atau pindah sekolah, buka profil pesilat tersebut.
2. Klik tombol merah **Ajukan Hapus / Mutasi**.
3. Tuliskan alasan lengkap pada formulir (misal: *Siswa pindah domisili ke luar kota mulai semester ganjil*).
4. Klik **Kirim Pengajuan ke Pembina/Admin**.
5. Permohonan akan masuk ke antrean persetujuan Admin tanpa menghapus riwayat kehadiran yang sudah ada.

### 5.8 Menutup Sesi Latihan
1. Setelah seluruh materi latihan silat selesai, klik tombol **Tutup Sesi Latihan**.
2. Status sesi berubah menjadi **SELESAI**.
3. Presensi mandiri siswa akan otomatis terkunci sehingga tidak ada lagi data presensi susulan yang dapat masuk secara liar.

### 5.9 Sertifikat Lisensi Kepelatihan Resmi & Sertifikat Prestasi Siswa
1. **Sertifikat Lisensi Pelatih**:
   - Buka menu profil atau direktori pelatih, lalu klik tombol **Sertifikat** (`/members/<id>/certificate/`).
   - Format: Standar A4 Landscape resmi ber-ornamen bingkai ganda emas klasik (*antique gold & crimson*).
   - Memuat: Nomor Sertifikat Lisensi resmi (`SRT/PLT-IPSI/2026/...`), Nomor Registrasi Pelatih, Tingkatan Pendekar, Spesialisasi bidang, Pengalaman masa pengabdian, QR Code otentikasi digital, serta tanda tangan Ketua Pembina dan Kepala Sekolah.
2. **Sertifikat Kompetensi & Prestasi Anggota (Pesilat)**:
   - Pelatih dapat membuka profil siswa atau direktori anggota dan mengklik tombol **Sertifikat**.
   - Memuat: NISN 10 digit, tingkatan sabuk terkini, persentase kehadiran latihan, predikat kedisiplinan (*Sangat Baik / Baik / Cukup*), serta tanda tangan Pelatih Utama dan Kepala Sekolah.
3. **Pencetakan Fisik**: Tekan tombol **Cetak Sertifikat A4** untuk mencetak langsung ke kertas tebal (Concorde/Linen 220–260 gsm) dalam format landscape.


---

## 6. PANDUAN PENGGUNA: ANGGOTA / SISWA PESILAT

### 6.1 Login & Dashboard Siswa
1. Buka alamat aplikasi di peramban smartphone: `http://127.0.0.1:8000/auth/login/`.
2. Masukkan username (misal: `pesilat1`) dan password (`pesilat123`).
3. Pada **Dashboard Pesilat**, siswa dapat melihat:
   - Status sesi latihan hari ini (apakah sedang DIBUKA oleh pelatih).
   - Persentase kehadiran pribadi dan lencana **Attendance Streak** (rekor hadir tanpa bolos).
   - Status sabuk saat ini dan syarat kelayakan Ujian Kenaikan Tingkat (UKT).

### 6.2 Registrasi Wajah Pertama Kali (*Face Enrollment*)
1. Saat pertama kali bergabung di eskul, masuk ke menu **Profil Saya**.
2. Klik tombol **Daftarkan Wajah Saya**.
3. Pastikan berada di tempat dengan pencahayaan yang cukup.
4. Arahkan kamera depan HP ke wajah Anda dan tahan selama 2 detik hingga muncul pesan *"Wajah berhasil diregistrasikan!"*. Data acuan ini akan digunakan untuk seluruh absensi berikutnya.

### 6.3 Presensi Wajah Mandiri & Pemindaian QR
1. Jika pelatih mengumumkan sesi telah dibuka:
   - Buka menu **Presensi Mandiri**.
   - Pilih metode **Pindai Wajah**: Hadapkan kamera ke wajah Anda. Ketika lingkaran berubah hijau, kehadiran Anda langsung tercatat otomatis.
   - Atau pilih metode **Scan QR Code**: Arahkan kamera HP ke layar proyektor pelatih untuk membaca kode QR.
2. Muncul konfirmasi kartu hadir hijau: *"Presensi Berhasil: HADIR"*.

### 6.4 Klaim Presensi Darurat Manual
1. Jika kamera HP rusak, lensa buram, atau izin kamera bermasalah:
   - Pilih menu **Presensi Darurat Manual**.
   - Pilih sesi latihan aktif hari ini.
   - Tulis alasan kendala teknis perangkat Anda.
   - Tekan **Kirim Klaim Kehadiran**. Pelatih di lapangan akan memverifikasi klaim kehadiran Anda secara manual.

### 6.5 Pengajuan Surat Izin & Sakit (Lampiran Foto)
1. Jika Anda berhalangan hadir karena sakit atau ada keperluan keluarga penting:
   - Klik menu **Ajukan Izin / Sakit** (`/attendance/permit/create/`).
   - Pilih jenis: **IZIN** atau **SAKIT**.
   - Tulis keterangan alasan (misal: *Demam tinggi, istirahat dokter 2 hari*).
   - Unggah foto surat dokter atau surat keterangan bertanda tangan orang tua.
   - Klik **Kirim Permohonan Izin**.
2. Status akan tercatat **MENUNGGU VERIFIKASI** hingga dikonfirmasi oleh pelatih.

### 6.6 Memantau Syarat Ujian Sabuk (UKT) & Attendance Streak
1. Buka tab **Riwayat & Sabuk** di navigasi bawah.
2. Anda dapat melihat:
   - Riwayat ujian sabuk yang pernah diikuti beserta predikat kelulusannya.
   - Indikator kelayakan UKT: Jika persentase kehadiran Anda telah mencapai batas minimal sabuk (e.g. $\ge 75\%$), akan tampil penanda hijau:  
     🟢 **"Selamat! Anda Memenuhi Syarat Mengikuti Ujian Kenaikan Tingkat"**.
   - Lencana **Streak**: Menghitung berapa minggu berturut-turut Anda hadir disiplin tanpa alpa.

### 6.7 Melihat Kartu Tanda Anggota (KTA) Digital (Kebijakan Akses Pratinjau)
1. Buka menu **Profil** dan klik tombol **ID Card** (`/members/my-card/`).
2. Tampil KTA digital resmi beresolusi tajam dengan warna tema Silat Crimson dan ornamen emas.
3. **Kebijakan Hak Akses Siswa**:
   - Anggota berhak **melihat (preview)** data identitas, foto, NISN, tingkat sabuk, dan kode QR resmi miliknya secara transparan.
   - Anggota **tidak diberikan akses untuk mencetak (*no print access*)** kartu fisik secara mandiri demi menjaga standar bahan (PVC) dan keabsahan legalitas organisasi.
   - Pada halaman KTA siswa, tombol cetak digantikan dengan penanda:  
     👁️ **"Mode Pratinjau (Cetak Fisik Dikelola Pelatih/Admin)"**.
   - Jika Anda membutuhkan cetak fisik kartu KTA untuk turnamen atau administrasi sekolah, silakan mengajukannya langsung ke Pelatih Silat atau Pembina Eskul.

### 6.8 Mengakses & Mencetak Sertifikat Kompetensi Ekstrakurikuler Resmi
1. Buka menu **Profil** dan klik tombol **Sertifikat Resmi** (`/members/my-certificate/`), atau klik tombol **Lihat Sertifikat** dari halaman KTA Anda.
2. Sistem akan menyajikan lembar **Sertifikat Kompetensi & Keikutsertaan A4 Landscape** resmi dengan desain elegan:
   - Identitas nama pesilat, nomor NISN 10 digit, dan kelas sekolah.
   - Tingkatan sabuk pencak silat yang disandang saat ini.
   - Rekam jejak persentase kehadiran latihan dan predikat kelulusan (*Sangat Baik / Baik / Cukup*).
   - Kode QR otentikasi digital yang dapat dipindai untuk membuktikan keaslian sertifikat secara langsung ke basis data SilatTrack.
   - Kolom legalitas tanda tangan Pelatih Utama dan Kepala Sekolah.
3. **Mencetak Sertifikat**: Anggota dapat menekan tombol **Cetak Sertifikat A4** untuk mencetak portofolio prestasi atau menyimpannya sebagai berkas PDF untuk lampiran e-Rapor atau pendaftaran jalur prestasi (PPDB).


---

## 7. PANDUAN PENGGUNA: ORANG TUA / WALI MURID (PORTAL TRANSPARANSI)

### 7.1 Mengakses Portal Wali Murid Tanpa Login
Orang tua atau wali murid tidak perlu mengingat username dan kata sandi baru untuk mengecek kegiatan anaknya:
1. Buka peramban smartphone/komputer dan kunjungi:  
   👉 **`http://127.0.0.1:8000/members/transparansi-wali/`**  
   *(Atau klik tombol bergambar orang tua "Portal Wali" di bilah atas aplikasi).*

### 7.2 Melakukan Pencarian Siswa (NISN 10 Digit & Tanggal Lahir)
1. Pada form pencarian yang tampil:
   - Masukkan **10 Digit NISN Anak** (misal: `0081122331`).
   - Masukkan **Tanggal Lahir Anak** sesuai data resmi sekolah.
2. Klik tombol **Cari Data Pesilat**.

### 7.3 Memantau Keaktifan, Sabuk, dan Riwayat Kehadiran Anak
Setelah verifikasi data cocok, sistem menampilkan dashboard transparansi anak:
- **Identitas Pesilat**: Nama lengkap anak, asal sekolah mitra, kelas, dan foto profil.
- **Tingkatan Sabuk**: Sabuk yang disandang saat ini beserta kurikulum dasar yang sedang dipelajari.
- **Statistik Kehadiran**: Persentase kehadiran anak dalam kegiatan latihan eskul pencak silat.
- **Rekor Kehadiran (*Streak*)**: Indikator kedisiplinan anak berlatih tanpa absen.
- **Tabel Riwayat Latihan Terkini**: Daftar tanggal sesi latihan, materi yang dipelajari, jam hadir, dan status kehadiran anak (Hadir, Izin, Sakit, Alpa).

---

## 8. PANDUAN MENGATASI KENDALA (TROUBLESHOOTING & FAQ)

### T1: Kamera tidak menyala atau muncul pesan "Camera Permission Denied"?
- **Penyebab**: Peramban memblokir izin akses perangkat kamera/webcam.
- **Solusi**:
  1. Klik ikon gembok/setelan di sebelah kiri bilah alamat URL peramban (*Address Bar*).
  2. Ubah setelan **Kamera** menjadi **Izinkan (*Allow*)**.
  3. Muat ulang halaman (*Refresh / F5*).

### T2: Wajah tidak terdeteksi saat pemindaian biometrik?
- **Penyebab**: Pencahayaan terlalu gelap, wajah tertutup masker/topi, atau sudut kamera terlalu miring.
- **Solusi**:
  1. Berdirilah di tempat dengan pencahayaan terang menghadap ke wajah.
  2. Buka kacamata hitam, masker, atau penutup wajah.
  3. Posisikan wajah tepat di dalam reticle oval panduan pemindai pada jarak $50\text{ cm} - 1\text{ meter}$.

### T3: Sistem menolak penyimpanan NISN dengan pesan "NISN harus tepat 10 digit angka"?
- **Penyebab**: NISN yang diketik kurang dari 10 digit, lebih dari 10 digit, atau mengandung karakter spasi/huruf.
- **Solusi**:
  1. Masukkan tepat 10 digit angka resmi Kemdikbudristek (misal: `0081122331`).
  2. Pastikan tidak ada spasi di awal atau akhir angka.

### T4: Kode QR tidak bisa dipindai atau muncul pesan "Kode QR tidak sah / kedaluwarsa"?
- **Penyebab**: Sesi latihan sudah ditutup oleh pelatih, atau pesilat mencoba memindai tangkapan layar (screenshot) lama kiriman teman.
- **Solusi**:
  1. Pastikan status sesi latihan masih **DIBUKA** oleh pelatih.
  2. Pindai kode QR secara langsung dari layar perangkat pelatih di lokasi latihan.

### T5: Bagaimana jika pelatih keliru menekan status presensi siswa?
- **Solusi**:
  1. Pelatih cukup mengklik ulang tombol status yang benar (misal dari **S** ke **H**) pada baris pesilat di detail sesi latihan.
  2. Perubahan akan langsung diperbarui secara instan oleh sistem.

### T6: Bagaimana cara mencetak laporan dengan kop sekolah tertentu?
- **Solusi**:
  1. Masuk ke menu **Laporan Presensi** (`/attendance/reports/`).
  2. Pilih sekolah yang diinginkan pada dropdown filter **Sekolah Mitra**.
  3. Klik **Terapkan Filter**, lalu tekan tombol **Cetak Laporan Resmi**.
  4. Laporan otomatis memuat kop surat resmi sekolah serta tanda tangan kepala sekolah yang bersangkutan.

---
*Dokumen Buku Panduan SilatTrack ini disusun sebagai pedoman operasional resmi. Untuk bantuan teknis lebih lanjut, hubungi tim pengembang atau guru pembina ekstrakurikuler sekolah.*
