# Entity Relationship Diagram (ERD) & Data Dictionary
## SilatTrack: Sistem Absensi Eskul Pencak Silat

- **Dokumen**: Spesifikasi Model Data Relasional & Django ORM
- **Database Engine**: PostgreSQL / SQLite 3 (Production-ready Django Models)
- **Versi**: 1.3.0 (Updated: November 2026)
- **Status**: Complete, Verified & Normalized (3NF)

---

## 1. Visual Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    SEKOLAH ||--o{ ANGGOTA_PROFILE : "asal sekolah pesilat"

    USER ||--o| ANGGOTA_PROFILE : "extends as pesilat"
    USER ||--o| PELATIH_PROFILE : "extends as coach"
    USER ||--o{ SESI_LATIHAN : "dilatih oleh (pelatih)"
    USER ||--o{ JADWAL_LATIHAN : "diusulkan oleh (pelatih)"
    USER ||--o{ JADWAL_LATIHAN : "disetujui oleh (admin)"
    USER ||--o{ PRESENSI : "diverifikasi oleh"}
    USER ||--o{ PENGAJUAN_HAPUS_ANGGOTA : "diajukan oleh (pelatih)"
    USER ||--o{ PENGAJUAN_HAPUS_ANGGOTA : "disetujui oleh (admin)"

    TINGKAT_SABUK ||--o{ ANGGOTA_PROFILE : "sabuk saat ini"
    TINGKAT_SABUK ||--o{ RIWAYAT_SABUK : "sabuk lama"
    TINGKAT_SABUK ||--o{ RIWAYAT_SABUK : "sabuk baru"

    KATEGORI_TANDING ||--o{ ANGGOTA_PROFILE : "kategori fokus peminatan"

    JADWAL_LATIHAN ||--o{ SESI_LATIHAN : "dasar jadwal rutin"

    SESI_LATIHAN ||--o{ PRESENSI : "memiliki daftar presensi"

    ANGGOTA_PROFILE ||--o{ PRESENSI : "riwayat presensi pesilat"
    ANGGOTA_PROFILE ||--o{ RIWAYAT_SABUK : "portofolio kenaikan tingkat"
    ANGGOTA_PROFILE ||--o{ PENGAJUAN_HAPUS_ANGGOTA : "target pesilat yang diajukan"

    PELATIH_PROFILE ||--o{ RIWAYAT_SABUK : "diuji oleh pelatih"

    PERGURUAN {
        int id PK
        string nama_perguruan "Nama resmi padepokan silat"
        string singkatan "Brand aplikasi di navbar"
        string logo_perguruan "Lambang perguruan silat"
        string semboyan "Motto / filosofi perguruan"
        text alamat_pusat
        string kontak
        datetime created_at
        datetime updated_at
    }

    SEKOLAH {
        int id PK
        string nama_sekolah UK
        string npsn
        text alamat
        string logo_sekolah "Lambang resmi sekolah"
        string nama_kepala_sekolah "Penandatangan laporan resmi"
        string nip_kepala_sekolah "NIP penandatangan"
        string jabatan_kepala_sekolah "Jabatan (e.g. Kepala Sekolah)"
        boolean is_aktif
        datetime created_at
    }

    USER {
        uuid id PK
        string username UK
        string email
        string password
        string first_name
        string last_name
        string role "ADMIN | PELATIH | ANGGOTA"
        string phone_number
        string avatar
        boolean is_active
        datetime date_joined
    }

    TINGKAT_SABUK {
        int id PK
        string nama_sabuk UK "Putih, Kuning, Hijau, Biru, Cokelat, Hitam"
        int urutan_tingkat UK
        string warna_hex
        int min_kehadiran_ukt "Persyaratan hadir % untuk UKT"
        text deskripsi
    }

    KATEGORI_TANDING {
        int id PK
        string nama "Tanding Putra/Putri, Seni Tunggal/Ganda/Regu"
        string kelas_tanding "Kelas A, B, C, Bebas"
        text catatan_teknis
    }

    ANGGOTA_PROFILE {
        uuid user_id PK, FK
        string nisn UK "10 Digit Angka Kemdikbudristek"
        int sekolah_id FK "nullable, asal sekolah"
        string jenis_kelamin "L | P"
        date tanggal_lahir "Autentikasi portal wali murid"
        string kelas_sekolah "Contoh: X PPLG 1"
        int sabuk_saat_ini_id FK
        int kategori_fokus_id FK "nullable"
        string nama_wali
        string no_hp_wali
        string status_keanggotaan "AKTIF | NONAKTIF | ALUMNI"
        json face_descriptor "128-d floating embedding vector"
        datetime face_registered_at "Waktu registrasi biometrik"
    }

    PELATIH_PROFILE {
        uuid user_id PK, FK
        string nomor_registrasi UK
        string tingkatan_pendekar "Pelatih Muda, Madya, Pendekar"
        string spesialisasi "Tanding | Seni | Wasit Juri | Fisik"
        string sertifikasi_sk
    }

    JADWAL_LATIHAN {
        int id PK
        string nama_jadwal "Latihan Reguler Sore"
        int hari_indeks "0=Senin s/d 6=Minggu"
        time jam_mulai
        time jam_selesai
        string nama_lokasi "Dojo Silat / GOR Sekolah"
        decimal latitude
        decimal longitude
        int radius_toleransi_meter "Default: 100m"
        boolean is_aktif
        string status_persetujuan "MENUNGGU | DISETUJUI | DITOLAK"
        uuid dibuat_oleh_id FK "nullable"
        uuid disetujui_oleh_id FK "nullable"
        text catatan_admin
    }

    SESI_LATIHAN {
        uuid id PK
        int jadwal_id FK "nullable, dasar jadwal"
        uuid pelatih_id FK "Pelatih penanggung jawab"
        date tanggal
        datetime jam_buka
        datetime jam_tutup "nullable"
        string status "TERJADWAL | DIBUKA | SELESAI | BATAL"
        string status_persetujuan "MENUNGGU | DISETUJUI | DITOLAK"
        uuid disetujui_oleh_id FK "nullable, admin verifikator"
        datetime waktu_disetujui "nullable"
        text catatan_persetujuan
        string tipe_sesi "REGULER | TC_KEJUARAAN | UKT | FISIK"
        text materi_latihan "Jurnal kurikulum harian"
        string nama_lokasi "Lokasi latihan fleksibel"
        time jam_mulai "Jam mulai mandiri"
        time jam_selesai "Jam selesai mandiri"
        string qr_secret_salt "Kunci HMAC QR Code"
        decimal latitude_aktual
        decimal longitude_aktual
        int total_hadir "Denormalized counter"
        string foto_kegiatan "Dokumentasi sesi latihan"
        string keterangan_foto
    }

    PRESENSI {
        uuid id PK
        uuid sesi_id FK
        uuid anggota_id FK
        string status "HADIR | IZIN | SAKIT | ALPA"
        string metode_presensi "FACE_SCAN | QR_DYNAMIC | MANUAL_PELATIH | MANUAL_MANDIRI | GEOFENCE"
        datetime waktu_presensi
        string bukti_foto "Foto surat keterangan izin/sakit"
        string foto_face_scan "Snapshot audit wajah saat scan AI"
        float face_distance "Euclidean distance kemiripan biometrik"
        text catatan_alasan
        boolean is_verified
        uuid verified_by_id FK "nullable"
        decimal user_latitude
        decimal user_longitude
        string ip_address
        string device_user_agent
    }

    RIWAYAT_SABUK {
        uuid id PK
        uuid anggota_id FK
        int sabuk_asal_id FK
        int sabuk_baru_id FK
        uuid penguji_pelatih_id FK
        date tanggal_ujian
        string hasil "LULUS_TERPUJI | LULUS | MENGULANG"
        text evaluasi_teknik
    }

    PENGAJUAN_HAPUS_ANGGOTA {
        uuid id PK
        uuid anggota_id FK "Pesilat yang diajukan hapus"
        uuid diajukan_oleh_id FK "Pelatih pemohon"
        text alasan "Alasan permohonan hapus/mutasi"
        string status "MENUNGGU | DISETUJUI | DITOLAK"
        uuid disetujui_oleh_id FK "nullable, admin"
        text catatan_admin
        datetime created_at
        datetime updated_at
    }
```

---

## 2. Kamus Data & Spesifikasi Kolom (Data Dictionary)

### 2.1 Entitas: `Sekolah` (`core_sekolah`)
Master data institusi sekolah dalam skenario *multi-school / multi-tenant*. Mengelola konfigurasi kop surat dan data tanda tangan resmi pada cetak laporan.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK, Auto | ID unik sekolah |
| `nama_sekolah` | VARCHAR(150) | Not Null, Unique | Nama resmi sekolah (e.g., "SMKN 1 Rongga") |
| `npsn` | VARCHAR(20) | Nullable | Nomor Pokok Sekolah Nasional resmi Kemdikbud |
| `alamat` | TEXT | Nullable | Alamat lengkap sekolah untuk kop surat |
| `logo_sekolah` | FileField / VARCHAR(255) | Nullable | Path berkas lambang/logo sekolah (`sekolah_logos/`) untuk Kop Surat |
| `nama_kepala_sekolah` | VARCHAR(150) | Default: "Drs. H. Mulyadi, M.M" | Nama pejabat kepala sekolah untuk tanda tangan |
| `nip_kepala_sekolah` | VARCHAR(50) | Default: "19720412 199802 1 003"| NIP kepala sekolah untuk validasi dokumen dinas |
| `jabatan_kepala_sekolah` | VARCHAR(100) | Default: "Kepala Sekolah" | Nomenklatur jabatan resmi |
| `is_aktif` | BOOLEAN | Default: True | Status keaktifan kemitraan sekolah |
| `created_at` | DATETIME | Auto Now Add | Waktu penambahan data sekolah |

---

### 2.2 Entitas: `User` (`accounts_user`)
Meng-inherit `AbstractUser` bawaan Django dengan primary key UUID untuk keamanan referensi URL dan integrasi otentikasi standar industri.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, Auto UUIDv4 | Pengidentifikasi unik global |
| `username` | VARCHAR(150) | Unique, Not Null | Kredensial unik untuk login pengguna |
| `email` | VARCHAR(254) | Nullable, Indexed | Email pengguna untuk reset password & notifikasi |
| `password` | VARCHAR(128) | Not Null | Hashed password (PBKDF2 SHA-256) |
| `first_name` | VARCHAR(150) | Not Null | Nama depan pengguna |
| `last_name` | VARCHAR(150) | Blank | Nama belakang pengguna |
| `role` | VARCHAR(20) | Choices, Default: 'ANGGOTA' | Choices: `ADMIN`, `PELATIH`, `ANGGOTA` |
| `phone_number` | VARCHAR(20) | Nullable | Nomor WhatsApp aktif untuk kontak darurat |
| `avatar` | FileField / VARCHAR(255) | Nullable | Path foto profil pengguna (`avatars/%Y/%m/`) |
| `is_active` | BOOLEAN | Default: True | Status aktivasi akun pengguna |
| `date_joined` | DATETIME | Default: Now | Waktu pendaftaran akun ke sistem |

---

### 2.3 Entitas: `AnggotaProfile` (`members_anggotaprofile`)
Detail informasi pesilat yang terhubung 1-to-1 dengan User, dilengkapi validasi NISN 10 digit Kemdikbudristek dan representasi biometrik wajah.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK, FK (`User.id`), OneToOne | Relasi ke akun User utama |
| `nisn` | VARCHAR(10) | Unique, Regex `^\d{10}$` | 10 digit NISN resmi standar Kemdikbudristek |
| `sekolah_id` | INT | FK (`Sekolah.id`), Nullable | Asal sekolah pesilat (*Multi-School Support*) |
| `jenis_kelamin` | CHAR(1) | Choices (`L`, `P`) | L = Laki-laki, P = Perempuan |
| `tanggal_lahir` | DATE | Nullable | Kredensial verifikasi pencarian di Portal Wali Murid |
| `kelas_sekolah` | VARCHAR(50) | Not Null | Kelas & Jurusan di sekolah (misal: "X PPLG 1") |
| `sabuk_saat_ini_id` | INT | FK (`TingkatSabuk.id`) | Sabuk yang saat ini disandang pesilat |
| `kategori_fokus_id` | INT | FK (`KategoriTanding.id`), Nullable | Peminatan prestasi (Tanding / Seni) |
| `nama_wali` | VARCHAR(100) | Nullable | Nama orang tua / wali murid |
| `no_hp_wali` | VARCHAR(20) | Nullable | Nomor kontak darurat wali murid |
| `status_keanggotaan`| VARCHAR(20) | Choices, Default: 'AKTIF' | Choices: `AKTIF`, `NONAKTIF`, `ALUMNI` |
| `face_descriptor` | JSONField | Nullable | Vektor 128 float embedding fitur wajah (face-api.js) |
| `face_registered_at`| DATETIME | Nullable | Waktu rekaman pendaftaran biometrik pertama kali |

---

### 2.4 Entitas: `PelatihProfile` (`members_pelatihprofile`)
Profil instruktur/coach perguruan silat penanggung jawab latihan dan penguji kenaikan tingkat.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `user_id` | UUID | PK, FK (`User.id`), OneToOne | Relasi ke akun User utama |
| `nomor_registrasi` | VARCHAR(50) | Unique, Not Null | Nomor lisensi/registrasi kepelatihan perguruan |
| `tingkatan_pendekar`| VARCHAR(100) | Nullable | Gelar tingkatan (e.g., Pelatih Muda, Pendekar) |
| `spesialisasi` | VARCHAR(100) | Nullable | Keahlian (Tanding, Seni Tunggal/Ganda/Regu, Fisik) |
| `sertifikasi_sk` | VARCHAR(100) | Nullable | Nomor SK pengangkatan/sertifikasi kepelatihan |

---

### 2.5 Entitas: `JadwalLatihan` (`schedule_jadwallatihan`)
Master template jadwal mingguan dengan integrasi koordinat geofence dan alur persetujuan admin.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK, Auto | ID jadwal latihan |
| `nama_jadwal` | VARCHAR(100) | Not Null | Nama kegiatan (e.g. "Latihan Rutin Teknik & Jurus")|
| `hari_indeks` | SMALLINT | Choices (0-6) | 0 = Senin s/d 6 = Minggu |
| `jam_mulai` | TIME | Not Null | Waktu mulai latihan (e.g. 15:30:00) |
| `jam_selesai` | TIME | Not Null | Waktu selesai latihan (e.g. 17:30:00) |
| `nama_lokasi` | VARCHAR(150) | Not Null | Nama tempat fisik (e.g. "Dojo Utama SMKN 1 Rongga") |
| `latitude` | DECIMAL(10, 8) | Nullable | Titik koordinat garis lintang geofence |
| `longitude` | DECIMAL(11, 8) | Nullable | Titik koordinat garis bujur geofence |
| `radius_toleransi_meter`| INT | Default: 100 | Toleransi jarak validasi absensi (meter) |
| `is_aktif` | BOOLEAN | Default: True | Status aktif jadwal mingguan |
| `status_persetujuan`| VARCHAR(20) | Choices, Default: 'DISETUJUI' | Choices: `MENUNGGU`, `DISETUJUI`, `DITOLAK` |
| `dibuat_oleh_id` | UUID | FK (`User.id`), Nullable | Pelatih yang mengusulkan jadwal |
| `disetujui_oleh_id`| UUID | FK (`User.id`), Nullable | Admin/Pembina yang menyetujui jadwal |
| `catatan_admin` | TEXT | Blank, Nullable | Catatan revisi atau pertimbangan admin |

---

### 2.6 Entitas: `SesiLatihan` (`attendance_sesilatihan`)
Sesi latihan konkret harian dengan dukungan jadwal fleksibel (lokasi & jam mandiri), dokumentasi kegiatan, serta verifikasi admin.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, Auto UUIDv4 | ID unik sesi latihan |
| `jadwal_id` | INT | FK (`JadwalLatihan.id`), Nullable | Acuan jadwal rutin (opsional untuk sesi mandiri) |
| `pelatih_id` | UUID | FK (`User.id`), Protect | Pelatih penanggung jawab sesi |
| `tanggal` | DATE | Default: Now, Indexed | Tanggal pelaksanaan sesi latihan |
| `jam_buka` | DATETIME | Default: Now | Waktu tepat sesi dibuka pelatih |
| `jam_tutup` | DATETIME | Nullable | Waktu tepat sesi ditutup pelatih |
| `status` | VARCHAR(20) | Choices, Default: 'DIBUKA' | Choices: `TERJADWAL`, `DIBUKA`, `SELESAI`, `BATAL` |
| `status_persetujuan`| VARCHAR(20) | Choices, Default: 'DISETUJUI' | Choices: `MENUNGGU`, `DISETUJUI`, `DITOLAK` |
| `disetujui_oleh_id`| UUID | FK (`User.id`), Nullable | Admin yang menyetujui pelaksanaan sesi |
| `waktu_disetujui` | DATETIME | Nullable | Waktu diterbitkannya persetujuan admin |
| `catatan_persetujuan`| TEXT | Blank, Nullable | Catatan/instruksi admin terkait sesi |
| `tipe_sesi` | VARCHAR(20) | Choices, Default: 'REGULER' | Choices: `REGULER`, `TC_KEJUARAAN`, `UKT`, `FISIK` |
| `materi_latihan` | TEXT | Blank, Nullable | Jurnal materi ajar harian yang diajarkan |
| `nama_lokasi` | VARCHAR(150) | Blank, Nullable | Lokasi sesi fleksibel/ad-hoc jika di luar dojo rutin |
| `jam_mulai` | TIME | Blank, Nullable | Jam mulai mandiri untuk sesi fleksibel |
| `jam_selesai` | TIME | Blank, Nullable | Jam selesai mandiri untuk sesi fleksibel |
| `qr_secret_salt` | VARCHAR(64) | Default: random hex | Kunci rahasia pembangkit token HMAC QR Code |
| `latitude_aktual` | DECIMAL(10,8) | Nullable | Titik koordinat pelatih saat membuka sesi |
| `longitude_aktual`| DECIMAL(11,8) | Nullable | Titik koordinat pelatih saat membuka sesi |
| `total_hadir` | INT | Default: 0 | Nilai hitung cepat terdenormalisasi jumlah hadir |
| `foto_kegiatan` | FileField / VARCHAR(255)| Nullable | Foto dokumentasi kegiatan sesi (`kegiatan_sesi/%Y/%m/`) |
| `keterangan_foto` | VARCHAR(255) | Blank, Nullable | Deskripsi singkat foto kegiatan latihan |

---

### 2.7 Entitas: `Presensi` (`attendance_presensi`)
Pencatatan riwayat transaksi kehadiran pesilat dengan audit trail lengkap (snapshot foto biometrik & metrik jarak Euclidean).

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, Auto UUIDv4 | ID transaksi unik presensi |
| `sesi_id` | UUID | FK (`SesiLatihan.id`), Cascade | Sesi latihan yang dihadiri |
| `anggota_id` | UUID | FK (`AnggotaProfile.user_id`), Cascade | Pesilat yang tercatat presensinya |
| `status` | VARCHAR(10) | Choices, Default: 'HADIR' | Choices: `HADIR`, `IZIN`, `SAKIT`, `ALPA` |
| `metode_presensi` | VARCHAR(20) | Choices, Default: 'FACE_SCAN' | Choices: `FACE_SCAN`, `QR_DYNAMIC`, `MANUAL_PELATIH`, `MANUAL_MANDIRI`, `GEOFENCE` |
| `waktu_presensi` | DATETIME | Default: Now, Indexed | Timestamp tepat saat absensi tercatat |
| `bukti_foto` | FileField / VARCHAR(255) | Nullable | Foto surat dokter/keterangan izin (`surat_izin/%Y/%m/`) |
| `foto_face_scan` | FileField / VARCHAR(255) | Nullable | Foto snapshot wajah hasil scan kamera (`face_scans/%Y/%m/`) |
| `face_distance` | FLOAT | Nullable | Nilai Euclidean distance saat verifikasi biometrik |
| `catatan_alasan` | TEXT | Blank, Nullable | Alasan izin/sakit atau catatan pelatih |
| `is_verified` | BOOLEAN | Default: True | Flag verifikasi validitas presensi |
| `verified_by_id` | UUID | FK (`User.id`), Nullable | Admin/Pelatih yang menyetujui izin atau mengoreksi data |
| `user_latitude` | DECIMAL(10,8) | Nullable | Garis lintang perangkat siswa saat absensi |
| `user_longitude`| DECIMAL(11,8) | Nullable | Garis bujur perangkat siswa saat absensi |
| `ip_address` | GenericIPAddress | Nullable | IP Address perangkat siswa |
| `device_user_agent`| VARCHAR(255) | Nullable | Tipe browser/perangkat yang digunakan |

---

### 2.8 Entitas: `PengajuanHapusAnggota` (`members_pengajuanhapusanggota`)
Mekanisme pengamanan integritas data historis pesilat. Pelatih mengajukan permohonan penghapusan, dan hanya Admin yang berhak mengeksekusi penghapusan.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK, Auto UUIDv4 | ID pengajuan |
| `anggota_id` | UUID | FK (`AnggotaProfile.user_id`), Cascade | Pesilat yang diajukan untuk dihapus/dimutasi |
| `diajukan_oleh_id`| UUID | FK (`User.id`), Cascade | Pelatih pemohon penghapusan |
| `alasan` | TEXT | Not Null | Penjelasan alasan penghapusan anggota |
| `status` | VARCHAR(20) | Choices, Default: 'MENUNGGU' | Choices: `MENUNGGU`, `DISETUJUI`, `DITOLAK` |
| `disetujui_oleh_id`| UUID | FK (`User.id`), Nullable | Admin pembina yang memutuskan permohonan |
| `catatan_admin` | TEXT | Blank, Nullable | Alasan persetujuan atau penolakan admin |
| `created_at` | DATETIME | Auto Now Add | Waktu permohonan diajukan |
| `updated_at` | DATETIME | Auto Now | Waktu status terakhir diperbarui |

---

### 2.9 Entitas: `TingkatSabuk` (`core_tingkatsabuk`) & `RiwayatKenaikanSabuk` (`members_riwayatkenaikansabuk`)
Master hierarki sabuk dan buku rapor riwayat kenaikan tingkat pesilat.

- **`TingkatSabuk`**: `id` (PK), `nama_sabuk` (UK), `urutan_tingkat` (UK), `warna_hex`, `min_kehadiran_ukt` (%), `deskripsi`.
- **`RiwayatKenaikanSabuk`**: `id` (PK, UUID), `anggota_id` (FK), `sabuk_asal_id` (FK), `sabuk_baru_id` (FK), `penguji_pelatih_id` (FK), `tanggal_ujian`, `hasil` (`LULUS_TERPUJI`, `LULUS`, `MENGULANG`), `evaluasi_teknik`.

---

### 2.10 Entitas: `Perguruan` (`core_perguruan`)
Entitas tunggal (*singleton pattern*) untuk menyimpan identitas resmi padepokan/perguruan pencak silat, branding aplikasi global, kop surat ganda cetak laporan presensi, dan sertifikat resmi.

| Nama Kolom | Tipe Data | Constraint | Keterangan |
| :--- | :--- | :--- | :--- |
| `id` | INT | PK, Auto | ID unik konfigurasi perguruan |
| `nama_perguruan` | VARCHAR(150) | Not Null | Nama resmi perguruan silat (e.g., "Perguruan Pencak Silat Indonesia") |
| `singkatan` | VARCHAR(50) | Not Null, Default: "SilatTrack" | Brand aplikasi pada bilah navigasi dan tajuk |
| `logo_perguruan` | FileField / VARCHAR(255) | Nullable | Berkas lambang perguruan silat (`perguruan_logos/`) |
| `semboyan` | VARCHAR(200) | Nullable | Semboyan / motto resmi perguruan silat |
| `alamat_pusat` | TEXT | Nullable | Alamat sekretariat pusat / padepokan silat |
| `kontak` | VARCHAR(100) | Nullable | Nomor kontak / telepon sekretariat |
| `created_at` | DATETIME | Auto Now Add | Waktu inisialisasi entitas |
| `updated_at` | DATETIME | Auto Now | Waktu terakhir pembaruan data |

---

## 3. Indeks & Aturan Integritas Data (Constraints & Indexes)

1. **Unique Key Komposit & Keamanan Transaksi**:
   - `UNIQUE (sesi_id, anggota_id)` pada tabel `Presensi`: Menjamin pesilat tidak dapat memiliki lebih dari satu baris presensi pada sesi yang sama (*Zero Double Attendance*).
   - `UNIQUE (nisn)` pada tabel `AnggotaProfile`: Memastikan setiap pesilat memiliki 10 digit nomor induk unik yang terstandarisasi.
2. **Compound Index untuk Performa Tinggi**:
   - `INDEX idx_presensi_waktu_status (waktu_presensi, status)`: Mempercepat agregasi laporan rekap bulanan dan perhitungan streak kehadiran.
   - `INDEX idx_sesi_tgl_status (tanggal, status)`: Mengoptimalkan pemuatan dashboard monitoring harian.
3. **Cascade & Protection Rules**:
   - Penghapusan `User` akan me-trigger `CASCADE` ke `AnggotaProfile` atau `PelatihProfile`.
   - Penghapusan `SesiLatihan` dibatasi (`PROTECT`) jika telah memiliki data riwayat `Presensi` untuk menjaga integritas data rapor sekolah.
   - Penghapusan anggota dilindungi oleh workflow `PengajuanHapusAnggota` untuk mencegah manipulasi data kehadiran sepihak.
