# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## SilatTrack: Sistem Absensi dan Manajemen Ekstrakurikuler Pencak Silat

| Informasi Dokumen | Keterangan |
| :--- | :--- |
| **Versi Dokumen** | 1.1 |
| **Tanggal Pembaruan** | 12 Oktober 2026 (Revisi: November 2026) |
| **Status** | Spesifikasi Kebutuhan Resmi (Final Draft) |
| **Dokumen Acuan** | PRD SilatTrack v1.1.0, ERD & Data Dictionary, Architectural & Technical Design Document (TDD) v1.1.0 |

---

### Riwayat Perubahan Dokumen
| Versi | Tanggal | Deskripsi Perubahan |
| :--- | :--- | :--- |
| 1.0 | 12-10-2026 | Penyusunan awal draf SRS berdasarkan PRD, ERD, dan dokumen arsitektur. |
| 1.1 | 03-11-2026 | Penyempurnaan tabel Kebutuhan Fungsional (FR) dan Non-Fungsional (NFR): penambahan kolom keterangan & justifikasi rekayasa perangkat lunak, standardisasi skala prioritas menjadi **Wajib**, **Penting**, dan **Opsional**, serta penegasan klasifikasi batasan arsitektur perangkat lunak. |

---

## Daftar Isi
1. [Pendahuluan](#1-pendahuluan)
   - 1.1 [Tujuan](#11-tujuan)
   - 1.2 [Ruang Lingkup](#12-ruang-lingkup)
   - 1.3 [Dokumen Acuan](#13-dokumen-acuan)
   - 1.4 [Konvensi dan Definisi Prioritas](#14-konvensi-dan-definisi-prioritas)
2. [Gambaran Umum Sistem](#2-gambaran-umum-sistem)
   - 2.1 [Perspektif Produk](#21-perspektif-produk)
   - 2.2 [Kelas Pengguna dan Hak Akses](#22-kelas-pengguna-dan-hak-akses)
   - 2.3 [Lingkungan Operasional](#23-lingkungan-operasional)
   - 2.4 [Batasan Desain dan Implementasi](#24-batasan-desain-dan-implementasi)
3. [Persyaratan Fungsional](#3-persyaratan-fungsional)
4. [Persyaratan Antarmuka Eksternal](#4-persyaratan-antarmuka-eksternal)
   - 4.1 [Antarmuka Pengguna (UI)](#41-antarmuka-pengguna)
   - 4.2 [Antarmuka Perangkat Keras](#42-antarmuka-perangkat-keras)
   - 4.3 [Antarmuka Perangkat Lunak & Batasan Implementasi](#43-antarmuka-perangkat-lunak--batasan-implementasi)
   - 4.4 [Antarmuka Komunikasi](#44-antarmuka-komunikasi)
5. [Persyaratan Non-Fungsional](#5-persyaratan-non-fungsional)
6. [Persyaratan Data dan Aturan Bisnis](#6-persyaratan-data-dan-aturan-bisnis)
   - 6.1 [Entitas Data Utama](#61-entitas-data-utama)
   - 6.2 [Aturan Bisnis (Business Rules)](#62-aturan-bisnis)
   - 6.3 [Aturan Penyimpanan dan Validasi](#63-aturan-penyimpanan-dan-validasi)
7. [Kriteria Penerimaan dan Pengujian](#7-kriteria-penerimaan-dan-pengujian)
8. [Batasan, Asumsi, dan Ketergantungan](#8-batasan-asumsi-dan-ketergantungan)
9. [Matriks Ketertelusuran](#9-matriks-ketertelusuran)
- [Lampiran A. Glosarium](#lampiran-a-glosarium)
- [Lampiran B. Catatan Klarifikasi](#lampiran-b-catatan-klarifikasi)

---

## 1. Pendahuluan

### 1.1 Tujuan
Dokumen *Software Requirements Specification* (SRS) ini menetapkan seluruh kebutuhan fungsional, kebutuhan non-fungsional, antarmuka sistem, spesifikasi data, serta kriteria penerimaan pengujian untuk **SilatTrack**. Dokumen ini menjadi pedoman utama bagi pengembang perangkat lunak, penguji mutu (*QA*), pembina eskul, pelatih, dan pihak manajemen sekolah dalam membangun serta memvalidasi kesesuaian sistem.

### 1.2 Ruang Lingkup
**SilatTrack** adalah aplikasi web modern responsif (PWA-ready) yang dirancang khusus untuk manajemen kehadiran dan keaktifan ekstrakurikuler pencak silat. Lingkup sistem mencakup:
- Autentikasi berbasis peran (*Role-Based Access Control* / RBAC).
- Pengelolaan profil pesilat dan pelatih.
- Pengaturan jadwal rutin mingguan dan sesi latihan dinamis.
- Presensi multi-metode dengan biometrik pengenalan wajah (*AI Face Recognition*) sebagai metode utama, didukung presensi manual pelatih dan *Dynamic Rolling QR Code* sebagai metode alternatif.
- Pengajuan izin/sakit disertai bukti surat.
- Dashboard rekapitulasi kehadiran, gamifikasi (*attendance streak*), evaluasi otomatis prasyarat Ujian Kenaikan Tingkat (UKT), dan ekspor laporan resmi (PDF dan Excel).

### 1.3 Dokumen Acuan
1. *Product Requirements Document* (PRD) SilatTrack v1.1.0 — AI Face Recognition Scanner.
2. *Entity Relationship Diagram* (ERD) & *Data Dictionary* SilatTrack.
3. *Architectural & Technical Design Document* (TDD) SilatTrack v1.1.0.

### 1.4 Konvensi dan Definisi Prioritas
Setiap kebutuhan diberi kode unik (**FR-xxx** untuk Kebutuhan Fungsional dan **NFR-xxx** untuk Kebutuhan Non-Fungsional).
Untuk mempermudah pemahaman seluruh pemangku kepentingan tanpa kerancuan istilah teknis asing, skala prioritas diklasifikasikan ke dalam 3 tingkatan bahasa Indonesia yang lugas:
1. **Wajib:** Kebutuhan mutlak (*core system*). Sistem tidak dapat dirilis atau dinyatakan berfungsi tanpa pemenuhan fitur ini.
2. **Penting:** Kebutuhan bernilai tinggi yang sangat dianjurkan untuk efisiensi operasional dan kenyamanan, namun sistem masih dapat berjalan sementara waktu jika ditunda.
3. **Opsional:** Fitur pendukung/pelengkap (*nice-to-have*) yang dapat dikerjakan setelah kebutuhan utama terpenuhi atau pada iterasi pengembangan berikutnya.

---

## 2. Gambaran Umum Sistem

### 2.1 Perspektif Produk
SilatTrack dibangun menggunakan paradigma arsitektur **HTML-over-the-Wire / Modern Monolith (DATH Stack)**:
- **Django 5.2:** Menangani routing, autentikasi, business logic, ORM, dan rendering server-side.
- **HTMX 2:** Melakukan pertukaran fragmen HTML secara instan (*partial DOM swap*) tanpa *full page reload*.
- **Alpine.js 3:** Menangani interaksi mikro di sisi browser (kontrol stream kamera, pewaktu mundur, dan dialog modal).
- **Tailwind CSS & Google Material Design 3 (M3):** Menyediakan sistem desain visual bertema Silat Crimson (`#8A1C14`) dan Brass/Gold (`#7D5800`).
- **face-api.js:** Menjalankan inferensi pendeteksian wajah dan ekstraksi *descriptor* 128 dimensi langsung di browser klien menggunakan WebGL.
- **PostgreSQL / SQLite:** Mesin penyimpanan data relasional yang ternormalisasi (3NF).

### 2.2 Kelas Pengguna dan Hak Akses
| Peran | Deskripsi & Kemampuan Utama |
| :--- | :--- |
| **Admin / Pembina Eskul** | Memantau seluruh aktivitas eskul, mengelola akun pelatih dan anggota, mengevaluasi persentase kehadiran, mengaudit bukti foto absensi, dan mengunduh laporan rekapitulasi (PDF/Excel). |
| **Pelatih / Instruktur** | Membuat, membuka, dan menutup sesi latihan; memantau absensi live; mengubah status kehadiran anggota secara cepat (*quick toggle*); memvalidasi surat izin/sakit; mencatat jurnal materi latihan; serta mengelola evaluasi kenaikan sabuk. |
| **Anggota / Pesilat** | Melakukan absensi wajah mandiri saat sesi dibuka; menggunakan metode absensi darurat jika kamera bermasalah; mengajukan permohonan izin/sakit beserta lampiran foto; serta memantau riwayat kehadiran dan syarat UKT. |
| **Orang Tua / Wali Murid** | Memperoleh akses informasi transparansi status kehadiran siswa pada kegiatan ekstrakurikuler. |

### 2.3 Lingkungan Operasional
- **Sisi Klien:** Peramban modern (*Chrome, Safari, Firefox, Edge*) pada smartphone Android/iOS (target resolusi 360–430 px), tablet, maupun komputer desktop. Perangkat memerlukan modul kamera fisik dan izin akses peramban (*webcam permission*).
- **Penyajian AI Lokal:** Seluruh bobot model neural network disajikan dari direktori lokal server (`/static/models/`) agar proses pembacaan wajah tidak bergantung pada koneksi internet publik.
- **Sisi Server:** Server aplikasi Python berbasis Django yang berkomunikasi melalui protokol aman HTTP/HTTPS dengan basis data relasional.

### 2.4 Batasan Desain dan Implementasi
1. Pola aplikasi mengutamakan *Zero JavaScript Build Fatigue* tanpa framework SPA berat (React/Vue/Angular).
2. Tampilan antarmuka patuh pada token resmi Google Material Design 3 (Top App Bar, Navigation Bar Mobile, Navigation Rail Desktop, M3 Cards, dan FAB).
3. Deteksi dan ekstraksi wajah dilakukan di peramban klien, namun **verifikasi akhir wajib divalidasi ulang di server** (*Zero Client Trust*).

---

## 3. Persyaratan Fungsional

*Kebutuhan Fungsional mendefinisikan apa yang harus dilakukan oleh sistem (layanan, proses input-output, aturan bisnis, dan aksi pengguna).*

| ID | Area / Modul | Kebutuhan Fungsional | Prioritas | Keterangan & Justifikasi Status Fungsional |
| :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Autentikasi | Sistem menyediakan formulir dan mekanisme login terpisah untuk peran ADMIN, PELATIH, dan ANGGOTA. | **Wajib** | **Fungsional (Layanan Pengguna):** Aksi nyata pengguna dalam memasukkan kredensial dan sistem memverifikasi identitas pengguna. |
| **FR-002** | Otorisasi / RBAC | Sistem membatasi akses menu, aksi tombol, dan data yang tampil sesuai dengan peran pengguna yang sedang login. | **Wajib** | **Fungsional (Logika Hak Akses):** Logika internal sistem untuk memfilter halaman dan data yang berhak dilihat/dikelola tiap peran. |
| **FR-003** | Manajemen Sesi | Sistem menyediakan mekanisme pembuatan sesi login aktif, pelacakan waktu aktif, serta pemutusan sesi (*logout*). | **Wajib** | **Fungsional (Siklus Akun):** Layanan pengelolaan status aktif/tidak aktifnya pengguna. *(Atribut keamanannya diatur di NFR).* |
| **FR-004** | Manajemen Pengguna | Admin dapat membuat, melihat, mengedit, dan menonaktifkan akun pelatih maupun anggota eskul. | **Wajib** | **Fungsional (Operasi CRUD):** Fitur eksplisit bagi admin untuk memanipulasi data akun pengguna di dalam sistem. |
| **FR-005** | Profil Pengguna | Sistem menyimpan dan menampilkan data identitas dasar, nomor kontak, status aktif, dan foto profil pengguna. | **Wajib** | **Fungsional (Pengelolaan Data Profil):** Layanan penyimpanan dan penarikan informasi identitas pengguna dari basis data. |
| **FR-006** | Profil Anggota | Sistem menyimpan data khusus pesilat (NISN, kelas, jenis kelamin, tanggal lahir, nama/kontak wali, sabuk, dan kategori tanding). | **Wajib** | **Fungsional (Entitas Khusus Pesilat):** Menyimpan atribut khas pesilat yang dibutuhkan untuk administrasi eskul dan seleksi tanding. |
| **FR-007** | Profil Pelatih | Sistem menyimpan nomor registrasi pelatih, tingkatan pendekar, keahlian khusus (tanding/seni), dan sertifikasi SK. | **Penting** | **Fungsional (Entitas Khusus Pelatih):** Menyimpan portofolio legalitas pelatih sebagai penanggung jawab latihan dan penguji kenaikan sabuk. |
| **FR-008** | Ekstraksi Biometrik | Sistem dapat menyalakan kamera, menemukan wajah, dan membaca pola fitur wajah (vektor 128 dimensi) via browser. | **Wajib** | **Fungsional (Pemrosesan Data Masukan):** Mengubah input citra kamera fisik menjadi data terstruktur (vektor) untuk diolah sistem. |
| **FR-009** | Registrasi Wajah Awal | Sistem menyediakan menu pendaftaran wajah pertama kali (*face enrollment*) bagi pesilat baru, disertai foto acuan. | **Wajib** | **Fungsional (Alur Registrasi Data Acuan):** Alur kerja awal bagi siswa baru untuk menyimpan data acuan wajah yang akan dipakai selamanya. |
| **FR-010** | Pencocokan Wajah Klien | Browser membandingkan pola wajah dari kamera dengan data acuan milik siswa menggunakan perhitungan jarak kemiripan. | **Wajib** | **Fungsional (Algoritma Pencocokan Lokal):** Menjalankan komparasi wajah langsung di ponsel siswa sebelum mengirimkan hasil ke server. |
| **FR-011** | Deteksi Kestabilan | Sistem menahan kamera beberapa detik hingga posisi wajah diam dan stabil sebelum mengirim presensi secara otomatis. | **Wajib** | **Fungsional (Logika Alur Antarmuka):** Mengatur alur interaksi kamera agar tidak mengambil foto yang buram atau tidak sengaja terpotret. |
| **FR-012** | Validasi Wajah Server | Server mengecek ulang data wajah kiriman browser dengan data acuan sebelum resmi menyatakan pesilat HADIR. | **Wajib** | **Fungsional (Logika Verifikasi Server):** Keputusan sistem di server untuk menerima atau menolak keabsahan wajah siswa. |
| **FR-013** | Presensi Wajah Mandiri | Pesilat dapat melakukan absen wajah mandiri hanya jika sesi latihan hari tersebut sudah DIBUKA oleh pelatih. | **Wajib** | **Fungsional (Validasi Aturan Bisnis):** Memeriksa syarat status sesi latihan sebelum mengizinkan siswa mengirim data kehadiran. |
| **FR-014** | Presensi Manual Mandiri | Siswa dapat mengisi formulir klaim presensi darurat secara mandiri jika kamera handphone bermasalah atau rusak. | **Wajib** | **Fungsional (Fitur Jalur Cadangan):** Memberi alternatif bagi siswa agar tetap tercatat absensinya saat perangkat berkendala fisik. |
| **FR-015** | Pencatatan Cepat Pelatih | Pelatih dapat langsung mengubah status pesilat (HADIR, IZIN, SAKIT, ALPA) dengan satu sentuhan tombol (*quick toggle*). | **Wajib** | **Fungsional (Fitur Cepat Operasional):** Aksi langsung pelatih untuk mencatat atau mengoreksi kehadiran siswa tanpa membuka halaman baru. |
| **FR-016** | Presensi Massal | Pelatih dapat mencentang seluruh pesilat yang hadir secara serempak hanya dengan sekali klik (*bulk action*). | **Penting** | **Fungsional (Otomasi Data Massal):** Fitur percepatan penginputan data untuk menghemat waktu pelatih saat anggota yang datang sangat banyak. |
| **FR-017** | Presensi Dynamic QR | Sistem menyediakan alternatif presensi dengan memindai kode QR bergerak yang tampil di layar proyektor / ponsel pelatih. | **Penting** | **Fungsional (Metode Alternatif Presensi):** Fitur pemindaian kode QR temporal sebagai opsi kedua jika presensi wajah sedang antre panjang. |
| **FR-018** | Pencatatan Info Presensi | Sistem menyimpan secara lengkap metode yang dipakai (Wajah/QR/Manual), jam absensi, status, dan siapa yang memverifikasi. | **Wajib** | **Fungsional (Pencatatan Riwayat Lengkap):** Menjamin setiap satu kali pesilat absen, seluruh jejak transaksinya tersimpan ke basis data. |
| **FR-019** | Cegah Presensi Ganda | Sistem otomatis menolak jika seorang siswa mencoba mengirimkan presensi lebih dari satu kali pada sesi latihan yang sama. | **Wajib** | **Fungsional (Logika Validasi Transaksi):** Menjaga agar satu siswa tidak memiliki dua record kehadiran pada hari latihan yang sama. |
| **FR-020** | Pengajuan Izin / Sakit | Siswa dapat mengajukan surat izin atau sakit dengan menuliskan alasan dan melampirkan foto bukti surat dokter/wali. | **Wajib** | **Fungsional (Formulir & Upload Berkas):** Layanan penerimaan data formulir serta penyimpanan berkas gambar surat keterangan izin. |
| **FR-021** | Persetujuan Izin / Sakit | Pelatih dapat melihat bukti surat izin/sakit siswa, lalu menekan tombol Setujui (*Approve*) atau Tolak (*Reject*). | **Wajib** | **Fungsional (Alur Kerja Persetujuan):** Aksi penentu keputusan oleh pelatih yang langsung memperbarui status kehadiran siswa. |
| **FR-022** | Buat Sesi Latihan | Pelatih dapat membuat jadwal sesi latihan baru dan memilih tipenya: Latihan Reguler, TC Kejuaraan, Ujian Sabuk, atau Fisik. | **Wajib** | **Fungsional (Pembuatan Data Transaksi):** Menyediakan sarana bagi pelatih untuk menginisialisasi wadah absensi harian. |
| **FR-023** | Buka dan Tutup Sesi | Pelatih dapat mengubah status sesi latihan: dari TERJADWAL $\rightarrow$ DIBUKA $\rightarrow$ SELESAI atau BATAL. | **Wajib** | **Fungsional (Pengendalian Alur Latihan):** Tombol pengendali operasional yang menentukan kapan waktu absensi mulai dan selesai. |
| **FR-024** | Penyimpanan Data Sesi | Sistem mencatat tanggal, jam buka/tutup aktual, pelatih penanggung jawab, materi ajar, dan ringkasan total hadir. | **Wajib** | **Fungsional (Pencatatan Rincian Kegiatan):** Merekam data pelaksanaan eskul secara menyeluruh untuk keperluan laporan ke sekolah. |
| **FR-025** | Kelola Jadwal Rutin | Admin/Pelatih dapat mengatur jadwal mingguan eskul (hari, jam mulai/selesai, lokasi lapangan, dan radius toleransi). | **Wajib** | **Fungsional (Master Data Jadwal):** Fitur pengelolaan jadwal tetap mingguan yang menjadi acuan pembuatan sesi otomatis. |
| **FR-026** | Catat Materi Latihan | Pelatih dapat mencatat rangkuman materi silat yang diajarkan (kuda-kuda, pasang, jurus tunggal baku, fisik, sambung). | **Wajib** | **Fungsional (Pencatatan Kurikulum Eskul):** Buku jurnal digital agar pelatih dan sekolah mengetahui capaian latihan pesilat. |
| **FR-027** | Grafik & Statistik Dashboard | Sistem menampilkan ringkasan jumlah yang hadir per pertemuan dan grafik persentase kehadiran bulanan. | **Wajib** | **Fungsional (Pengolahan & Tampilan Data):** Mengubah data mentah absensi menjadi grafik visual yang mudah dipahami pembina eskul. |
| **FR-028** | Ekspor Laporan Excel/PDF | Sistem dapat mengunduh laporan rekapitulasi kehadiran pesilat ke dalam format file Excel (.xlsx) dan PDF siap cetak. | **Wajib** | **Fungsional (Konversi & Ekspor Berkas):** Fitur penarikan data ke format dokumen fisik untuk pelaporan formal ke pihak sekolah/wali. |
| **FR-029** | Master Tingkatan Sabuk | Sistem menyediakan pengaturan urutan sabuk (Putih, Kuning, Hijau, dst.), warna tanda, dan syarat minimal persen hadir UKT. | **Wajib** | **Fungsional (Pengaturan Aturan Acuan):** Menu pengaturan kriteria kenaikan tingkat yang menjadi dasar perhitungan sistem. |
| **FR-030** | Catatan Riwayat Sabuk | Sistem mencatat riwayat sabuk pesilat sejak awal daftar, tanggal ujian kenaikan sabuk, nilai evaluasi, dan nama penguji. | **Wajib** | **Fungsional (Pencatatan Portofolio Prestasi):** Merekam rekam jejak kenaikan sabuk pesilat sepanjang bergabung di ekstrakurikuler. |
| **FR-031** | Cek Kelayakan Ujian (UKT) | Sistem otomatis menghitung apakah pesilat sudah memenuhi syarat minimal hadir untuk boleh ikut Ujian Kenaikan Tingkat. | **Wajib** | **Fungsional (Perhitungan Otomatis Bisnis):** Kalkulasi otomatis yang menghasilkan status apakah pesilat *Memenuhi Syarat* atau *Belum*. |
| **FR-032** | Gamifikasi (Streak & Badge) | Sistem dapat menghitung rekor latihan tanpa bolos (*streak*) dan memberikan lencana keaktifan pada profil pesilat. | **Opsional** | **Fungsional (Fitur Motivasi Tambahan):** Fitur hiburan/gamifikasi untuk memotivasi pesilat muda agar semakin rajin berlatih. |
| **FR-033** | Galeri Bukti Foto Absen | Sistem menyimpan foto wajah saat siswa melakukan scan dan menampilkannya pada halaman audit pelatih. | **Wajib** | **Fungsional (Penyimpanan Bukti Fisik):** Menyediakan foto dokumentasi presensi agar pelatih dapat memastikan kejujuran kehadiran siswa. |
| **FR-034** | Cek Lokasi (Geofencing) | Sistem dapat membaca koordinat lokasi ponsel siswa dan memastikan siswa memang benar-benar berada di area lapangan/dojo. | **Penting** | **Fungsional (Perhitungan Jarak Lokasi):** Fitur pembatasan jarak menggunakan GPS agar siswa tidak bisa absen dari luar lokasi latihan. |
| **FR-035** | Portal Pantau Wali Murid | Sistem dapat menyediakan halaman khusus bagi orang tua untuk memantau apakah anaknya hadir pada latihan silat hari ini. | **Opsional** | **Fungsional (Layanan Eksternal Publik):** Fasilitas keterbukaan informasi bagi wali murid untuk memantau kegiatan ekstrakurikuler anak. |
| **FR-036** | Catatan Audit Perubahan | Sistem mencatat nama pelatih/admin dan waktu ketika terjadi pengubahan status kehadiran secara manual. | **Wajib** | **Fungsional (Pencatatan Log Keamanan):** Mengetahui siapa yang mengubah data absensi jika suatu saat terjadi perselisihan data. |

---

## 4. Persyaratan Antarmuka Eksternal

### 4.1 Antarmuka Pengguna
- Mengadopsi prinsip desain Google Material Design 3 (M3).
- **Destinasi Navigasi Mobile:** 4 destinasi utama pada Navigation Bar bawah (Beranda, Presensi/Scan, Jadwal, Profil) dengan indikator berbentuk pil.
- **Reticle Pemindai Wajah:** Antarmuka pemindai dilengkapi panduan reticle oval dengan 3 status warna dinamis:
  - Abu-abu: Siaga (*Standby* / Menunggu wajah).
  - Kuning: Mendeteksi dan menstabilkan wajah (*Stabilizing buffer*).
  - Hijau: Terverifikasi dan mengirimkan data (*Verified*).
- **Umpan Balik Instan:** Menggunakan komponen Snackbar M3 dengan aksi pembatalan (*undo*) jika terjadi salah input.

### 4.2 Antarmuka Perangkat Keras
- **Kamera Ponsel / Webcam:** Resolusi minimal 720p dengan dukungan API browser `navigator.mediaDevices.getUserMedia`.
- **Modul GPS (Opsional):** Membaca koordinat lintang/bujur melalui `navigator.geolocation` jika fitur geofencing diaktifkan pada sesi terkait.

### 4.3 Antarmuka Perangkat Lunak & Batasan Implementasi
*(Komponen berikut merupakan Batasan Arsitektural & Teknologi / Architectural Constraints yang termasuk ke dalam kategori Kebutuhan Non-Fungsional).*

| Komponen | Versi Acuan | Peran dalam Sistem & Batasan Teknis |
| :--- | :--- | :--- |
| **Django** | 5.2 (Python) | Server backend monolitik, routing URL, autentikasi RBAC, middleware keamanan, dan ORM basis data. |
| **Alpine.js** | 3.x | Pengendali kamera di browser, countdown timer kode QR, dan state modal dialog (overhead amat ringan < 15 KB). |
| **face-api.js** | 0.22.x | Pustaka neural network klien berbasis TensorFlow.js untuk mendeteksi wajah dan menghasilkan descriptor 128D. |
| **HTMX** | 2.x | Mesin transmisi hypermedia via request AJAX untuk pembaruan komponen DOM tanpa memuat ulang seluruh halaman (*HTML-over-the-Wire*). |
| **Tailwind CSS** | 3.x | Kerangka kerja utilitas CSS untuk styling responsif dengan token warna Material Design 3. |
| **PostgreSQL / SQLite** | PostgreSQL 15+ / SQLite 3 | Mesin sistem manajemen basis data relasional (RDBMS) yang mendukung constraint data ketat. |
| **Penyimpanan Media** | Local / S3-compatible | Direktori penyimpanan berkas foto snapshot presensi, avatar, dan surat dokter. |

### 4.4 Antarmuka Komunikasi
- Protokol komunikasi berbasis HTTP/HTTPS standar.
- Setiap pengiriman data mutasi (POST) wajib menyertakan token header `X-CSRFToken`.
- Dynamic QR menggunakan token HMAC-SHA256 dengan slot waktu per 15 detik.
- Pertukaran data interaktif menggunakan fragmen HTML (HTMX partials) dengan `Content-Type: text/html`.

---

## 5. Persyaratan Non-Fungsional

*Kebutuhan Non-Fungsional mendefinisikan seberapa baik, seberapa cepat, seberapa aman, dan seberapa andal sistem menjalankan fungsinya (mengacu pada ISO/IEC 25010).*

| ID | Parameter Kualitas (ISO 25010) | Kebutuhan Non-Fungsional | Kriteria / Target Terukur | Prioritas | Keterangan & Justifikasi Status Non-Fungsional |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-001** | Kecepatan Server (*Latency*) | Server harus merespons permintaan halaman atau pembaruan status absensi secara sangat cepat. | Waktu respons server di bawah **200 milidetik** ($< 200\text{ ms}$). | **Penting** | **Non-Fungsional (Kinerja):** Menentukan standar kecepatan loading server, bukan menambah tombol/fitur baru. |
| **NFR-002** | Kehematan Kuota Jaringan | Ukuran data yang dikirim antar-halaman harus sangat ringan agar hemat kuota internet siswa di lapangan. | Ukuran pertukaran fragmen HTML di bawah **5 Kilobyte** ($< 5\text{ KB}$) per klik. | **Penting** | **Non-Fungsional (Efisiensi Sumber Daya):** Menjamin sistem tidak boros kuota saat digunakan di luar ruangan. |
| **NFR-003** | Kecepatan Deteksi AI | Pemindaian wajah di kamera ponsel harus berjalan mulus tanpa membuat tampilan layar macet/patah-patah. | Kecepatan baca model wajah di bawah **100 milidetik per frame** ($< 100\text{ ms}$). | **Wajib** | **Non-Fungsional (Kinerja Komputasi Klien):** Standar kelancaran kerja modul kecerdasan buatan di ponsel pengguna. |
| **NFR-004** | Kemandirian Tanpa Internet Publik | File model AI wajah harus disimpan langsung di server lokal sekolah tanpa tergantung server Google/pihak ketiga. | $100\%$ file model AI dimuat dari server lokal (`/static/models/`). | **Wajib** | **Non-Fungsional (Ketersediaan Sistem):** Menjamin fungsi deteksi wajah tetap menyala walau internet sekolah sedang lambat. |
| **NFR-005** | Responsif di Semua Layar | Tampilan antarmuka harus otomatis menyesuaikan diri dengan rapi di layar HP kecil, tablet, hingga laptop. | Tampilan tidak rusak pada ukuran layar HP 360 px hingga desktop lebar. | **Wajib** | **Non-Fungsional (Kenyamanan Tampilan):** Menjamin kenyamanan visual pengguna di berbagai jenis ukuran smartphone. |
| **NFR-006** | Keamanan Data Web | Sistem harus mencegah serangan manipulasi form web (anti-CSRF) dan memblokir akses tanpa izin di sisi server. | $100\%$ form mutasi data dilindungi token keamanan CSRF dan validasi peran. | **Wajib** | **Non-Fungsional (Keamanan Aplikasi):** Standar perlindungan sistem web dari pembobolan atau pemalsuan form online. |
| **NFR-007** | Ketahanan Verifikasi Wajah | Sistem tidak boleh percaya begitu saja pada hasil di HP siswa; keaslian wajah wajib dihitung ulang di server sekolah. | Nilai batas toleransi kemiripan wajah di server diatur ketat ($\le 0{,}60$). | **Wajib** | **Non-Fungsional (Keamanan Biometrik):** Standar kebal manipulasi agar siswa pintar tidak bisa memanipulasi kodingan di browsernya. |
| **NFR-008** | Privasi Data Siswa | Foto wajah dan berkas foto surat dokter/sakit tidak boleh bisa dilihat atau diunduh sembarang orang di internet. | Berkas media terkunci hanya untuk akun siswa yang bersangkutan, pelatih, dan admin. | **Wajib** | **Non-Fungsional (Perlindungan Privasi):** Kepatuhan etika dan hukum terhadap perlindungan data sensitif pribadi milik anak sekolah. |
| **NFR-009** | Pencegahan Data Rangkap | Basis data harus menjamin tidak akan pernah ada data presensi ganda untuk siswa dan sesi yang sama. | Diterapkan aturan kunci unik (*unique constraint*) langsung di mesin database. | **Wajib** | **Non-Fungsional (Keandalan Basis Data):** Menjaga konsistensi data dari risiko klik ganda saat koneksi internet tersendat. |
| **NFR-010** | Keamanan Riwayat Historis | Jadwal sesi latihan yang sudah pernah dihadiri siswa tidak boleh bisa dihapus sembarangan secara permanen. | Penghapusan data sesi yang memiliki absensi diblokir sistem (*Protected Delete*). | **Wajib** | **Non-Fungsional (Keandalan Audit):** Mencegah hilangnya arsip resmi kehadiran eskul yang menjadi bukti nilai di rapor sekolah. |
| **NFR-011** | Kenyamanan Keterbacaan Warna | Kontras teks warna merah silat dan aksen emas harus tajam dan mudah dibaca meski di bawah sinar matahari. | Memenuhi standar rasio kontras resmi minimal $4{,}5:1$ (standar dunia WCAG 2.1 AA). | **Penting** | **Non-Fungsional (Kenyamanan Penglihatan):** Menjamin pelatih di lapangan terbuka tidak kesulitan membaca teks di layar HP. |
| **NFR-012** | Ketahanan Saat Kamera Gagal | Jika kamera HP rusak atau izin kamera diblokir pengguna, aplikasi tidak boleh langsung *error/blank/crash*. | Muncul pesan ramah dalam waktu $< 0{,}5$ detik dan tombol presensi alternatif otomatis aktif. | **Wajib** | **Non-Fungsional (Ketahanan Error):** Sistem mampu menangani kegagalan perangkat fisik pengguna secara tenang dan elegan. |
| **NFR-013** | Kerapian Struktur Kode | Kode program harus terbagi rapi ke modul-modul independen (akun, anggota, jadwal, presensi). | Struktur proyek terbagi rapi ke folder aplikasi modular Django. | **Penting** | **Non-Fungsional (Kemudahan Perawatan):** Mempermudah developer/adik kelas yang nantinya akan melanjutkan pengembangan aplikasi. |
| **NFR-014** | Anti Titip Absen (Token QR) | Kode QR absensi harus otomatis hangus jika sudah difoto atau disebarkan lewat chat WA lebih dari 15 detik. | Kode QR berganti tiap 15 detik dan token yang kadaluwarsa langsung ditolak. | **Wajib** | **Non-Fungsional (Keandalan Keamanan Token):** Mencegah kecurangan siswa yang menitipkan foto kode QR kepada temannya di luar dojo. |

---

## 6. Persyaratan Data dan Aturan Bisnis

### 6.1 Entitas Data Utama
1. **User:** Akun pengguna sistem (UUID, username, email, password hash, role: `ADMIN`/`PELATIH`/`ANGGOTA`, avatar, phone_number, is_active).
2. **AnggotaProfile:** Profil pesilat (relasi 1-to-1 ke User, NISN unik, kelas, jenis kelamin, tanggal lahir, nama/kontak wali, sabuk_id, kategori_id, face_descriptor 128D).
3. **PelatihProfile:** Profil instruktur (relasi 1-to-1 ke User, nomor registrasi, tingkatan pendekar, spesialisasi, sertifikasi SK).
4. **TingkatSabuk:** Master sabuk (nama sabuk, urutan tingkat, warna hex, min_kehadiran_ukt persentase, deskripsi).
5. **KategoriTanding:** Master cabang silat (nama: Tanding Putra/Putri, Seni Tunggal/Ganda/Regu, kelas tanding).
6. **JadwalLatihan:** Template jadwal mingguan (hari indeks 0-6, jam mulai, jam selesai, lokasi, koordinat latitude/longitude, radius toleransi meter, is_aktif).
7. **SesiLatihan:** Instansiasi latihan harian (tanggal, jam buka, jam tutup, pelatih_id, status: `TERJADWAL`/`DIBUKA`/`SELESAI`/`BATAL`, tipe_sesi, materi_latihan, qr_secret_salt, total_hadir).
8. **Presensi:** Transaksi kehadiran pesilat (sesi_id, anggota_id, status: `HADIR`/`IZIN`/`SAKIT`/`ALPA`, metode: `FACE_SCAN`/`QR_DYNAMIC`/`MANUAL_PELATIH`, waktu_presensi, bukti_foto_url, catatan_alasan, is_verified, verified_by).
9. **RiwayatSabuk:** Portofolio perjalanan sabuk pesilat (anggota_id, sabuk_lama, sabuk_baru, tanggal_ujian, hasil_ujian, catatan_teknis, penguji_id).

### 6.2 Aturan Bisnis (Business Rules)
1. **Satu Akun Satu Peran Utama:** Setiap pengguna hanya memiliki satu peran aktif (`ADMIN`, `PELATIH`, atau `ANGGOTA`).
2. **Keunikan Absensi:** Satu anggota hanya diperbolehkan memiliki tepat satu record absensi per sesi latihan.
3. **Siklus Status Presensi:** Status yang sah adalah `HADIR`, `IZIN`, `SAKIT`, dan `ALPA`.
4. **Siklus Status Sesi:** Sesi hanya dapat menerima presensi mandiri jika berstatus `DIBUKA`.
5. **Ambang Kemiripan Wajah:**
   - Di sisi browser (klien), kecocokan diakui jika jarak Euclidean $\le 0{,}58$.
   - Di sisi server, verifikasi ditolak jika jarak Euclidean $> 0{,}60$.
6. **Kedaluwarsa Dynamic QR:** Token QR berganti otomatis setiap 15 detik; toleransi keterlambatan transmisi jaringan yang diterima server maksimal $\pm 1$ slot waktu (15 detik).
7. **Ambang Kelayakan UKT:** Kelayakan kenaikan tingkat dihitung dari perbandingan kehadiran aktual terhadap ambang batas sabuk terkait (nilai konfigurasi default basis data adalah $75\%$, dapat disesuaikan hingga $80\%$ sesuai perguruan).
8. **Perlindungan Arsip Bersejarah:** Data sesi latihan yang sudah memiliki data absensi anggota dilindungi dari penghapusan permanen (`PROTECT`).

---

## 7. Kriteria Penerimaan dan Pengujian

| ID | Skenario Pengujian | Langkah / Kondisi Uji | Hasil yang Diharapkan |
| :--- | :--- | :--- | :--- |
| **AT-001** | Login Berhasil | Pengguna memasukkan username dan kata sandi yang valid. | Masuk ke sistem dan diarahkan ke dashboard sesuai perannya masing-masing. |
| **AT-002** | Otorisasi Hak Akses | Pesilat mencoba membuka URL halaman administrasi pelatih/admin. | Server mengembalikan status 403 Forbidden atau mengarahkan kembali ke beranda pesilat. |
| **AT-003** | Absen Wajah Cocok | Siswa memindai wajah dengan descriptor yang mirip di bawah ambang batas $\le 0{,}58$. | Presensi tercatat HADIR satu kali, foto bukti tersimpan, dan muncul notifikasi sukses. |
| **AT-004** | Wajah Orang Lain Ditolak | Siswa mencoba memindai wajah orang lain yang tidak sesuai dengan data acuan akunnya. | Sistem menolak presensi dengan notifikasi "Wajah tidak cocok, verifikasi gagal". |
| **AT-005** | Pendaftaran Wajah Baru | Siswa baru yang belum punya data wajah melakukan pendaftaran pertama kali. | Sistem memvalidasi sesi dan menyimpan vektor descriptor wajah sebagai acuan permanen. |
| **AT-006** | Blokir Presensi Ganda | Siswa yang sudah absen mencoba melakukan pemindaian wajah ulang pada sesi yang sama. | Sistem menolak dan menampilkan pesan bahwa siswa sudah tercatat hadir sebelumnya. |
| **AT-007** | Quick Toggle Pelatih | Pelatih mengklik tombol HADIR/IZIN/SAKIT pada baris tabel anggota. | Status anggota langsung terbarui seketika (*zero reload*) dan counter hadir bertambah. |
| **AT-008** | Pengajuan Izin & Foto | Siswa mengunggah alasan dan foto surat dokter saat tidak bisa hadir. | Pengajuan tersimpan dengan status IZIN/SAKIT menunggu konfirmasi pelatih. |
| **AT-009** | Validasi Dynamic QR | Siswa memindai kode QR yang sudah lewat dari 30 detik (tangkapan layar dari teman). | Sistem menolak token karena telah kedaluwarsa (*Anti-Replay Protection*). |
| **AT-010** | Unduh Laporan | Admin mengklik tombol ekspor laporan periode bulanan. | File Excel (.xlsx) dan PDF resmi berhasil terunduh dengan data yang rapi dan sesuai filter. |
| **AT-011** | Kalkulasi Syarat UKT | Siswa dengan kehadiran $85\%$ membuka menu profil sabuk (syarat $75\%$). | Indikator menunjukkan label hijau "Memenuhi Syarat Mengikuti Ujian Sabuk". |
| **AT-012** | Uji Tampilan Mobile | Aplikasi dibuka pada browser smartphone Android dengan lebar layar 375 px. | Tampilan responsif, navigasi bawah tampil rapi, dan tombol mudah ditekan ibu jari. |
| **AT-013** | Perlindungan CSRF | Request POST dikirim tanpa token keamanan `X-CSRFToken`. | Server Django langsung menolak request dengan kode HTTP 403 CSRF Failed. |
| **AT-014** | Proteksi Hapus Sesi | Admin mencoba menghapus sesi latihan yang sudah memiliki data kehadiran pesilat. | Penghapusan ditolak sistem karena data terikat perlindungan integritas (*Protected*). |

---

## 8. Batasan, Asumsi, dan Ketergantungan

### 8.1 Batasan
1. **Pencahayaan Kamera:** Akurasi pengenalan wajah biometrik sangat bergantung pada pencahayaan lingkungan latihan dan kebersihan lensa kamera ponsel.
2. **Konektivitas Transaksi:** Meskipun file AI di-load secara lokal di browser, proses konfirmasi absensi HADIR tetap memerlukan koneksi jaringan (LAN sekolah atau data internet seluler) untuk berkomunikasi dengan server Django.

### 8.2 Asumsi
1. Seluruh pelatih dan siswa telah memiliki akun login unik sebelum sesi latihan resmi dimulai.
2. Sesi latihan harus dibuka terlebih dahulu oleh pelatih penanggung jawab agar presensi mandiri siswa dapat diterima.

### 8.3 Ketergantungan & Rekomendasi
1. Ambang batas kehadiran UKT ditetapkan default pada nilai **75%** di basis data, namun antarmuka admin menyediakan opsi penyesuaian fleksibel hingga **80%** sesuai kebijakan perguruan silat.
2. Proses pendaftaran wajah pertama (*enrollment*) dianjurkan dilakukan dengan verifikasi tatap muka bersama pelatih guna menjamin keaslian pemilik wajah.

---

## 9. Matriks Ketertelusuran

| Dokumen Sumber | Bagian Sumber | Cakupan pada Dokumen SRS |
| :--- | :--- | :--- |
| **PRD SilatTrack v1.1.0** | §2 User Personas & Roles | FR-001 s.d. FR-007 (Manajemen Pengguna & RBAC) |
| **PRD SilatTrack v1.1.0** | §3.1 Auth & Users | FR-001 s.d. FR-005, NFR-006, NFR-008 |
| **PRD SilatTrack v1.1.0** | §3.2 Schedule & Sessions | FR-022 s.d. FR-026 (Sesi & Materi Latihan) |
| **PRD SilatTrack v1.1.0** | §3.3 Multi-Method Attendance | FR-008 s.d. FR-021, FR-033, FR-034, NFR-003, NFR-007 |
| **PRD SilatTrack v1.1.0** | §3.4 Gamification & Belt Tracking | FR-029 s.d. FR-032 (Sabuk, Kelayakan UKT, Streak) |
| **PRD SilatTrack v1.1.0** | §3.5 Rekapitulasi & Pelaporan | FR-027, FR-028 (Dashboard & Ekspor Excel/PDF) |
| **PRD SilatTrack v1.1.0** | §4 Non-Functional Requirements | NFR-001 s.d. NFR-014 |
| **ERD & Data Dictionary** | Spesifikasi Model Data & Relasi | Bagian 6 (Entitas, Constraint Unik, Protected Delete) |
| **TDD SilatTrack v1.1.0** | §1-5 Arsitektur DATH & M3 | Bagian 2, Bagian 4.3 (Alpine, HTMX, Tailwind M3) |

---

## Lampiran A. Glosarium
- **DATH Stack:** Arsitektur modern monolitik yang menggabungkan Django, Alpine.js, Tailwind CSS, dan HTMX.
- **Descriptor Wajah:** Vektor numerik array 128 dimensi yang merepresentasikan fitur unik kontur wajah seseorang.
- **Euclidean Distance:** Formula perhitungan jarak geometris antara dua vektor numerik untuk mengukur tingkat kemiripan wajah. Semakin kecil angkanya, semakin identik wajah tersebut.
- **Dynamic Rolling QR:** Kode QR beranimasi yang token tanda tangannya berganti otomatis mengikuti slot waktu temporal untuk mencegah foto dibagikan ke siswa lain.
- **Geofencing:** Validasi radius toleransi jarak fisik perangkat terhadap koordinat lapangan latihan menggunakan GPS.
- **HTML-over-the-Wire:** Pola arsitektur di mana server mengirimkan potongan HTML siap pakai ke peramban, alih-alih mengirim JSON mentah yang harus di-render frontend.
- **UKT:** Ujian Kenaikan Tingkat sabuk dalam seni bela diri pencak silat.

---

## Lampiran B. Catatan Klarifikasi
Dokumen versi 1.1 ini telah menyempurnakan klasifikasi kebutuhan dengan memisahkan batasan arsitektural teknis ke kelompok batasan implementasi non-fungsional, melengkapi keterangan justifikasi pada setiap butir kebutuhan fungsional dan non-fungsional, serta menstandarkan skala prioritas menjadi **Wajib**, **Penting**, dan **Opsional** agar mudah dimengerti oleh seluruh pihak.
