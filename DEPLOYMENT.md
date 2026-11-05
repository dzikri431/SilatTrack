# 🚀 Panduan Lengkap Hosting & Deployment SilatTrack

Aplikasi **SilatTrack** (Sistem Absensi Eskul Pencak Silat Berbasis Multi-Sekolah) sudah disiapkan sepenuhnya untuk **Production Ready**. Seluruh konfigurasi server web (`gunicorn`), static file serving (`whitenoise`), database fallback (`dj-database-url`), serta proteksi `CSRF_TRUSTED_ORIGINS` telah terpasang dan teruji 100%.

---

## 📋 Fitur Terbaru yang Sudah Terintegrasi
1. **Multi-Sekolah & Dojo Bebas**:
   - Mendukung pencatatan dan filter data pesilat antar sekolah berbeda (SMKN 1 Rongga, SMAN 1 Rongga, SMPN 1 Rongga, dll).
   - Penentuan lokasi latihan fleksibel: Admin dapat langsung membuka sesi, sedangkan Pelatih dapat mengajukan lokasi & waktu latihan baru yang membutuhkan persetujuan Admin (`status_persetujuan: MENUNGGU` -> `DISETUJUI`).
2. **Filter & Monitoring Siswa Sesuai Sekolah**:
   - Tab filter sekolah di direktori anggota, cockpit presensi, dan rekapitulasi laporan agar data siswa tidak bercampur.
3. **Pengesahan & Tanda Tangan Laporan Resmi**:
   - Penandatangan Pembina & Pelatih otomatis dari akun sistem.
   - Penandatangan Kepala Sekolah (Nama, NIP, Jabatan) dapat diedit langsung, disesuaikan per sekolah, dan disimpan permanen sebagai default sekolah tersebut (`save_kepala_sekolah`).
   - Pratinjau cetak A4 memiliki fitur *quick-edit* tanda tangan langsung di browser sebelum dicetak/disimpan ke PDF.
4. **Validasi NISN Kemdikbudristek**:
   - Format NISN wajib tepat 10 digit numerik resmi Dapodik (`^\d{10}$`) untuk integrasi nilai raport sekolah.
5. **Waktu, Tanggal & Jadwal Fleksibel**:
   - Bebas memilih tanggal dan rentang jam latihan saat membuka sesi tanpa menghilangkan jadwal rutin mingguan yang ada di sistem.

---

## 🛠️ Langkah 1: Push Proyek ke GitHub Anda

Git lokal pada folder proyek ini sudah diinisialisasi dan di-commit (`main` branch). Anda hanya perlu menghubungkannya ke akun GitHub:

