from django.conf import settings
from django.db import models


class JadwalLatihan(models.Model):
    class Hari(models.IntegerChoices):
        SENIN = 0, 'Senin'
        SELASA = 1, 'Selasa'
        RABU = 2, 'Rabu'
        KAMIS = 3, 'Kamis'
        JUMAT = 4, 'Jumat'
        SABTU = 5, 'Sabtu'
        MINGGU = 6, 'Minggu'

    class StatusPersetujuan(models.TextChoices):
        MENUNGGU = 'MENUNGGU', 'Menunggu Persetujuan Admin'
        DISETUJUI = 'DISETUJUI', 'Disetujui Admin'
        DITOLAK = 'DITOLAK', 'Ditolak Admin'

    nama_jadwal = models.CharField(max_length=100, verbose_name="Nama Jadwal / Kegiatan")
    hari_indeks = models.SmallIntegerField(choices=Hari.choices, verbose_name="Hari Latihan")
    jam_mulai = models.TimeField(verbose_name="Jam Mulai")
    jam_selesai = models.TimeField(verbose_name="Jam Selesai")
    nama_lokasi = models.CharField(max_length=150, verbose_name="Lokasi Latihan", help_text="Contoh: Dojo Utama / Lapangan Indoor Sekolah")
    
    # Koordinat Geofence
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="Latitude Lokasi")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="Longitude Lokasi")
    radius_toleransi_meter = models.PositiveIntegerField(
        default=100,
        verbose_name="Radius Toleransi (Meter)",
        help_text="Radius maksimal siswa dari titik lokasi untuk absensi geolokasi."
    )
    is_aktif = models.BooleanField(default=True, verbose_name="Status Jadwal Aktif")
    status_persetujuan = models.CharField(
        max_length=20,
        choices=StatusPersetujuan.choices,
        default=StatusPersetujuan.DISETUJUI,
        verbose_name="Status Persetujuan"
    )
    dibuat_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jadwal_diajukan',
        verbose_name="Dibuat / Diusulkan Oleh"
    )
    disetujui_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jadwal_disetujui',
        verbose_name="Disetujui Oleh"
    )
    catatan_admin = models.TextField(
        blank=True,
        null=True,
        verbose_name="Catatan Admin / Pembina"
    )

    class Meta:
        verbose_name = "Jadwal Latihan Rutin"
        verbose_name_plural = "Daftar Jadwal Latihan"
        ordering = ['hari_indeks', 'jam_mulai']

    def __str__(self):
        return f"{self.nama_jadwal} ({self.get_hari_indeks_display()}, {self.jam_mulai.strftime('%H:%M')} - {self.jam_selesai.strftime('%H:%M')})"
