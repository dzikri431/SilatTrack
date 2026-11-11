import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin / Pembina Eskul'
        PELATIH = 'PELATIH', 'Pelatih / Coach'
        ANGGOTA = 'ANGGOTA', 'Anggota / Siswa Pesilat'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ANGGOTA,
        verbose_name="Peran Pengguna"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Nomor WhatsApp / Kontak"
    )
    avatar = models.FileField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Foto Profil"
    )

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Daftar Pengguna"
        ordering = ['first_name', 'last_name', 'username']

    def __str__(self):
        full_name = self.get_full_name()
        return f"{full_name} ({self.get_role_display()})" if full_name else f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_pelatih_role(self):
        return self.role == self.Role.PELATIH

    @property
    def is_anggota_role(self):
        return self.role == self.Role.ANGGOTA


class AccountRequest(models.Model):
    """
    Permohonan pembuatan akun yang diajukan oleh Pelatih, menunggu persetujuan Admin.
    """
    class Status(models.TextChoices):
        PENDING  = 'PENDING',  'Menunggu Persetujuan'
        APPROVED = 'APPROVED', 'Disetujui'
        REJECTED = 'REJECTED', 'Ditolak'

    class AccountType(models.TextChoices):
        PELATIH = 'PELATIH', 'Pelatih / Coach'
        ANGGOTA = 'ANGGOTA', 'Anggota / Siswa Pesilat'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Siapa yang mengajukan
    requested_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='account_requests_sent',
        verbose_name="Diajukan oleh"
    )

    # Data akun yang diminta
    account_type  = models.CharField(max_length=10, choices=AccountType.choices, verbose_name="Tipe Akun")
    username      = models.CharField(max_length=150, verbose_name="Username")
    first_name    = models.CharField(max_length=150, verbose_name="Nama Depan")
    last_name     = models.CharField(max_length=150, blank=True, verbose_name="Nama Belakang")
    email         = models.EmailField(blank=True, verbose_name="Email")
    phone_number  = models.CharField(max_length=20, blank=True, verbose_name="No. HP")
    password_hash = models.CharField(max_length=256, verbose_name="Password (terenkripsi)")  # disimpan via set_password

    # Data tambahan tersimpan sebagai JSON
    extra_data = models.JSONField(default=dict, verbose_name="Data Profil Tambahan")

    # Status & audit
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name="Status")
    catatan_admin = models.TextField(blank=True, verbose_name="Catatan Admin")
    reviewed_by  = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='account_requests_reviewed',
        verbose_name="Ditinjau oleh"
    )
    created_at  = models.DateTimeField(default=timezone.now, verbose_name="Waktu Pengajuan")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Waktu Peninjauan")

    class Meta:
        verbose_name = "Permohonan Akun"
        verbose_name_plural = "Daftar Permohonan Akun"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.first_name} {self.last_name} ({self.get_account_type_display()}) — oleh {self.requested_by}"