1. Buka [GitHub](https://github.com/) dan buat repositori baru (misalnya dengan nama `silattrack` atau `absensi-eskul-silat`). Biarkan kosong (jangan centang README/.gitignore karena sudah ada di lokal).
2. Salin URL repositori GitHub Anda (contoh: `https://github.com/USERNAME/silattrack.git`).
3. Buka PowerShell / Terminal di folder proyek ini (`c:\absensi eskul pencak silat`), lalu jalankan:

```powershell
git remote add origin https://github.com/USERNAME/silattrack.git
git push -u origin main
```

*(Ganti `USERNAME/silattrack.git` dengan link repositori GitHub Anda).*

---

## 🌐 Langkah 2: Pilihan Platform Hosting (Gratis & Siap Pakai)

### 🥇 OPSI 1: Render.com (Paling Direkomendasikan - Gratis & Otomatis SSL HTTPS)
Kelebihan: Mendukung HTTPS gratis resmi (wajib agar kamera HP untuk Barcode Scan & AI Face Recognition serta GPS Geolocation browser aktif).

**Langkah-langkah:**
1. Daftar atau masuk ke [Render.com](https://render.com/) menggunakan akun GitHub Anda.
2. Di Dashboard Render, klik tombol **New +** -> pilih **Web Service**.
3. Pilih opsi **Build and deploy from a Git repository**, lalu klik **Connect** pada repositori `silattrack` Anda.
4. Isi form konfigurasi sebagai berikut:
   - **Name**: `silattrack` *(atau nama unik yang Anda inginkan)*
   - **Region**: `Singapore (Southeast Asia)` *(paling cepat untuk akses di Indonesia)*
   - **Branch**: `main`
   - **Root Directory**: *(kosongkan)*
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**:
     ```bash
     gunicorn silattrack.wsgi:application
     ```
   - **Instance Type**: Pilih **Free**.
5. Buka bagian **Advanced** -> **Add Environment Variable**:
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(isi sembarang string acak yang panjang)*
   - `ALLOWED_HOSTS`: `*`
6. Klik **Create Web Service**.
7. Tunggu build selesai sekitar 1-2 menit. Begitu selesai, website Anda akan langsung aktif dengan link:
   👉 `https://silattrack.onrender.com`

---

### 🥈 OPSI 2: PythonAnywhere (Alternatif Sangat Cocok untuk SQLite)
Kelebihan: Menjalankan file SQLite (`db.sqlite3`) secara persisten tanpa perlu konfigurasi database cloud terpisah.

**Langkah-langkah:**
1. Buka [PythonAnywhere.com](https://www.pythonanywhere.com/) dan buat akun gratis (username Anda akan jadi subdomain: `username.pythonanywhere.com`).
2. Buka tab **Consoles** -> jalankan **Bash Console**:
   ```bash
   git clone https://github.com/USERNAME/silattrack.git
   cd silattrack
   mkvirtualenv --python=/usr/bin/python3.10 silattrack-venv
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
3. Buka tab **Web** di dashboard PythonAnywhere:
   - Klik **Add a new web app** -> pilih **Manual configuration** -> Python 3.10.
   - Di bagian **Virtualenv**, masukkan path virtualenv: `/home/USERNAME/.virtualenvs/silattrack-venv`.
   - Di bagian **Code**, atur:
     - Source code: `/home/USERNAME/silattrack`
     - Working directory: `/home/USERNAME/silattrack`
   - Buka file **WSGI configuration file** (klik link wsgi file), hapus isinya dan ganti dengan:
     ```python
     import os
     import sys

     path = '/home/USERNAME/silattrack'
     if path not in sys.path:
         sys.path.append(path)

     os.environ['DJANGO_SETTINGS_MODULE'] = 'silattrack.settings'

     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
4. Di bagian **Static files**:
   - URL: `/static/` -> Directory: `/home/USERNAME/silattrack/staticfiles`
   - URL: `/media/` -> Directory: `/home/USERNAME/silattrack/media`
5. Klik tombol hijau **Reload <username>.pythonanywhere.com**.
6. Aplikasi aktif di `https://<username>.pythonanywhere.com`.

---

### 🥉 OPSI 3: Akses Online Instan dari Laptop (Untuk Demo & Presentasi Cepat)
Jika Anda ingin segera mendemokan aplikasi ke kepala sekolah, pelatih, atau murid di lapangan hari ini tanpa perlu setup cloud:

1. Jalankan server Django lokal:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```
2. Buka terminal baru dan gunakan tunnel HTTPS gratis:
   - Menggunakan **Cloudflare Tunnel (Quick Tunnel)**:
     ```powershell
     cloudflared tunnel --url http://localhost:8000
     ```
   - Atau menggunakan **Localtunnel**:
     ```powershell
     npx localtunnel --port 8000
     ```
3. Anda akan mendapatkan URL publik berprotokol HTTPS resmi (misal: `https://xxxx.trycloudflare.com`).
4. Link ini bisa langsung dibuka di HP siapa saja dan semua fitur sensor (Kamera Scanner Barcode, AI Face Snapshot Wajah, dan GPS Geofence) langsung aktif tanpa peringatan keamanan!
