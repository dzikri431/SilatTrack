from django.contrib import admin
from .models import TingkatSabuk, KategoriTanding, Sekolah


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
    list_display = ('nama_sekolah', 'npsn', 'nama_kepala_sekolah', 'nip_kepala_sekolah', 'is_aktif')
    search_fields = ('nama_sekolah', 'npsn', 'nama_kepala_sekolah')
    list_filter = ('is_aktif',)

