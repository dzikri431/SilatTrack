import hashlib
import hmac
import time
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.schedule.models import JadwalLatihan
from apps.members.models import AnggotaProfile


def generate_qr_secret_salt():
    return uuid.uuid4().hex


class SesiLatihan(models.Model):
    class StatusSesi(models.TextChoices):
        TERJADWAL = 'TERJADWAL', 'Terjadwal'
        DIBUKA = 'DIBUKA', 'Sesi Dibuka (Presensi Aktif)'
        SELESAI = 'SELESAI', 'Selesai Ditutup'
        BATAL = 'BATAL', 'Dibatalkan'

    class TipeSesi(models.TextChoices):
        REGULER = 'REGULER', 'Latihan Rutin'
        TC_KEJUARAAN = 'TC_KEJUARAAN', 'Training Camp (TC) Kejuaraan'
        UKT = 'UKT', 'Ujian Kenaikan Tingkat (UKT)'
        FISIK = 'FISIK', 'Tes Fisik & Ketahanan'

    class StatusPersetujuanSesi(models.TextChoices):
        MENUNGGU = 'MENUNGGU', 'Menunggu Persetujuan Admin'
        DISETUJUI = 'DISETUJUI', 'Disetujui Admin'
        DITOLAK = 'DITOLAK', 'Ditolak Admin'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    jadwal = models.ForeignKey(
        JadwalLatihan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesi_list',
        verbose_name="Dasar Jadwal Rutin"
    )

    pelatih = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sesi_dilatih',
        verbose_name="Pelatih Penanggung Jawab"
    )

    tanggal = models.DateField(
        default=timezone.now,
        verbose_name="Tanggal Latihan"
    )

    jam_buka = models.DateTimeField(
        default=timezone.now,
        verbose_name="Waktu Dibuka"
    )

    jam_tutup = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Waktu Ditutup"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusSesi.choices,
        default=StatusSesi.DIBUKA,
        verbose_name="Status Sesi"
    )

    status_persetujuan = models.CharField(
        max_length=20,
        choices=StatusPersetujuanSesi.choices,
        default=StatusPersetujuanSesi.DISETUJUI,
        verbose_name="Status Persetujuan Admin"
    )

    disetujui_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesi_disetujui',
        verbose_name="Disetujui Oleh"
    )

    waktu_disetujui = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Waktu Persetujuan"
    )

    catatan_persetujuan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Catatan Persetujuan Admin"
    )

    tipe_sesi = models.CharField(
        max_length=20,
        choices=TipeSesi.choices,
        default=TipeSesi.REGULER,
        verbose_name="Tipe Latihan"
    )

    materi_latihan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Menu Materi Latihan",
        help_text=(
            "Contoh: Tangkisan atas, Elakan, Kuda-kuda tengah, "
            "Sambung rintis 3 ronde."
        )
    )

    nama_lokasi = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Lokasi / Tempat Latihan",
        help_text="Contoh: Dojo Utama SMKN 1 Rongga, Lapangan SMAN 1, GOR Kecamatan, dll."
    )

    jam_mulai = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Jam Mulai Latihan"
    )

    jam_selesai = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Jam Selesai Latihan"
    )

    qr_secret_salt = models.CharField(
        max_length=64,
        default=generate_qr_secret_salt,
        verbose_name="QR Secret Salt (HMAC)"
    )


    latitude_aktual = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Latitude Pelatih"
    )

    longitude_aktual = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Longitude Pelatih"
    )

    total_hadir = models.PositiveIntegerField(
        default=0,
        verbose_name="Total Hadir"
    )

    foto_kegiatan = models.FileField(
        upload_to='kegiatan_sesi/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Foto Dokumentasi Kegiatan Sesi"
    )

    keterangan_foto = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Keterangan Foto Kegiatan"
    )

    class Meta:
        verbose_name = "Sesi Latihan"
        verbose_name_plural = "Daftar Sesi Latihan"
        ordering = ['-tanggal', '-jam_buka']

    def __str__(self):
        return (
            f"{self.get_tipe_sesi_display()} - "
            f"{self.tanggal.strftime('%d/%m/%Y')} "
            f"({self.get_status_display()})"
        )

    @property
    def lokasi_efektif(self):
        if self.nama_lokasi:
            return self.nama_lokasi
        if self.jadwal and self.jadwal.nama_lokasi:
            return self.jadwal.nama_lokasi
        return "Dojo Utama"

    @property
    def jam_mulai_efektif(self):
        if self.jam_mulai:
            return self.jam_mulai
        if self.jadwal and self.jadwal.jam_mulai:
            return self.jadwal.jam_mulai
        return self.jam_buka.time() if self.jam_buka else None

    @property
    def jam_selesai_efektif(self):
        if self.jam_selesai:
            return self.jam_selesai
        if self.jadwal and self.jadwal.jam_selesai:
            return self.jadwal.jam_selesai
        return None


    def generate_current_qr_token(self, interval_seconds=None):
        """
        Menghasilkan Token QR Code untuk sesi latihan.
        Format: <sesi_id>:<hmac_hash> (statis dan aman untuk sesi ini, tanpa batas putaran waktu).
        """
        message = str(self.id).encode('utf-8')
        secret_key = self.qr_secret_salt.encode('utf-8')
        signature = hmac.new(
            secret_key,
            message,
            hashlib.sha256
        ).hexdigest()[:16]
        return f"{self.id}:{signature}"

    def verify_qr_token(
        self,
        token_str,
        interval_seconds=None,
        tolerance_slots=None
    ):
        """
        Validasi token QR Code sesi.
        Mendukung format sesi statis (<sesi_id>:<signature>)
        maupun format legacy (<sesi_id>:<timeslot>:<signature>).
        """
        try:
            if not token_str:
                return False, "Token QR Code kosong."

            parts = token_str.split(':')

            if len(parts) == 2:
                sesi_id, provided_sig = parts

                if sesi_id != str(self.id):
                    return False, "QR Code bukan milik sesi latihan ini."

                if self.status != self.StatusSesi.DIBUKA:
                    return (
                        False,
                        "Sesi latihan sudah ditutup oleh pelatih. "
                        "Presensi tidak lagi dapat dilakukan."
                    )

                message = str(self.id).encode('utf-8')
                secret_key = self.qr_secret_salt.encode('utf-8')
                expected_sig = hmac.new(
                    secret_key,
                    message,
                    hashlib.sha256
                ).hexdigest()[:16]

                if hmac.compare_digest(expected_sig, provided_sig):
                    return True, "Valid"

                return (
                    False,
                    "Kode QR tidak sah / tanda tangan keamanan tidak cocok."
                )

            elif len(parts) == 3:
                # Dukungan format legacy jika ada token lama
                sesi_id, timeslot_str, provided_sig = parts

                if sesi_id != str(self.id):
                    return False, "QR Code bukan milik sesi latihan ini."

                if self.status != self.StatusSesi.DIBUKA:
                    return (
                        False,
                        "Sesi latihan sudah ditutup oleh pelatih. "
                        "Presensi tidak lagi dapat dilakukan."
                    )

                token_timeslot = int(timeslot_str)
                message = f"{self.id}:{token_timeslot}".encode('utf-8')
                secret_key = self.qr_secret_salt.encode('utf-8')
                expected_sig = hmac.new(
                    secret_key,
                    message,
                    hashlib.sha256
                ).hexdigest()[:16]

                if hmac.compare_digest(expected_sig, provided_sig):
                    return True, "Valid"

                return (
                    False,
                    "Kode QR tidak sah / tanda tangan keamanan tidak cocok."
                )

            else:
                return False, "Format QR Code tidak valid."

        except Exception as e:
            return False, f"Kesalahan verifikasi token: {str(e)}"

    def update_attendance_counters(self):
        self.total_hadir = self.daftar_presensi.filter(
            status=Presensi.StatusPresensi.HADIR
        ).count()

        self.save(update_fields=['total_hadir'])


