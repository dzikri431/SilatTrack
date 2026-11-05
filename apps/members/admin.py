from django.contrib import admin
from .models import AnggotaProfile, PelatihProfile, RiwayatKenaikanSabuk


@admin.register(AnggotaProfile)
class AnggotaProfileAdmin(admin.ModelAdmin):
    list_display = ('nisn', 'user', 'sekolah', 'kelas_sekolah', 'sabuk_saat_ini', 'status_keanggotaan')
    list_filter = ('sekolah', 'sabuk_saat_ini', 'status_keanggotaan', 'jenis_kelamin')
    search_fields = ('nisn', 'user__first_name', 'user__last_name', 'kelas_sekolah', 'sekolah__nama_sekolah')



@admin.register(PelatihProfile)
class PelatihProfileAdmin(admin.ModelAdmin):
    list_display = ('nomor_registrasi', 'user', 'tingkatan_pendekar', 'spesialisasi')
    search_fields = ('nomor_registrasi', 'user__first_name', 'user__last_name')


@admin.register(RiwayatKenaikanSabuk)
class RiwayatKenaikanSabukAdmin(admin.ModelAdmin):
    list_display = ('anggota', 'sabuk_asal', 'sabuk_baru', 'tanggal_ujian', 'hasil')
    list_filter = ('hasil', 'tanggal_ujian')
