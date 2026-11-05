from django.contrib import admin
from .models import JadwalLatihan


@admin.register(JadwalLatihan)
class JadwalLatihanAdmin(admin.ModelAdmin):
    list_display = ('nama_jadwal', 'hari_indeks', 'jam_mulai', 'jam_selesai', 'nama_lokasi', 'is_aktif')
    list_filter = ('hari_indeks', 'is_aktif')
    search_fields = ('nama_jadwal', 'nama_lokasi')