class Presensi(models.Model):
    class StatusPresensi(models.TextChoices):
        HADIR = 'HADIR', 'Hadir'
        IZIN = 'IZIN', 'Izin'
        SAKIT = 'SAKIT', 'Sakit'
        ALPA = 'ALPA', 'Alpa / Tanpa Keterangan'

    class MetodePresensi(models.TextChoices):
        FACE_SCAN = (
            'FACE_SCAN',
            'AI Face Recognition Scanner'
        )
        QR_DYNAMIC = (
            'QR_DYNAMIC',
            'Scan QR Code'
        )
        MANUAL_PELATIH = (
            'MANUAL_PELATIH',
            'Input Manual Pelatih'
        )
        MANUAL_MANDIRI = (
            'MANUAL_MANDIRI',
            'Input Manual Mandiri (Siswa)'
        )
        GEOFENCE = (
            'GEOFENCE',
            'Geofencing GPS'
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    sesi = models.ForeignKey(
        SesiLatihan,
        on_delete=models.CASCADE,
        related_name='daftar_presensi',
        verbose_name="Sesi Latihan"
    )

    anggota = models.ForeignKey(
        AnggotaProfile,
        on_delete=models.CASCADE,
        related_name='riwayat_presensi',
        verbose_name="Pesilat"
    )

    status = models.CharField(
        max_length=10,
        choices=StatusPresensi.choices,
        default=StatusPresensi.HADIR,
        verbose_name="Status Kehadiran"
    )

    metode_presensi = models.CharField(
        max_length=20,
        choices=MetodePresensi.choices,
        default=MetodePresensi.FACE_SCAN,
        verbose_name="Metode Presensi"
    )

    waktu_presensi = models.DateTimeField(
        default=timezone.now,
        verbose_name="Waktu Presensi"
    )

    bukti_foto = models.FileField(
        upload_to='surat_izin/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Foto Surat Izin / Sakit"
    )

    foto_face_scan = models.FileField(
        upload_to='face_scans/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Snapshot Bukti Wajah Biometrik"
    )

    face_distance = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Euclidean Distance Wajah"
    )

    catatan_alasan = models.TextField(
        blank=True,
        null=True,
        verbose_name="Catatan / Alasan"
    )

    is_verified = models.BooleanField(
        default=True,
        verbose_name="Terverifikasi"
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='presensi_diverifikasi',
        verbose_name="Diverifikasi Oleh"
    )

    user_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Latitude Siswa"
    )

    user_longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="Longitude Siswa"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="IP Address"
    )

    device_user_agent = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Device Agent"
    )

    class Meta:
        verbose_name = "Presensi Latihan"
        verbose_name_plural = "Daftar Presensi Latihan"
        unique_together = ('sesi', 'anggota')
        ordering = ['-waktu_presensi']

    def __str__(self):
        return (
            f"{self.anggota.user.get_full_name()} - "
            f"{self.sesi.tanggal} "
            f"({self.get_status_display()})"
        )