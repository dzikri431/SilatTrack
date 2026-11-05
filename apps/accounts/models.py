import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


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
