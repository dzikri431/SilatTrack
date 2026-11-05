# SilatTrack: Sistem Absensi Eskul Pencak Silat

Aplikasi manajemen dan absensi ekstrakurikuler Pencak Silat modern berbasis **DATH Stack** (Django + Alpine.js + Tailwind CSS + HTMX) dengan arsitektur **HTML-over-the-Wire / Modern Monolith** dan sistem desain **Google Material Design 3 (M3)**.

---

## 🥋 Fitur Unggulan

1. **Dynamic Rolling QR Code (Anti Titip Absen)**:
   - QR Code dienkripsi menggunakan HMAC-SHA256 dan berotasi otomatis setiap 15 detik menggunakan HTMX polling.
   - Screenshot / foto QR dari jauh tidak bisa digunakan oleh siswa yang tidak hadir di lokasi latihan.
2. **In-Browser Camera Scanner**:
   - Pesilat dapat langsung memindai QR code pelatih langsung dari browser smartphone mereka menggunakan HTML5-QRCode dan Alpine.js tanpa perlu mengunduh aplikasi di App Store/Play Store.
3. **Pelatih Attendance Cockpit**:
   - Pelatih dapat mengabsen atau mengoreksi status puluhan murid secara instan (*Hadir, Izin, Sakit, Alpa*) dengan HTMX zero-reload inline swapping.
   - Terdapat mode **Layar Penuh (Projector / Smart TV)** untuk ditampilkan di aula/dojo tempat latihan.
4. **Kualifikasi Ujian Kenaikan Sabuk (UKT)**:
   - Penghitungan persentase kehadiran otomatis yang diselaraskan dengan prasyarat minimal tingkatan sabuk masing-masing pesilat.
5. **Ekspor Rekap Laporan Excel**:
   - Pembina dan pelatih dapat mengunduh rekapan presensi per sesi atau berkala langsung ke format spreadsheet `.xlsx` siap cetak.
6. **Pendaftaran Mandiri Anggota Baru (Self-Registration)**:
   - Calon atau siswa pesilat baru dapat membuat akun sendiri melalui formulir pendaftaran (`/auth/register/`).
   - Data otomatis terhubung ke sistem admin, direktori pesilat, dan dapat langsung diabsen oleh pelatih pada sesi latihan aktif.
7. **Manajemen Profil & Keamanan Pengguna**:
   - Setiap pengguna (Admin, Pelatih, maupun Pesilat) dapat mengubah data diri mereka (`/auth/profile/`): foto profil (avatar), nama lengkap, username, email, nomor handphone/WhatsApp, dan ganti kata sandi dengan aman.
   - Pesilat dapat melihat penjelasan kurikulum materi tingkatan sabuk mereka, ambang batas UKT, dan riwayat ujian sabuk.
8. **Desain Google Material Design 3 (M3)**:
   - Antarmuka responsif ramah mobile dengan palet warna pendekar (*Crimson Maroon & Golden Brass*), pill navigation, elevated cards, and state layers.

---

## 🛠️ Tech Stack (DATH Stack)

- **Backend**: Python 3.14 + Django 5.2 (Modern Monolith, Custom User Model, ORM)
- **Frontend / Interaction**: HTMX 2.x (HTML-over-the-Wire, Partial Swaps, Out-Of-Band Updates)
- **Client Micro-Interactions**: Alpine.js 3.x (State management, camera scanner handler, timer)
- **Styling**: Tailwind CSS + Google Material Design 3 Design Tokens
- **Scanner**: HTML5-QRCode Scanner Library
- **Exporting**: openpyxl

---

## 🚀 Cara Menjalankan Aplikasi

### 1. Jalankan Server Django
Buka terminal / PowerShell di direktori proyek dan jalankan:
```bash
python manage.py runserver
```

Buka browser di: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 👥 Akun Demo untuk Uji Coba (Tersedia Tombol 1-Click di Halaman Login)

| Role | Username | Password | Keterangan |
| :--- | :--- | :--- | :--- |
| **Pembina / Superadmin** | `admin` | `admin123` | Akses penuh dashboard analitik & Django Admin |
| **Pelatih Silat** | `pelatih1` | `pelatih123` | Akses buka sesi, cockpit presensi, rolling QR |
| **Pesilat 1** | `pesilat1` | `pesilat123` | Siswa Sabuk Kuning (Scanner presensi & UKT progress) |
| **Pesilat 2** | `pesilat2` | `pesilat123` | Siswa Sabuk Hijau |
| **Pesilat 3** | `pesilat3` | `pesilat123` | Siswa Sabuk Putih |

*(Pada halaman login, Anda juga dapat langsung mengklik tombol kartu akun demo untuk login instan).*

---

## 📚 Dokumentasi Rekayasa Perangkat Lunak

- 📄 [Product Requirements Document (PRD)](file:///C:/absensi%20eskul%20pencak%20silat/docs/PRD.md)
- 📊 [Entity Relationship Diagram & Data Dictionary (ERD)](file:///C:/absensi%20eskul%20pencak%20silat/docs/ERD.md)
- 🏛️ [Arsitektur Teknis DATH Stack & Material Design 3](file:///C:/absensi%20eskul%20pencak%20silat/docs/ARCHITECTURE.md)

---

## 🧪 Menjalankan Pengujian (Automated Tests)

Untuk memastikan seluruh fungsi presensi, rolling token HMAC, dan ekspor excel bekerja dengan baik:
```bash
python manage.py test
```
Semua 12 unit test telah terverifikasi lulus 100% (**OK**).
