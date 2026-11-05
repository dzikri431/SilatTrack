import uuid
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from apps.core.models import TingkatSabuk, KategoriTanding, Sekolah

nisn_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="NISN harus tepat 10 digit angka sesuai standar resmi Kementerian Pendidikan (Kemdikbudristek)."
)


class AnggotaProfile(models.Model):
    class Gender(models.TextChoices):
        LAKI_LAKI = 'L', 'Laki-laki'
        PEREMPUAN = 'P', 'Perempuan'

    class MembershipStatus(models.TextChoices):
        AKTIF = 'AKTIF', 'Aktif Berlatih'
        NONAKTIF = 'NONAKTIF', 'Nonaktif / Hiatus'
        ALUMNI = 'ALUMNI', 'Alumni / Lulus'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='anggota_profile',
        verbose_name="Akun Pengguna"
    )
    nisn = models.CharField(
        max_length=10,
        unique=True,
        validators=[nisn_validator],
        verbose_name="NISN (10 Digit Kemendikbud)",
        help_text="10 digit Nomor Induk Siswa Nasional resmi Kemdikbudristek untuk sinkronisasi nilai e-Rapor sekolah."
    )
    sekolah = models.ForeignKey(
        Sekolah,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anggota_list',
        verbose_name="Asal Sekolah"
    )
    jenis_kelamin = models.CharField(max_length=1, choices=Gender.choices, default=Gender.LAKI_LAKI, verbose_name="Jenis Kelamin")
    tanggal_lahir = models.DateField(blank=True, null=True, verbose_name="Tanggal Lahir")
    kelas_sekolah = models.CharField(max_length=50, verbose_name="Kelas & Jurusan", help_text="Contoh: X PPLG 1, XI IPA 3")

    sabuk_saat_ini = models.ForeignKey(
        TingkatSabuk,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pesilat_list',
        verbose_name="Tingkat Sabuk Saat Ini"
    )
    kategori_fokus = models.ForeignKey(
        KategoriTanding,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pesilat_list',
        verbose_name="Kategori Peminatan"
    )
    nama_wali = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nama Orang Tua / Wali")
    no_hp_wali = models.CharField(max_length=20, blank=True, null=True, verbose_name="No. HP Wali Murid")
    status_keanggotaan = models.CharField(
        max_length=20,
        choices=MembershipStatus.choices,
        default=MembershipStatus.AKTIF,
        verbose_name="Status Keanggotaan"
    )

    # Biometric Profile (face-api.js on-device neural network embedding)
    face_descriptor = models.JSONField(
        blank=True,
        null=True,
        verbose_name="128-d Biometric Embedding Vector",
        help_text="Vektor 128 float embedding fitur wajah hasil inferensi face-api.js"
    )
    face_registered_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Waktu Registrasi Wajah Biometrik"
    )

    class Meta:
        verbose_name = "Profil Pesilat"
        verbose_name_plural = "Daftar Anggota Pesilat"
        ordering = ['kelas_sekolah', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.nisn}) - {self.sabuk_saat_ini.nama_sabuk if self.sabuk_saat_ini else 'Belum ada sabuk'}"

    @property
    def has_face_registered(self):
        """Cek apakah pesilat sudah melakukan auto-enrollment wajah biometrik."""
        return bool(self.face_descriptor and isinstance(self.face_descriptor, list) and len(self.face_descriptor) == 128)

    def calculate_attendance_streak(self):
        """Menghitung berapa sesi latihan berturut-turut pesilat hadir tanpa alpa."""
        from apps.attendance.models import Presensi
        recent = self.riwayat_presensi.select_related('sesi').order_by('-sesi__tanggal', '-sesi__jam_buka')
        streak = 0
        for p in recent:
            if p.status == Presensi.StatusPresensi.HADIR:
                streak += 1
            elif p.status in [Presensi.StatusPresensi.IZIN, Presensi.StatusPresensi.SAKIT]:
                continue
            else:
                break
        return streak


class PelatihProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='pelatih_profile',
        verbose_name="Akun Pengguna"
    )
    nomor_registrasi = models.CharField(max_length=50, unique=True, verbose_name="No. Registrasi / Lisensi Pelatih")
    tingkatan_pendekar = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tingkatan Pendekar / Gelar")
    spesialisasi = models.CharField(max_length=100, blank=True, null=True, verbose_name="Spesialisasi Kepelatihan", help_text="Tanding, Seni Tunggal/Ganda/Regu, Fisik, Wasit Juri")
    sertifikasi_sk = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nomor SK / Sertifikasi")

    class Meta:
        verbose_name = "Profil Pelatih"
        verbose_name_plural = "Daftar Pelatih"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.tingkatan_pendekar or 'Pelatih'}"


class RiwayatKenaikanSabuk(models.Model):
    class HasilUjian(models.TextChoices):
        LULUS_TERPUJI = 'LULUS_TERPUJI', 'Lulus Dengan Pujian'
        LULUS = 'LULUS', 'Lulus'
        MENGULANG = 'MENGULANG', 'Mengulang / Perbaikan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anggota = models.ForeignKey(AnggotaProfile, on_delete=models.CASCADE, related_name='riwayat_kenaikan_sabuk', verbose_name="Pesilat")
    sabuk_asal = models.ForeignKey(TingkatSabuk, on_delete=models.PROTECT, related_name='riwayat_sabuk_lama', verbose_name="Sabuk Lama")
    sabuk_baru = models.ForeignKey(TingkatSabuk, on_delete=models.PROTECT, related_name='riwayat_sabuk_baru', verbose_name="Sabuk Baru")
    penguji_pelatih = models.ForeignKey(PelatihProfile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Pelatih Penguji")
    tanggal_ujian = models.DateField(verbose_name="Tanggal Ujian (UKT)")
    hasil = models.CharField(max_length=20, choices=HasilUjian.choices, default=HasilUjian.LULUS, verbose_name="Hasil Ujian")
    evaluasi_teknik = models.TextField(blank=True, null=True, verbose_name="Catatan & Evaluasi Teknik")

    class Meta:
        verbose_name = "Riwayat Kenaikan Sabuk"
        verbose_name_plural = "Daftar Riwayat Kenaikan Sabuk"
        ordering = ['-tanggal_ujian']

    def __str__(self):
        return f"{self.anggota.user.get_full_name()}: {self.sabuk_asal.nama_sabuk} -> {self.sabuk_baru.nama_sabuk}"


class PengajuanHapusAnggota(models.Model):
    class StatusPengajuan(models.TextChoices):
        MENUNGGU = 'MENUNGGU', 'Menunggu Persetujuan Admin'
        DISETUJUI = 'DISETUJUI', 'Disetujui Admin'
        DITOLAK = 'DITOLAK', 'Ditolak Admin'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anggota = models.ForeignKey(
        AnggotaProfile,
        on_delete=models.CASCADE,
        related_name='pengajuan_hapus_list',
        verbose_name="Pesilat yang Diajukan Hapus"
    )
    diajukan_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pengajuan_hapus_diajukan',
        verbose_name="Pelatih Pemohon"
    )
    alasan = models.TextField(verbose_name="Alasan Permohonan Hapus")
    status = models.CharField(
        max_length=20,
        choices=StatusPengajuan.choices,
        default=StatusPengajuan.MENUNGGU,
        verbose_name="Status Persetujuan Admin"
    )
    disetujui_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pengajuan_hapus_disetujui',
        verbose_name="Disetujui Oleh"
    )
    catatan_admin = models.TextField(blank=True, null=True, verbose_name="Catatan Admin")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Waktu Pengajuan")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Waktu Pembaruan")

    class Meta:
        verbose_name = "Pengajuan Hapus Anggota"
        verbose_name_plural = "Daftar Pengajuan Hapus Anggota"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pengajuan Hapus {self.anggota.user.get_full_name()} oleh {self.diajukan_oleh.get_full_name()} ({self.get_status_display()})"

