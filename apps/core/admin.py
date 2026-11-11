from django.contrib import admin
from .models import TingkatSabuk, KategoriTanding, Sekolah, Perguruan


@admin.register(TingkatSabuk)
class TingkatSabukAdmin(admin.ModelAdmin):
    list_display = ('urutan_tingkat', 'nama_sabuk', 'warna_hex', 'min_kehadiran_ukt')
    ordering = ('urutan_tingkat',)


@admin.register(KategoriTanding)
class KategoriTandingAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kelas_tanding')
    search_fields = ('nama', 'kelas_tanding')


@admin.register(Sekolah)
class SekolahAdmin(admin.ModelAdmin):
    list_display = ('nama_sekolah', 'npsn', 'nama_kepala_sekolah', 'nip_kepala_sekolah', 'logo_sekolah', 'is_aktif')
    search_fields = ('nama_sekolah', 'npsn', 'nama_kepala_sekolah')
    list_filter = ('is_aktif',)


@admin.register(Perguruan)
class PerguruanAdmin(admin.ModelAdmin):
    list_display = ('nama_perguruan', 'singkatan', 'logo_perguruan', 'kontak')


