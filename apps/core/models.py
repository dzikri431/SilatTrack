from django.db import models


class TingkatSabuk(models.Model):
    nama_sabuk = models.CharField(max_length=50, unique=True, verbose_name="Nama Sabuk")
    urutan_tingkat = models.PositiveSmallIntegerField(unique=True, verbose_name="Urutan Tingkat (Hierarki)")
    warna_hex = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Warna HEX")
    min_kehadiran_ukt = models.PositiveSmallIntegerField(
        default=75,
        verbose_name="Minimal Kehadiran untuk UKT (%)",
        help_text="Persentase minimum presensi latihan sebelum berhak mengikuti Ujian Kenaikan Tingkat."
    )
    deskripsi = models.TextField(blank=True, null=True, verbose_name="Deskripsi / Kurikulum Materi")

    class Meta:
        verbose_name = "Tingkat Sabuk"
        verbose_name_plural = "Daftar Tingkat Sabuk"
        ordering = ['urutan_tingkat']

    def __str__(self):
        return f"Sabuk {self.nama_sabuk} (Tingkat {self.urutan_tingkat})"


class KategoriTanding(models.Model):
    nama = models.CharField(max_length=100, verbose_name="Nama Kategori")
    kelas_tanding = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Kelas Berat / Golongan",
        help_text="Contoh: Kelas A (39-43 kg), Kelas Bebas, Seni Tunggal Baku"
    )
    catatan_teknis = models.TextField(blank=True, null=True, verbose_name="Catatan Teknis / Juri")

    class Meta:
        verbose_name = "Kategori Tanding / Seni"
        verbose_name_plural = "Daftar Kategori Tanding / Seni"
        ordering = ['nama']

    def __str__(self):
        if self.kelas_tanding:
            return f"{self.nama} - {self.kelas_tanding}"
        return self.nama


class Sekolah(models.Model):
    nama_sekolah = models.CharField(max_length=150, unique=True, verbose_name="Nama Sekolah")
    npsn = models.CharField(max_length=20, blank=True, null=True, verbose_name="NPSN")
    alamat = models.TextField(blank=True, null=True, verbose_name="Alamat Sekolah")
    logo_sekolah = models.FileField(
        upload_to='sekolah_logos/',
        blank=True,
        null=True,
        verbose_name="Logo Resmi Sekolah"
    )
    nama_kepala_sekolah = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        default="Drs. H. Mulyadi, M.M",
        verbose_name="Nama Kepala Sekolah"
    )
    nip_kepala_sekolah = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default="19720412 199802 1 003",
        verbose_name="NIP Kepala Sekolah"
    )
    jabatan_kepala_sekolah = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="Kepala Sekolah",
        verbose_name="Jabatan Kepala Sekolah"
    )
    is_aktif = models.BooleanField(default=True, verbose_name="Status Aktif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Ditambahkan")

    class Meta:
        verbose_name = "Sekolah"
        verbose_name_plural = "Daftar Sekolah"
        ordering = ['nama_sekolah']

    def __str__(self):
        return self.nama_sekolah

    @property
    def logo(self):
        return self.logo_sekolah


class Perguruan(models.Model):
    nama_perguruan = models.CharField(
        max_length=150,
        default="Perguruan Pencak Silat Indonesia",
        verbose_name="Nama Perguruan / Padepokan Silat"
    )
    singkatan = models.CharField(
        max_length=50,
        default="SilatTrack",
        verbose_name="Singkatan / Nama Brand Aplikasi",
        help_text="Nama pendek yang tampil pada bilah navigasi dan tajuk aplikasi."
    )
    logo_perguruan = models.FileField(
        upload_to='perguruan_logos/',
        blank=True,
        null=True,
        verbose_name="Logo Resmi Perguruan"
    )
    semboyan = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default="Ksatria Berbudi Luhur dan Berakhlak Mulia",
        verbose_name="Motto / Semboyan Perguruan"
    )
    alamat_pusat = models.TextField(
        blank=True,
        null=True,
        default="Sekretariat Pusat Dewan Pendekar Pencak Silat",
        verbose_name="Alamat Padepokan / Pusat"
    )
    kontak = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default="(021) 8876-5432",
        verbose_name="Kontak Sekretariat"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Dibuat Pada")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Terakhir Diperbarui")

    class Meta:
        verbose_name = "Pengaturan Perguruan & Identitas Aplikasi"
        verbose_name_plural = "Pengaturan Perguruan & Identitas Aplikasi"

    def __str__(self):
        return self.nama_perguruan

    @property
    def logo(self):
        return self.logo_perguruan

    @classmethod
    def get_solo(cls):
        """Mengambil data identitas perguruan tunggal atau membuat bawaan jika belum ada."""
        obj = cls.objects.first()
        if not obj:
            obj = cls.objects.create(
                nama_perguruan="Perguruan Pencak Silat Indonesia",
                singkatan="SilatTrack",
                semboyan="Ksatria Berbudi Luhur dan Berakhlak Mulia"
            )
        return obj


