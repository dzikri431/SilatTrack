# Panduan Hosting & Online SilatTrack

Proyek **SilatTrack** telah disiapkan agar siap diakses secara online, baik untuk **uji coba langsung di HP via HTTPS** maupun **hosting permanen di cloud (Render / Railway / PythonAnywhere)**.

---

## 1. Akses Online Instan (Sedang Berjalan Sekarang)

Proyek ini telah berhasil di-online-kan melalui secure tunnel HTTPS:
* **Public URL:** [https://tired-ghosts-take.loca.lt](https://tired-ghosts-take.loca.lt)
* **Tunnel Password / Friendly Click:** Jika diminta memasukkan *Tunnel Password* pada tampilan pertama, masukkan IP:
  ```text
  180.254.86.15
  ```
* **Kelebihan:** 
  - Menggunakan protokol **HTTPS resmi** sehingga kamera HP (Barcode & AI Face Scan) serta GPS Geolocation browser aktif tanpa diblokir.
  - Dapat dibuka langsung dari HP siswa, pelatih, maupun admin.

---

## 2. Fitur Geofence & Navigasi SMKN 1 Rongga

* **Titik Acuan Lokasi:** SMKN 1 Rongga
* **Koordinat:** `-7.0011, 107.2721`
* **Radius Presensi:** Maksimal 100 meter.
* **Auto-Detect GPS:** Halaman presensi otomatis membaca koordinat GPS perangkat begitu halaman dibuka.
* **Live GPS Tracking:** Memantau pergerakan siswa secara real-time. Begitu masuk dalam radius 100m, sistem otomatis mengaktifkan pemindai presensi.
* **Petunjuk Arah Google Maps:** Tersedia tombol langsung untuk membuka navigasi rute Google Maps ke SMKN 1 Rongga:
  `https://www.google.com/maps/dir/?api=1&destination=-7.0011,107.2721`

---

## 3. Panduan Deploy Permanen 24/7 Gratis (Cloud Hosting)

File konfigurasi produksi telah disiapkan:
- `Procfile` (`web: gunicorn silattrack.wsgi --log-file -`)
- `requirements.txt` (termasuk `gunicorn`, `whitenoise`, `dj-database-url`)
- `silattrack/settings.py` (`WhiteNoiseMiddleware`, `CSRF_TRUSTED_ORIGINS`, `ALLOWED_HOSTS = ['*']`)

### Opsi A: Deploy di Render (Rekomendasi Gratis)
1. Buat akun di [Render.com](https://render.com/).
2. Push repositori proyek ini ke GitHub Anda.
3. Klik **New +** -> **Web Service**.
4. Hubungkan repositori GitHub Anda.
5. Konfigurasi:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn silattrack.wsgi:application`
6. Klik **Create Web Service**. Website akan aktif dengan domain `https://nama-projek.onrender.com`.

### Opsi B: Deploy di Railway.app
1. Buka [Railway.app](https://railway.app/).
2. Klik **New Project** -> **Deploy from GitHub repo**.
3. Railway akan otomatis mendeteksi `Procfile` dan `requirements.txt`.
4. Tambahkan service SQLite volume atau PostgreSQL database.
5. Klik **Generate Domain** untuk mendapatkan URL publik.

### Opsi C: PythonAnywhere
1. Buka [PythonAnywhere.com](https://www.pythonanywhere.com/).
2. Upload file proyek atau `git clone`.
3. Buat Virtualenv, install `requirements.txt`.
4. Di tab **Web**, arahkan ke WSGI `silattrack/wsgi.py`.
