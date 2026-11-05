from django.contrib import admin
from .models import SesiLatihan, Presensi


@admin.register(SesiLatihan)
class SesiLatihanAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'tipe_sesi', 'pelatih', 'nama_lokasi', 'status', 'total_hadir')
    list_filter = ('status', 'tipe_sesi', 'tanggal')
    search_fields = ('pelatih__first_name', 'pelatih__last_name', 'materi_latihan', 'nama_lokasi')



@admin.register(Presensi)
class PresensiAdmin(admin.ModelAdmin):
    list_display = ('anggota', 'sesi', 'status', 'metode_presensi', 'waktu_presensi', 'is_verified')
    list_filter = ('status', 'metode_presensi', 'is_verified')
    search_fields = ('anggota__user__first_name', 'anggota__user__last_name', 'anggota__nisn')
