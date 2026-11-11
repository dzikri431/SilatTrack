# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## SilatTrack: Sistem Absensi dan Manajemen Ekstrakurikuler Pencak Silat

| Informasi Dokumen | Keterangan |
| :--- | :--- |
| **Versi Dokumen** | 1.3 |
| **Tanggal Pembaruan** | 09 November 2026 |
| **Status** | Spesifikasi Kebutuhan Resmi (Final Production Release) |
| **Dokumen Acuan** | PRD SilatTrack v1.3.0, ERD & Data Dictionary v1.3.0, Architectural & Technical Design Document (TDD) |

---

### Riwayat Perubahan Dokumen
| Versi | Tanggal | Deskripsi Perubahan |
| :--- | :--- | :--- |
| 1.0 | 12-10-2026 | Penyusunan awal draf SRS berdasarkan PRD, ERD, dan dokumen arsitektur awal. |
| 1.1 | 03-11-2026 | Penyempurnaan tabel Kebutuhan Fungsional (FR) dan Non-Fungsional (NFR): penambahan kolom keterangan & justifikasi rekayasa perangkat lunak, standardisasi skala prioritas menjadi **Wajib**, **Penting**, dan **Opsional**, serta penegasan batasan arsitektur perangkat lunak. |
| 1.2 | 09-11-2026 | Penambahan spesifikasi fitur Enterprise: Multi-Sekolah (*Multi-School Support*), Tanda Tangan Cetak Laporan Kustom, Validasi Format NISN 10 Digit Kemdikbudristek, Sesi Latihan Fleksibel & Alur Persetujuan (*Approval Workflow*) oleh Admin, Pengajuan Hapus Anggota Terkontrol, Audit Trail Snapshot & Euclidean Distance Biometrik, Portal Transparansi Wali Murid Tanpa Login, Kartu Tanda Anggota (KTA) Digital, serta Dokumentasi Foto Sesi. |
| 1.3 | 09-11-2026 | Penambahan spesifikasi fitur Branding & Kredensial Resmi: ID Card Pelatih & Anggota dengan pembatasan hak cetak (RBAC print restriction: anggota view-only, admin/pelatih can print), Sertifikat Penghargaan/Kompetensi resmi berbingkai silat dan dual logo landscape A4, Model Identitas Perguruan Silat (`Perguruan`) global, serta Dual-Logo Kop Surat pada Laporan Presensi dengan modal kustomisasi live upload/URL dan opsi simpan permanen ke basis data. |

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
- [Lampiran B. Catatan Rilis](#lampiran-b-catatan-rilis)

---

## 1. Pendahuluan

### 1.1 Tujuan
Dokumen *Software Requirements Specification* (SRS) ini menetapkan seluruh kebutuhan fungsional, kebutuhan non-fungsional, antarmuka sistem, spesifikasi data, serta kriteria penerimaan pengujian untuk **SilatTrack**. Dokumen ini menjadi pedoman utama bagi pengembang perangkat lunak, penguji mutu (*QA*), pembina eskul, pelatih, dan pihak manajemen sekolah dalam membangun, memelihara, serta menguji kesesuaian sistem.

### 1.2 Ruang Lingkup
**SilatTrack** adalah sistem aplikasi web modern responsif (PWA-ready) yang dirancang khusus untuk manajemen kehadiran dan keaktifan ekstrakurikuler pencak silat multi-sekolah. Lingkup sistem mencakup:
- Autentikasi berbasis peran (*Role-Based Access Control* / RBAC): Admin/Pembina, Pelatih/Coach, Anggota/Pesilat, dan Portal Wali Murid.
- Pengelolaan multi-sekolah dengan kustomisasi data penandatangan resmi kepala sekolah dan NIP.
- Standarisasi NISN 10 digit angka resmi Kemdikbudristek untuk sinkronisasi nilai e-Rapor.
- Pengelolaan jadwal rutin mingguan dan sesi latihan fleksibel mandiri dengan alur persetujuan (*approval workflow*) oleh Admin.
- Presensi multi-metode dengan *AI Face Recognition* (face-api.js) on-device sebagai metode utama, dilengkapi audit trail foto snapshot dan metrik Euclidean distance, didukung presensi manual pelatih dan *Dynamic Rolling QR Code*.
- Mekanisme pengamanan data anggota melalui workflow pengajuan hapus anggota terkontrol.
- Portal transparansi publik untuk orang tua/wali murid berbasis NISN dan tanggal lahir tanpa keharusan membuat akun login.
- Pembuatan Kartu Tanda Anggota (KTA) Digital pesilat dengan barcode/QR ID.
- Dashboard visual, evaluasi kelayakan Ujian Kenaikan Tingkat (UKT), penghitungan *attendance streak*, serta ekspor laporan resmi (PDF Print bersurat resmi dan Excel .xlsx).

### 1.3 Dokumen Acuan
1. *Product Requirements Document* (PRD) SilatTrack v1.2.0.
2. *Entity Relationship Diagram* (ERD) & *Data Dictionary* SilatTrack v1.2.0.
3. *Architectural & Technical Design Document* (TDD) SilatTrack.

### 1.4 Konvensi dan Definisi Prioritas
Setiap kebutuhan fungsional diberi kode unik (**FR-xxx**) dan kebutuhan non-fungsional (**NFR-xxx**). Skala prioritas diklasifikasikan ke dalam 3 tingkatan lugas:
1. **Wajib:** Kebutuhan mutlak (*core system*). Sistem tidak dapat dirilis atau dinyatakan berfungsi tanpa pemenuhan fitur ini.
2. **Penting:** Kebutuhan bernilai tinggi yang sangat dianjurkan untuk efisiensi operasional dan kenyamanan, namun sistem masih dapat berjalan sementara waktu jika ditunda.
3. **Opsional:** Fitur pendukung/pelengkap (*nice-to-have*) yang memperkaya pengalaman pengguna.

---

## 2. Gambaran Umum Sistem

### 2.1 Perspektif Produk
SilatTrack dibangun menggunakan paradigma arsitektur **HTML-over-the-Wire / Modern Monolith (DATH Stack)**:
- **Django 5.2:** Menangani routing URL, autentikasi, aturan bisnis, ORM basis data, dan rendering komponen HTML server-side.
- **HTMX 2:** Melakukan pertukaran fragmen HTML secara instan (*partial DOM swap*) tanpa *full page reload*.
- **Alpine.js 3:** Menangani interaktivitas mikro di sisi peramban (kontrol stream kamera webcam, pewaktu kode QR, dan state modal dialog).
- **Tailwind CSS & Google Material Design 3 (M3):** Menyediakan sistem tata letak visual bertema Silat Crimson (`#8A1C14`) dan Brass/Gold (`#7D5800`).
- **face-api.js:** Menjalankan inferensi pendeteksian wajah dan ekstraksi *descriptor* 128 dimensi langsung di browser klien menggunakan WebGL/TensorFlow.js.
- **PostgreSQL / SQLite:** Mesin penyimpanan data relasional yang ternormalisasi (3NF).

### 2.2 Kelas Pengguna dan Hak Akses
| Peran | Deskripsi & Kemampuan Utama |
| :--- | :--- |
| **Admin / Pembina Eskul** | Memantau seluruh aktivitas eskul lintas sekolah mitra; mengelola master data sekolah (nama sekolah, NPSN, kop, pejabat penandatangan); mengelola akun pengguna; menyetujui/menolak usulan jadwal dan sesi latihan; menyetujui/menolak pengajuan hapus pesilat; mengaudit bukti foto absensi biometrik; serta mencetak laporan presensi resmi ber-kop sekolah. |
| **Pelatih / Instruktur** | Mengusulkan jadwal latihan; membuat sesi latihan rutin atau ad-hoc fleksibel; membuka dan menutup sesi presensi; mengoperasikan pemindai wajah AI di lapangan; menampilkan Dynamic QR Code; melakukan *quick toggle* kehadiran (Hadir/Izin/Sakit/Alpa); mengunggah foto dokumentasi latihan; memvalidasi surat izin/sakit; mengajukan mutasi/penghapusan pesilat; dan mencatat riwayat kenaikan sabuk. |
| **Anggota / Pesilat** | Melakukan registrasi awal wajah (*face enrollment*); absensi mandiri via pemindai wajah atau QR Code; mengunduh Kartu Tanda Anggota (KTA) Digital; mengajukan permohonan izin/sakit beserta lampiran foto; memantau riwayat presensi, *attendance streak*, dan syarat kelayakan UKT. |
| **Orang Tua / Wali Murid** | Mengakses Portal Transparansi Wali Murid secara instan tanpa akun login, cukup dengan memasukkan 10 digit NISN dan tanggal lahir anak untuk memantau status keaktifan dan kehadiran real-time. |

### 2.3 Lingkungan Operasional
- **Sisi Klien:** Peramban web modern (*Google Chrome, Apple Safari, Mozilla Firefox, Microsoft Edge*) pada smartphone (resolusi target 360–430 px), tablet, maupun PC desktop. Perangkat membutuhkan modul kamera fisik dan izin akses *webcam*.
- **Penyajian AI Lokal:** Seluruh bobot model neural network disajikan dari direktori lokal server (`/static/models/`) agar proses pembacaan wajah dapat berjalan mandiri tanpa ketergantungan API pihak ketiga.
- **Sisi Server:** Python 3.10+ dengan runtime Django 5.2 yang berkomunikasi melalui HTTP/HTTPS dengan basis data relasional.

### 2.4 Batasan Desain dan Implementasi
1. Pola aplikasi mengutamakan *Zero JavaScript Build Fatigue* tanpa framework SPA berat (React/Vue/Angular).
2. Tampilan antarmuka patuh pada token resmi Google Material Design 3 (Top App Bar, Navigation Bar Mobile, Navigation Rail Desktop, M3 Cards, dan FAB).
3. Deteksi dan ekstraksi wajah dilakukan di peramban klien, namun **verifikasi akhir wajib divalidasi ulang di server** (*Zero Client Trust*).

---

## 3. Persyaratan Fungsional

| ID | Area / Modul | Kebutuhan Fungsional | Prioritas | Keterangan & Justifikasi Status Fungsional |
| :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Autentikasi | Sistem menyediakan formulir dan mekanisme login terpisah untuk peran ADMIN, PELATIH, dan ANGGOTA. | **Wajib** | **Layanan Pengguna:** Aksi verifikasi kredensial pengguna dan inisialisasi sesi login aman. |
| **FR-002** | Otorisasi / RBAC | Sistem membatasi akses menu, aksi tombol, dan tampilan data sesuai peran aktif pengguna. | **Wajib** | **Logika Hak Akses:** Menjamin isolasi data dan wewenang pengguna berdasarkan peran. |
| **FR-003** | Manajemen Sesi | Sistem menyediakan mekanisme pembuatan sesi login aktif, pelacakan sesi, dan pemutusan sesi (*logout*). | **Wajib** | **Siklus Akun:** Mengontrol siklus hidup otentikasi pengguna di sistem. |
| **FR-004** | Manajemen Pengguna | Admin dapat membuat, melihat, mengedit, dan menonaktifkan akun pelatih maupun anggota eskul. | **Wajib** | **Operasi CRUD Pengguna:** Fitur pengelolaan akun terpusat oleh Admin/Pembina. |
| **FR-005** | Profil Pengguna | Sistem menyimpan dan menampilkan data identitas dasar, nomor kontak WhatsApp, status aktif, dan foto profil. | **Wajib** | **Pengelolaan Profil:** Layanan penyimpanan dan pembaruan informasi profil pengguna. |
| **FR-006** | Profil Anggota | Sistem menyimpan data pesilat: NISN 10 digit, sekolah, kelas, jenis kelamin, tanggal lahir, nama/kontak wali, sabuk, dan kategori tanding. | **Wajib** | **Entitas Pesilat:** Parameter administrasi pesilat untuk keperluan eskul dan sinkronisasi sekolah. |
| **FR-007** | Profil Pelatih | Sistem menyimpan nomor registrasi lisensi, tingkatan pendekar, keahlian khusus, dan nomor SK kepelatihan. | **Penting** | **Entitas Pelatih:** Rekam legalitas pelatih sebagai instruktur resmi dan penguji UKT. |
| **FR-008** | Ekstraksi Biometrik | Sistem menyalakan kamera, mendeteksi kontur wajah, dan mengekstraksi vektor embedding 128 dimensi via peramban. | **Wajib** | **Pemrosesan Masukan Citra:** Mengonversi data stream kamera menjadi representasi numerik. |
| **FR-009** | Registrasi Wajah Awal | Sistem menyediakan alur pendaftaran wajah awal (*face enrollment*) bagi pesilat baru dan menyimpan vektor referensi. | **Wajib** | **Registrasi Data Acuan:** Merekam pola biometrik acuan pesilat ke basis data. |
| **FR-010** | Pencocokan Wajah Klien | Peramban membandingkan pola wajah dari kamera dengan data acuan milik siswa menggunakan perhitungan jarak Euclidean. | **Wajib** | **Komparasi Lokal:** Memberikan visual feedback instan di ponsel siswa saat wajah terdeteksi. |
| **FR-011** | Deteksi Kestabilan | Sistem menahan kamera beberapa detik hingga posisi wajah diam dan stabil sebelum mengirim presensi secara otomatis. | **Wajib** | **Logika Antarmuka:** Menghindari pengiriman foto kabur atau deteksi wajah parsial. |
| **FR-012** | Validasi Wajah Server | Server menghitung ulang jarak Euclidean kemiripan wajah ($\le 0{,}60$) sebelum mengesahkan kehadiran. | **Wajib** | **Verifikasi Server (*Zero Client Trust*):** Menjamin kepastian biometrik dan mencegah manipulasi klien. |
| **FR-013** | Presensi Wajah Mandiri | Pesilat dapat melakukan presensi wajah mandiri hanya jika sesi latihan hari tersebut berstatus DIBUKA. | **Wajib** | **Aturan Validasi Bisnis:** Membatasi waktu presensi sesuai jam operasional latihan. |
| **FR-014** | Presensi Manual Mandiri | Siswa dapat mengisi formulir klaim presensi darurat mandiri jika kamera handphone bermasalah atau rusak fisik. | **Wajib** | **Jalur Cadangan:** Menjaga hak kehadiran siswa saat terkendala perangkat fisik. |
| **FR-015** | Pencatatan Cepat Pelatih | Pelatih dapat langsung mengubah status pesilat (HADIR, IZIN, SAKIT, ALPA) dengan tombol *quick toggle* satu klik. | **Wajib** | **Operasional Lapangan:** Mempercepat kerja pelatih saat mengabsen banyak anggota di dojo. |
| **FR-016** | Presensi Massal | Pelatih dapat menandai seluruh anggota hadir serentak (*bulk action*) untuk mempercepat administrasi latihan besar. | **Penting** | **Otomasi Operasional:** Efisiensi pencatatan presensi saat kegiatan massal. |
| **FR-017** | Presensi Dynamic QR | Sistem menyediakan alternatif presensi dengan memindai kode QR bertanda tangan HMAC yang ditampilkan pelatih. | **Penting** | **Metode Alternatif:** Mengurai antrean saat banyak siswa hadir bersamaan. |
| **FR-018** | Pencatatan Info Presensi | Sistem merekam metode presensi yang digunakan, stempel waktu, status, bukti verifikasi, dan IP/perangkat. | **Wajib** | **Audit Trail Transaksi:** Rekam jejak presensi menyeluruh untuk keperluan audit kehadiran. |
| **FR-019** | Cegah Presensi Ganda | Sistem otomatis menolak percobaan presensi lebih dari satu kali untuk siswa yang sama pada sesi yang sama. | **Wajib** | **Integritas Basis Data:** Menerapkan unique constraint `(sesi_id, anggota_id)`. |
| **FR-020** | Pengajuan Izin / Sakit | Siswa dapat mengajukan izin/sakit dengan menyertakan keterangan alasan dan mengunggah foto surat dokter/keterangan orang tua. | **Wajib** | **Formulir & Unggah Berkas:** Sarana permohonan ketidakhadiran berdokumen sah. |
| **FR-021** | Persetujuan Izin / Sakit | Pelatih dapat meninjau lampiran foto surat izin/sakit dan memutuskan untuk menyetujui (*Approve*) atau menolak (*Reject*). | **Wajib** | **Alur Persetujuan Dokumen:** Wewenang verifikasi surat keterangan ketidakhadiran oleh pelatih. |
| **FR-022** | Buat Sesi Latihan | Pelatih dapat membuat sesi latihan baru dengan memilih tipe: Latihan Reguler, TC Kejuaraan, UKT, atau Tes Fisik. | **Wajib** | **Inisialisasi Sesi:** Membuat wadah transaksi presensi latihan harian. |
| **FR-023** | Buka dan Tutup Sesi | Pelatih dapat mengubah status sesi latihan: dari TERJADWAL $\rightarrow$ DIBUKA $\rightarrow$ SELESAI atau BATAL. | **Wajib** | **Pengendali Alur Latihan:** Mengatur periode aktif pembukaan absensi siswa. |
| **FR-024** | Penyimpanan Data Sesi | Sistem mencatat tanggal, jam operasional aktual, pelatih penanggung jawab, materi ajar, dan total kehadiran. | **Wajib** | **Perekaman Kegiatan:** Dokumentasi rekam jejak pelaksanaan latihan ekstrakurikuler. |
| **FR-025** | Kelola Jadwal Rutin | Admin dan Pelatih dapat menyusun jadwal rutin mingguan (hari, jam mulai/selesai, lokasi dojo, dan radius toleransi). | **Wajib** | **Master Jadwal Mingguan:** Templat jadwal tetap yang memandu operasional eskul. |
| **FR-026** | Catat Materi Latihan | Pelatih dapat mencatat rangkuman menu materi yang diajarkan (kuda-kuda, pasang, jurus tunggal baku, fisik, sambung). | **Wajib** | **Jurnal Kurikulum Eskul:** Dokumentasi capaian materi teknis silat setiap pertemuan. |
| **FR-027** | Grafik & Statistik Dashboard | Sistem menyajikan statistik jumlah hadir dan grafik persentase kehadiran bulanan secara interaktif. | **Wajib** | **Visualisasi Eksekutif:** Memudahkan pembina dan pelatih membaca tren kehadiran eskul. |
| **FR-028** | Ekspor Laporan Excel/PDF | Sistem menyediakan fitur ekspor rekapitulasi kehadiran pesilat ke format Excel (.xlsx) dan PDF cetak resmi. | **Wajib** | **Pelaporan Formal:** Penyajian dokumen resmi untuk nilai rapor sekolah dan evaluasi dinas. |
| **FR-029** | Master Tingkatan Sabuk | Sistem menyediakan konfigurasi hierarki sabuk (Putih s/d Hitam), kode warna HEX, dan ambang batas minimal kehadiran UKT. | **Wajib** | **Konfigurasi Standar Perguruan:** Pengaturan parameter kelayakan kenaikan tingkat. |
| **FR-030** | Catatan Riwayat Sabuk | Sistem mencatat portofolio kenaikan sabuk pesilat, tanggal ujian, penguji, predikat kelulusan, dan evaluasi teknik. | **Wajib** | **Buku Rapor Pesilat:** Rekam jejak progres prestasi pesilat dari pemula hingga pendekar. |
| **FR-031** | Cek Kelayakan UKT | Sistem menghitung otomatis persentase kehadiran pesilat terhadap ambang batas sabuk untuk menentukan kelayakan UKT. | **Wajib** | **Kalkulasi Bisnis Otomatis:** Menghindari subjektivitas dalam penentuan peserta ujian kenaikan sabuk. |
| **FR-032** | Gamifikasi (Streak & Badge) | Sistem menghitung rekor latihan tanpa bolos (*attendance streak*) dan menampilkan lencana keaktifan pada profil pesilat. | **Opsional** | **Motivasi Pesilat:** Meningkatkan semangat dan kedisiplinan berlatih pesilat muda. |
| **FR-033** | Galeri Bukti Foto Absen | Sistem menyimpan foto wajah saat verifikasi biometrik dan menampilkannya pada dashboard audit pelatih/admin. | **Wajib** | **Audit Fisik Presensi:** Memungkinkan pelatih memeriksa kembali keaslian kehadiran siswa. |
| **FR-034** | Cek Lokasi (Geofencing) | Sistem dapat memvalidasi koordinat GPS perangkat siswa berada di dalam radius toleransi lokasi latihan. | **Penting** | **Validasi Spasial:** Memastikan siswa berada di area dojo saat melakukan absensi. |
| **FR-035** | Portal Pantau Wali Murid | Sistem menyediakan antarmuka publik bagi wali murid untuk memantau status kehadiran anak secara real-time. | **Opsional** | **Keterbukaan Informasi:** Layanan transparansi bagi orang tua murid. |
| **FR-036** | Catatan Audit Perubahan | Sistem mencatat nama pelatih/admin dan stempel waktu ketika terjadi koreksi manual status presensi. | **Wajib** | **Log Integritas:** Mencegah sengketa data dan menjaga akuntabilitas koreksi absensi. |
| **FR-037** | Multi-Sekolah (*Multi-School*) | Sistem mendukung pengelolaan data master banyak sekolah mitra (`Sekolah`), mencakup NPSN, alamat, dan pejabat kepala sekolah. | **Wajib** | **Multi-Tenant Organisasi:** Memungkinkan satu aplikasi mengelola eskul silat di banyak sekolah sekaligus. |
| **FR-038** | Tanda Tangan Cetak Kustom | Sistem secara dinamis menyusun kop surat resmi dan blok tanda tangan kepala sekolah serta pelatih saat mencetak laporan presensi per sekolah. | **Wajib** | **Standarisasi Dokumen Dinas:** Menghasilkan dokumen cetak resmi yang sah dan siap ditandatangani kepala sekolah. |
| **FR-039** | Validasi NISN 10 Digit | Sistem memvalidasi bahwa setiap NISN pesilat tepat terdiri atas 10 digit angka (`^\d{10}$`) sesuai standar Kemdikbudristek. | **Wajib** | **Standardisasi Data Nasional:** Menjamin keselarasan data pesilat dengan DAPODIK dan sistem e-Rapor sekolah. |
| **FR-040** | Sesi Latihan Fleksibel | Pelatih dapat membuat sesi latihan di luar jadwal rutin dengan nama lokasi (`nama_lokasi`), jam mulai, dan jam selesai mandiri. | **Wajib** | **Fleksibilitas Operasional:** Mendukung latihan insidental, persiapan pertandingan (TC), atau latihan di lokasi khusus. |
| **FR-041** | Alur Persetujuan Sesi & Jadwal | Sistem menyediakan siklus status persetujuan (`MENUNGGU`, `DISETUJUI`, `DITOLAK`) beserta catatan arahan dari admin untuk setiap sesi dan jadwal yang diusulkan. | **Wajib** | **Tata Kelola & Otorisasi:** Memastikan seluruh kegiatan ekstrakurikuler mendapat izin resmi dari pihak pembina sekolah. |
| **FR-042** | Pengajuan Hapus Anggota Aman | Pelatih mengajukan permohonan hapus pesilat beserta alasan terinci, dan penghapusan hanya dapat dieksekusi setelah disetujui Admin. | **Wajib** | **Perlindungan Integritas Data:** Mencegah hilangnya riwayat presensi pesilat akibat kesalahan atau aksi sepihak di lapangan. |
| **FR-043** | Audit Trail Snapshot & Euclidean | Sistem menyimpan snapshot foto wajah aktual (`foto_face_scan`) dan nilai jarak Euclidean (`face_distance`) saat absensi biometrik berhasil. | **Wajib** | **Bukti Validitas Biometrik:** Menyediakan bukti empiris tingkat kemiripan wajah untuk mengeliminasi potensi kecurangan. |
| **FR-044** | Portal Wali Tanpa Login | Orang tua/wali dapat mengakses transparansi data anak cukup dengan memasukkan 10 digit NISN dan tanggal lahir tanpa akun login. | **Wajib** | **Aksesibilitas Publik:** Mempermudah orang tua tanpa membebani dengan manajemen username dan kata sandi baru. |
| **FR-045** | KTA Digital Pesilat | Sistem menghasilkan Kartu Tanda Anggota (KTA) Digital berformat rapi dengan foto, nomor identitas/QR barcode, sabuk, dan asal sekolah yang siap dicetak. | **Penting** | **Identitas Resmi Pesilat:** Kartu pengenal resmi siswa sebagai anggota sah ekstrakurikuler silat perguruan. |
| **FR-046** | Foto Dokumentasi Kegiatan Sesi | Pelatih dapat mengunggah foto dokumentasi kegiatan latihan fisik/teknik (`foto_kegiatan`) dan keterangan foto pada sesi terkait. | **Penting** | **Akuntabilitas Latihan:** Menyediakan dokumentasi visual pertanggungjawaban kegiatan eskul kepada pihak sekolah. |
| **FR-047** | ID Card Pelatih & Anggota | Sistem menghasilkan ID Card digital dua sisi berukuran standar CR80 yang memuat foto, nama, peran, nomor registrasi/NISN, asal sekolah, tingkat sabuk/spesialisasi, barcode QR verifikasi, dan stempel perguruan. | **Wajib** | **Kredensial Pengenal:** Kartu tanda pengenal resmi standar organisasi untuk pelatih dan pesilat. |
| **FR-048** | Pembatasan Cetak ID Card (RBAC) | Sistem membatasi wewenang cetak ID card; akun peran ANGGOTA hanya dapat melihat (*view-only*) kartu mereka sendiri tanpa tombol cetak, sedangkan ADMIN dan PELATIH berwenang penuh mencetak kartu. | **Wajib** | **Kontrol Otoritas Fisik:** Mencegah pencetakan mandiri liar oleh siswa dan menjaga wewenang administrasi di tangan pelatih/admin. |
| **FR-049** | Sertifikat Resmi Dual-Logo | Sistem menyediakan fitur penerbitan piagam sertifikat penghargaan/kompetensi resmi format Landscape A4 berbingkai silat klasik dengan Logo Sekolah (kiri) dan Logo Perguruan (kanan), nomor sertifikat, dan tanda tangan Kepala Sekolah serta Pelatih. | **Penting** | **Legalisasi Prestasi:** Bukti sertifikasi formal atas partisipasi atau keahlian pesilat/pelatih. |
| **FR-050** | Manajemen Identitas Perguruan | Sistem menyediakan konfigurasi terpusat data perguruan silat (`Perguruan`: nama resmi, singkatan brand, logo perguruan, semboyan, alamat, kontak) yang diterapkan secara global di navbar, login, dan kop surat. | **Wajib** | **Branding Terpusat:** Menjamin identitas organisasi perguruan silat tampil konsisten di seluruh modul sistem. |
| **FR-051** | Dual-Logo Kop Surat Laporan | Kop surat cetak laporan presensi resmi menampilkan lambang resmi Sekolah mitra di sisi kiri dan lambang resmi Perguruan Silat di sisi kanan dengan teks informasi dinamis sekolah di tengah. | **Wajib** | **Standar Dokumen Bersama:** Memenuhi etika tata persuratan kemitraan antara perguruan beladiri dan institusi sekolah. |
| **FR-052** | Modal Kustomisasi Logo Laporan | Sistem menyediakan antarmuka modal interaktif pada cetak laporan untuk menguji atau mengubah logo sekolah dan perguruan secara langsung via unggah berkas (FileReader) atau tautan URL dengan opsi simpan permanen ke basis data. | **Penting** | **Fleksibilitas Pelaporan:** Memudahkan pelatih menyesuaikan logo kop surat seketika sebelum mencetak laporan tanpa harus masuk ke Django admin. |

---

## 4. Persyaratan Antarmuka Eksternal

### 4.1 Antarmuka Pengguna
- Mengadopsi prinsip desain Google Material Design 3 (M3) dengan warna Silat Crimson (`#8A1C14`) dan Brass Gold (`#7D5800`).
- **Destinasi Navigasi Mobile:** 4 destinasi utama pada Navigation Bar bawah (Beranda, Presensi/Scan, Jadwal, Profil) dengan indikator berbentuk pil.
- **Reticle Pemindai Wajah:** Antarmuka pemindai dilengkapi panduan reticle oval dengan 3 status warna dinamis:
  - Abu-abu: Siaga (*Standby* / Menunggu wajah).
  - Kuning: Mendeteksi dan menstabilkan wajah (*Stabilizing buffer*).
  - Hijau: Terverifikasi dan mengirimkan data (*Verified*).
- **Umpan Balik Instan:** Menggunakan komponen Snackbar M3 dengan aksi pembatalan (*undo*) jika terjadi kesalahan input.
- **Kop Surat & Cetak Dokumen:** Template cetak laporan (*Print View*) otomatis menghilangkan elemen navigasi web, mengoptimalkan tata letak kertas A4/F4 portrait, dan memuat kop dinamis serta tanda tangan kepala sekolah.

### 4.2 Antarmuka Perangkat Keras
- **Kamera Ponsel / Webcam:** Resolusi minimal 720p dengan dukungan API browser `navigator.mediaDevices.getUserMedia`.
- **Modul GPS (Opsional):** Membaca koordinat lintang/bujur melalui `navigator.geolocation` jika fitur geofencing diaktifkan pada jadwal/sesi terkait.

### 4.3 Antarmuka Perangkat Lunak & Batasan Implementasi
| Komponen | Versi Acuan | Peran dalam Sistem & Batasan Teknis |
| :--- | :--- | :--- |
| **Django** | 5.2 (Python) | Server backend monolitik, routing URL, autentikasi RBAC, middleware keamanan, dan ORM basis data. |
| **Alpine.js** | 3.x | Pengendali kamera di peramban, timer kode QR, dan state modal dialog. |
| **face-api.js** | 0.22.x | Pustaka neural network klien berbasis TensorFlow.js untuk mendeteksi wajah dan menghasilkan descriptor 128D. |
| **HTMX** | 2.x | Mesin transmisi hypermedia via request AJAX untuk pembaruan komponen DOM tanpa memuat ulang seluruh halaman (*HTML-over-the-Wire*). |
| **Tailwind CSS** | 3.x | Kerangka kerja utilitas CSS untuk styling responsif dengan token warna Material Design 3. |
| **PostgreSQL / SQLite** | PostgreSQL 15+ / SQLite 3 | Mesin sistem manajemen basis data relasional (RDBMS) dengan constraint data ketat. |
| **Penyimpanan Media** | Local / S3-compatible | Direktori penyimpanan berkas foto snapshot presensi, foto kegiatan sesi, avatar, dan surat dokter. |

### 4.4 Antarmuka Komunikasi
- Protokol komunikasi berbasis HTTP/HTTPS standar.
- Setiap pengiriman data mutasi (POST) wajib menyertakan token header `X-CSRFToken`.
- Dynamic QR menggunakan token HMAC-SHA256 yang divalidasi ke rahasia *salt* sesi latihan.
- Pertukaran data interaktif menggunakan fragmen HTML (HTMX partials) dengan `Content-Type: text/html`.

---

## 5. Persyaratan Non-Fungsional

| ID | Parameter Kualitas (ISO 25010) | Kebutuhan Non-Fungsional | Kriteria / Target Terukur | Prioritas | Keterangan & Justifikasi Status Non-Fungsional |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NFR-001** | Kecepatan Server (*Latency*) | Server harus merespons permintaan halaman atau pembaruan status absensi secara sangat cepat. | Waktu respons server di bawah **200 milidetik** ($< 200\text{ ms}$). | **Penting** | **Kinerja:** Standar kelancaran loading server saat transaksi absensi serentak. |
| **NFR-002** | Kehematan Kuota Jaringan | Ukuran data yang dikirim antar-halaman harus sangat ringan agar hemat kuota internet siswa di lapangan. | Ukuran pertukaran fragmen HTML di bawah **5 Kilobyte** ($< 5\text{ KB}$) per interaksi. | **Penting** | **Efisiensi Sumber Daya:** Menjamin kelancaran absensi saat koneksi seluler di lapangan terbatas. |
| **NFR-003** | Kecepatan Deteksi AI | Pemindaian wajah di kamera ponsel harus berjalan mulus tanpa membuat tampilan layar macet/patah-patah. | Kecepatan baca model wajah di bawah **100 milidetik per frame** ($< 100\text{ ms}$). | **Wajib** | **Kinerja Komputasi Klien:** Standar responsivitas modul kecerdasan buatan di ponsel pengguna. |
| **NFR-004** | Kemandirian Tanpa Internet Publik | File model AI wajah harus disimpan langsung di server lokal sekolah tanpa tergantung server pihak ketiga. | $100\%$ file model AI dimuat dari server lokal (`/static/models/`). | **Wajib** | **Ketersediaan Sistem:** Menjamin fungsi deteksi wajah tetap menyala walau koneksi internet luar terganggu. |
| **NFR-005** | Responsif di Semua Layar | Tampilan antarmuka harus otomatis menyesuaikan diri dengan rapi di layar HP kecil, tablet, hingga laptop. | Tampilan tidak rusak pada ukuran layar HP 360 px hingga desktop lebar. | **Wajib** | **Kenyamanan Tampilan:** Menjamin kenyamanan visual pengguna di berbagai jenis perangkat. |
| **NFR-006** | Keamanan Data Web | Sistem harus mencegah serangan manipulasi form web (anti-CSRF) dan memblokir akses tanpa izin di sisi server. | $100\%$ form mutasi data dilindungi token keamanan CSRF dan validasi peran RBAC. | **Wajib** | **Keamanan Aplikasi:** Perlindungan sistem web dari pemalsuan form online dan eksploitasi akses. |
| **NFR-007** | Ketahanan Verifikasi Wajah | Sistem tidak boleh percaya begitu saja pada hasil di HP siswa; keaslian wajah wajib dihitung ulang di server sekolah. | Nilai batas toleransi kemiripan wajah di server diatur ketat ($\le 0{,}60$). | **Wajib** | **Keamanan Biometrik (*Zero Client Trust*):** Mencegah manipulasi skrip di peramban klien. |
| **NFR-008** | Privasi Data Siswa | Foto wajah dan berkas foto surat dokter/sakit tidak boleh bisa dilihat atau diunduh sembarang orang di internet. | Berkas media dilindungi otentikasi dan otorisasi peran terkait. | **Wajib** | **Perlindungan Privasi:** Kepatuhan terhadap etika dan undang-undang perlindungan data pribadi siswa. |
| **NFR-009** | Pencegahan Data Rangkap | Basis data harus menjamin tidak akan pernah ada data presensi ganda untuk siswa dan sesi yang sama. | Diterapkan aturan kunci unik komposit `(sesi_id, anggota_id)`. | **Wajib** | **Keandalan Basis Data:** Menjaga konsistensi data dari risiko klik ganda saat koneksi internet tersendat. |
| **NFR-010** | Keamanan Riwayat Historis | Sesi latihan yang sudah pernah dihadiri siswa dilindungi dari penghapusan sembarangan. | Penghapusan data sesi yang memiliki absensi diblokir sistem (*Protected Delete*). | **Wajib** | **Keandalan Audit:** Mencegah hilangnya arsip resmi kehadiran eskul yang menjadi bukti nilai e-Rapor. |
| **NFR-011** | Kenyamanan Keterbacaan Warna | Kontras teks warna merah silat dan aksen emas harus tajam dan mudah dibaca meski di bawah sinar matahari. | Memenuhi standar rasio kontras resmi minimal $4{,}5:1$ (WCAG 2.1 AA). | **Penting** | **Kenyamanan Penglihatan:** Menjamin kemudahan membaca teks di layar HP saat di lapangan terbuka. |
| **NFR-012** | Ketahanan Saat Kamera Gagal | Jika kamera HP rusak atau izin kamera diblokir, aplikasi tidak boleh langsung *error/blank/crash*. | Muncul pesan ramah dalam waktu $< 0{,}5$ detik dan tombol presensi alternatif otomatis aktif. | **Wajib** | **Ketahanan Gangguan (*Fault Tolerance*):** Menangani kegagalan perangkat fisik pengguna secara elegan. |
| **NFR-013** | Kerapian Arsitektur Proyek | Kode program harus terbagi rapi ke modul aplikasi mandiri (accounts, members, attendance, schedule, core). | Struktur proyek terbagi rapi ke folder aplikasi modular Django. | **Penting** | **Kemudahan Perawatan (*Maintainability*):** Mempermudah kolaborasi dan pengembangan sistem jangka panjang. |
| **NFR-014** | Anti Titip Absen (Token QR) | Kode QR absensi harus otomatis kedaluwarsa jika disebarkan lewat tangkapan layar chat WA. | Kode QR ditandatangani HMAC dan divalidasi status aktif sesinya. | **Wajib** | **Keandalan Token:** Mencegah kecurangan siswa yang membagikan foto kode QR ke siswa di luar tempat latihan. |

---

## 6. Persyaratan Data dan Aturan Bisnis

### 6.1 Entitas Data Utama
1. **Sekolah:** Master institusi sekolah mitra (`id`, `nama_sekolah`, `npsn`, `alamat`, `logo_sekolah`, `nama_kepala_sekolah`, `nip_kepala_sekolah`, `jabatan_kepala_sekolah`, `is_aktif`, `created_at`).
2. **User:** Akun pengguna sistem (`id` UUID, `username`, `email`, `password`, `first_name`, `last_name`, `role`: `ADMIN`/`PELATIH`/`ANGGOTA`, `avatar`, `phone_number`, `is_active`).
3. **AnggotaProfile:** Profil pesilat (`user_id` UUID OneToOne, `nisn` 10 digit unik, `sekolah_id` FK, `kelas_sekolah`, `jenis_kelamin`, `tanggal_lahir`, `nama_wali`, `no_hp_wali`, `sabuk_saat_ini_id` FK, `kategori_fokus_id` FK, `status_keanggotaan`, `face_descriptor` 128D JSON, `face_registered_at`).
4. **PelatihProfile:** Profil instruktur (`user_id` UUID OneToOne, `nomor_registrasi` unik, `tingkatan_pendekar`, `spesialisasi`, `sertifikasi_sk`).
5. **TingkatSabuk:** Master sabuk (`id`, `nama_sabuk`, `urutan_tingkat`, `warna_hex`, `min_kehadiran_ukt` %, `deskripsi`).
6. **KategoriTanding:** Master cabang silat (`id`, `nama`, `kelas_tanding`, `catatan_teknis`).
7. **JadwalLatihan:** Template jadwal mingguan (`id`, `nama_jadwal`, `hari_indeks` 0-6, `jam_mulai`, `jam_selesai`, `nama_lokasi`, `latitude`, `longitude`, `radius_toleransi_meter`, `is_aktif`, `status_persetujuan`, `dibuat_oleh_id` FK, `disetujui_oleh_id` FK, `catatan_admin`).
8. **SesiLatihan:** Instansiasi latihan harian (`id` UUID, `jadwal_id` FK nullable, `pelatih_id` FK, `tanggal`, `jam_buka`, `jam_tutup`, `status`: `TERJADWAL`/`DIBUKA`/`SELESAI`/`BATAL`, `status_persetujuan`: `MENUNGGU`/`DISETUJUI`/`DITOLAK`, `disetujui_oleh_id` FK, `waktu_disetujui`, `catatan_persetujuan`, `tipe_sesi`, `materi_latihan`, `nama_lokasi`, `jam_mulai`, `jam_selesai`, `qr_secret_salt`, `total_hadir`, `foto_kegiatan`, `keterangan_foto`).
9. **Presensi:** Transaksi kehadiran pesilat (`id` UUID, `sesi_id` FK, `anggota_id` FK, `status`: `HADIR`/`IZIN`/`SAKIT`/`ALPA`, `metode_presensi`: `FACE_SCAN`/`QR_DYNAMIC`/`MANUAL_PELATIH`/`MANUAL_MANDIRI`/`GEOFENCE`, `waktu_presensi`, `bukti_foto`, `foto_face_scan`, `face_distance`, `catatan_alasan`, `is_verified`, `verified_by_id` FK, `user_latitude`, `user_longitude`, `ip_address`, `device_user_agent`).
10. **PengajuanHapusAnggota:** Pengajuan mutasi/hapus anggota terkontrol (`id` UUID, `anggota_id` FK, `diajukan_oleh_id` FK, `alasan`, `status`: `MENUNGGU`/`DISETUJUI`/`DITOLAK`, `disetujui_oleh_id` FK, `catatan_admin`, `created_at`, `updated_at`).
11. **RiwayatKenaikanSabuk:** Portofolio perjalanan sabuk pesilat (`id` UUID, `anggota_id` FK, `sabuk_asal_id` FK, `sabuk_baru_id` FK, `penguji_pelatih_id` FK, `tanggal_ujian`, `hasil`: `LULUS_TERPUJI`/`LULUS`/`MENGULANG`, `evaluasi_teknik`).
12. **Perguruan:** Pengaturan identitas tunggal perguruan silat (`id`, `nama_perguruan`, `singkatan`, `logo_perguruan`, `semboyan`, `alamat_pusat`, `kontak`, `created_at`, `updated_at`).

### 6.2 Aturan Bisnis (Business Rules)
1. **Satu Akun Satu Peran:** Setiap pengguna terikat pada satu peran primer (`ADMIN`, `PELATIH`, atau `ANGGOTA`).
2. **Keunikan Absensi:** Satu anggota hanya boleh memiliki tepat satu record absensi per sesi latihan (`UNIQUE (sesi_id, anggota_id)`).
3. **Format Standar NISN:** Nilai NISN wajib tepat 10 digit angka numerik. Input yang tidak sesuai format ditolak langsung oleh validator model.
4. **Alur Persetujuan Kegiatan:** Usulan jadwal dan sesi latihan di luar reguler berstatus `MENUNGGU` hingga diverifikasi dan disetujui (`DISETUJUI`) oleh Admin/Pembina.
5. **Otoritas Penghapusan Anggota:** Pelatih tidak memiliki izin langsung untuk mengeksekusi *hard delete* terhadap data siswa; pelatih wajib melalui mekanisme `PengajuanHapusAnggota` yang disetujui Admin.
6. **Ambang Kemiripan Biometrik:**
   - Di sisi peramban klien, kecocokan reticle diakui jika jarak Euclidean $\le 0{,}58$.
   - Di sisi server, verifikasi ditolak jika jarak Euclidean $> 0{,}60$.
7. **Perekaman Audit Biometrik:** Setiap presensi metode `FACE_SCAN` yang berhasil wajib menyimpan snapshot foto wajah aktual dan nilai numerik jarak kemiripan (*Euclidean distance*).
8. **Akses Portal Wali Murid:** Data profil, tingkat sabuk, streak, dan presensi siswa dapat ditampilkan di Portal Wali jika kombinasi 10 digit NISN dan tanggal lahir siswa cocok di basis data.
9. **Kop & Tanda Tangan Cetak Dinamis:** Saat laporan dicetak dengan filter sekolah tertentu, dokumen harus menyajikan nama sekolah, alamat, nama kepala sekolah, NIP, serta nama pelatih pengampu sekolah bersangkutan.
10. **Perlindungan Arsip Bersejarah:** Sesi latihan yang telah memiliki data presensi tidak dapat dihapus (`PROTECT`) demi menjaga validitas nilai e-Rapor sekolah.
11. **Otoritas Cetak ID Card (RBAC):** Tombol dan fungsionalitas cetak ID card dibatasi hanya untuk peran ADMIN dan PELATIH. Peran ANGGOTA hanya diizinkan melihat (*view-only*) ID card milik sendiri tanpa akses pencetakan fisik.
12. **Standar Dual-Logo Dokumen Cetak:** Dokumen cetak resmi (Laporan Presensi dan Sertifikat) wajib menampilkan lambang Sekolah mitra di sebelah kiri dan lambang Perguruan Silat di sebelah kanan, dengan mekanisme cadangan (*vector SVG fallback*) jika berkas belum diunggah.

---

## 7. Kriteria Penerimaan dan Pengujian

| ID | Skenario Pengujian | Langkah / Kondisi Uji | Hasil yang Diharapkan |
| :--- | :--- | :--- | :--- |
| **AT-001** | Login Berhasil | Pengguna memasukkan username dan kata sandi yang valid. | Masuk ke sistem dan diarahkan ke dashboard sesuai perannya masing-masing. |
| **AT-002** | Otorisasi Hak Akses | Pesilat mencoba membuka URL halaman administrasi pelatih/admin. | Server mengembalikan status 403 Forbidden atau mengarahkan kembali ke beranda pesilat. |
| **AT-003** | Absen Wajah Cocok & Audit | Siswa memindai wajah dengan descriptor yang mirip di bawah ambang batas $\le 0{,}58$. | Presensi tercatat HADIR, snapshot foto wajah dan nilai Euclidean distance tersimpan rapi di database. |
| **AT-004** | Wajah Orang Lain Ditolak | Siswa mencoba memindai wajah orang lain yang tidak sesuai dengan data acuan akunnya. | Sistem menolak presensi dengan notifikasi "Wajah tidak cocok, verifikasi gagal". |
| **AT-005** | Pendaftaran Wajah Baru | Siswa baru yang belum punya data wajah melakukan pendaftaran biometrik pertama kali. | Sistem memvalidasi sesi dan menyimpan vektor descriptor wajah 128 dimensi sebagai acuan permanen. |
| **AT-006** | Blokir Presensi Ganda | Siswa yang sudah absen mencoba melakukan pemindaian wajah ulang pada sesi yang sama. | Sistem menolak dan menampilkan pesan bahwa siswa sudah tercatat hadir sebelumnya. |
| **AT-007** | Quick Toggle Pelatih | Pelatih mengklik tombol HADIR/IZIN/SAKIT pada baris tabel anggota. | Status anggota langsung terbarui seketika (*zero reload*) dan counter hadir bertambah. |
| **AT-008** | Pengajuan Izin & Foto | Siswa mengunggah alasan dan foto surat dokter saat tidak bisa hadir. | Pengajuan tersimpan dengan status IZIN/SAKIT menunggu konfirmasi pelatih. |
| **AT-009** | Validasi Dynamic QR | Siswa memindai kode QR yang sudah ditutup atau tidak cocok tanda tangannya. | Sistem menolak token dan memberikan pesan error yang informatif. |
| **AT-010** | Cetak Laporan Per Sekolah | Admin memilih filter sekolah dan menekan tombol cetak laporan resmi. | Muncul halaman cetak dengan kop sekolah, nama kepala sekolah, NIP, nama pelatih, dan tabel kehadiran yang rapi. |
| **AT-011** | Validasi Format NISN | Admin/pengguna memasukkan NISN kurang dari 10 digit (misal: 8 digit). | Sistem menolak penyimpanan dan menampilkan peringatan: "NISN harus tepat 10 digit angka...". |
| **AT-012** | Persetujuan Sesi Fleksibel | Pelatih membuat sesi latihan ad-hoc; Admin membuka dashboard dan menekan tombol Setujui. | Status sesi berubah dari MENUNGGU menjadi DISETUJUI, dan sesi siap dibuka oleh pelatih. |
| **AT-013** | Pengajuan Hapus Anggota | Pelatih mengajukan mutasi/hapus pesilat; Admin meninjau dan menyetujui pengajuan tersebut. | Data pengajuan tercatat di audit log dan data pesilat dinonaktifkan/dihapus secara aman oleh Admin. |
| **AT-014** | Portal Wali Murid | Orang tua membuka portal wali, memasukkan 10 digit NISN dan tanggal lahir anak yang valid. | Terbuka halaman ringkasan kehadiran anak, persentase keaktifan, streak latihan, dan sabuk saat ini. |
| **AT-015** | Unduh KTA Digital | Pesilat atau pelatih membuka menu Kartu Anggota pada detail profil pesilat. | Tampil Kartu Tanda Anggota (KTA) Digital lengkap dengan barcode/QR ID, foto, sabuk, dan nama sekolah. |
| **AT-016** | Proteksi Hapus Sesi Bersejarah | Admin mencoba menghapus sesi latihan yang sudah memiliki data kehadiran pesilat. | Penghapusan ditolak sistem karena data terikat perlindungan integritas (*Protected Delete*). |
| **AT-017** | RBAC Cetak ID Card | Anggota login dan membuka halaman ID Card miliknya; Pelatih/Admin membuka ID Card anggota. | Pada halaman anggota, tombol cetak disembunyikan (*view-only*). Pada Admin/Pelatih, tombol "Cetak ID Card" aktif dan mencetak dua sisi kartu. |
| **AT-018** | Cetak Sertifikat Dual-Logo | Admin/Pelatih membuka halaman sertifikat anggota atau pelatih. | Muncul tampilan sertifikat formal berbingkai silat dengan Logo Sekolah (kiri) dan Logo Perguruan (kanan), nomor seri, dan tanda tangan resmi. |
| **AT-019** | Kustomisasi Logo Kop Laporan | Pengguna menekan tombol "Atur Logo Kop Surat" pada halaman cetak laporan presensi. | Terbuka modal pengaturan; pengguna dapat mengunggah file/URL logo, melihat preview instan, dan menyimpan perubahan langsung ke basis data. |

---

## 8. Batasan, Asumsi, dan Ketergantungan

### 8.1 Batasan
1. **Pencahayaan Kamera:** Akurasi pengenalan wajah biometrik sangat bergantung pada pencahayaan lingkungan latihan dan kebersihan lensa kamera.
2. **Konektivitas Transaksi:** Meskipun komputasi inferensi neural network wajah berjalan lokal di browser, proses verifikasi akhir HADIR tetap membutuhkan koneksi jaringan (LAN/WiFi/Internet) untuk berkomunikasi dengan server Django.

### 8.2 Asumsi
1. Seluruh pelatih dan siswa telah memiliki akun aktif di sistem sebelum sesi latihan resmi dimulai.
2. Sesi latihan harus dibuka terlebih dahulu oleh pelatih penanggung jawab agar presensi mandiri siswa dapat diterima.

### 8.3 Ketergantungan
1. Bobot model AI (*weights manifest & shard bins*) tersimpan di direktori lokal `/static/models/`.
2. Format data NISN bergantung pada acuan nomor induk resmi yang diterbitkan oleh Kemdikbudristek.

---

## 9. Matriks Ketertelusuran

| Dokumen Sumber | Bagian Sumber | Cakupan pada Dokumen SRS |
| :--- | :--- | :--- |
| **PRD SilatTrack v1.3.0** | §2 User Personas & Roles | FR-001 s.d. FR-007, FR-044 (RBAC, Multi-Sekolah, Portal Wali) |
| **PRD SilatTrack v1.3.0** | §3.1 Multi-School Support | FR-037, FR-038 (Sekolah, Kop Surat, Tanda Tangan Kustom) |
| **PRD SilatTrack v1.3.0** | §3.2 Standarisasi NISN & KTA | FR-039, FR-045 (10-Digit NISN Kemdikbud, KTA Digital) |
| **PRD SilatTrack v1.3.0** | §3.3 Sesi Fleksibel & Approval | FR-022 s.d. FR-026, FR-040, FR-041, FR-046 |
| **PRD SilatTrack v1.3.0** | §3.4 AI Biometrics & Dynamic QR | FR-008 s.d. FR-021, FR-033, FR-043, NFR-003, NFR-007 |
| **PRD SilatTrack v1.3.0** | §3.5 Safe Deletion Approval | FR-042 (Pengajuan Hapus Anggota Terkontrol) |
| **PRD SilatTrack v1.3.0** | §3.6 Parent Portal | FR-035, FR-044 (Portal Transparansi Wali Murid) |
| **PRD SilatTrack v1.3.0** | §3.7 Gamifikasi & Sabuk | FR-029 s.d. FR-032 (Sabuk, Kelayakan UKT, Streak) |
| **PRD SilatTrack v1.3.0** | §3.8 Pelaporan & Rekapitulasi | FR-027, FR-028, FR-038 (Dashboard, Excel, PDF Print Kustom) |
| **PRD SilatTrack v1.3.0** | §3.9 ID Card RBAC Print | FR-047, FR-048 (ID Card Pelatih & Anggota, Akses Cetak Terbatas) |
| **PRD SilatTrack v1.3.0** | §3.10 Sertifikat Resmi Dual-Logo | FR-049 (Sertifikat Landscape A4, Dual Logo, Border Silat) |
| **PRD SilatTrack v1.3.0** | §3.11 Identitas Perguruan & Kop | FR-050, FR-051, FR-052 (Model Perguruan, Dual-Logo Kop & Modal) |
| **ERD SilatTrack v1.3.0** | Spesifikasi Model Data & Relasi | Bagian 6 (Entitas Perguruan, Sekolah, Presensi, Sesi, Kenaikan Sabuk) |

---

## Lampiran A. Glosarium
- **DATH Stack:** Arsitektur modern monolitik yang menggabungkan Django, Alpine.js, Tailwind CSS, dan HTMX.
- **Descriptor Wajah:** Vektor numerik array 128 dimensi yang merepresentasikan fitur unik kontur wajah seseorang.
- **Euclidean Distance:** Formula perhitungan jarak geometris antara dua vektor numerik untuk mengukur tingkat kemiripan wajah. Semakin kecil angkanya ($\le 0{,}60$), semakin identik wajah tersebut.
- **Dynamic Rolling QR:** Kode QR beranimasi yang token tanda tangannya divalidasi dengan kunci rahasia sesi untuk mencegah pemalsuan presensi.
- **Geofencing:** Validasi radius toleransi jarak fisik perangkat terhadap koordinat lokasi latihan menggunakan GPS.
- **HTML-over-the-Wire:** Pola arsitektur di mana server mengirimkan potongan HTML siap pakai ke peramban, alih-alih mengirim JSON mentah yang harus dirender frontend.
- **KTA Digital:** Kartu Tanda Anggota elektronik yang memuat identitas pesilat, barcode/QR ID, foto, dan asal sekolah.
- **UKT:** Ujian Kenaikan Tingkat sabuk dalam seni bela diri pencak silat.

---

## Lampiran B. Catatan Rilis
Dokumen SRS versi 1.3 ini merupakan spesifikasi lengkap sistem SilatTrack edisi rilis produksi terbaru. Seluruh pembaruan fitur—meliputi dukungan multi-sekolah, format NISN 10 digit Kemdikbudristek, workflow persetujuan sesi dan jadwal oleh admin, audit log snapshot presensi biometrik, pengajuan hapus anggota terkontrol, portal transparansi orang tua, KTA digital, ID Card Anggota & Pelatih dengan pembatasan hak cetak (RBAC), Sertifikat resmi dual-logo, Model Identitas Perguruan Silat global, serta Dual-Logo Kop Surat pada Laporan Presensi dengan modal kustomisasi interaktif—telah diintegrasikan secara komprehensif ke dalam kebutuhan fungsional, kebutuhan non-fungsional, model data, aturan bisnis, dan kriteria pengujian sistem.
