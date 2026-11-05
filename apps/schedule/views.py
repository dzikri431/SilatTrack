from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import JadwalLatihan
from apps.core.models import Sekolah



@login_required
def schedule_list(request):
    user = request.user
    if user.is_admin_role:
        # Admin melihat seluruh jadwal, termasuk pengajuan pelatih
        jadwal_list = JadwalLatihan.objects.all().select_related('dibuat_oleh', 'disetujui_oleh').order_by('hari_indeks', 'jam_mulai')
        pending_schedules = JadwalLatihan.objects.filter(status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU).select_related('dibuat_oleh')
    elif user.is_pelatih_role:
        # Pelatih melihat jadwal aktif plus pengajuan miliknya
        jadwal_list = JadwalLatihan.objects.filter(
            is_aktif=True,
            status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI
        ) | JadwalLatihan.objects.filter(dibuat_oleh=user)
        jadwal_list = jadwal_list.distinct().select_related('dibuat_oleh', 'disetujui_oleh').order_by('hari_indeks', 'jam_mulai')
        pending_schedules = JadwalLatihan.objects.filter(dibuat_oleh=user, status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU)
    else:
        # Siswa/Anggota hanya melihat jadwal aktif yang telah disetujui
        jadwal_list = JadwalLatihan.objects.filter(
            is_aktif=True,
            status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI
        ).select_related('dibuat_oleh').order_by('hari_indeks', 'jam_mulai')
        pending_schedules = JadwalLatihan.objects.none()

    context = {
        'jadwal_list': jadwal_list,
        'pending_schedules': pending_schedules,
        'total_pending': pending_schedules.count(),
    }
    return render(request, 'schedule/schedule_list.html', context)


@login_required
def schedule_create(request):
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak. Hanya Admin atau Pelatih yang dapat menambah / mengajukan jadwal.")
        return redirect('schedule:schedule_list')

    if request.method == 'POST':
        nama_jadwal = request.POST.get('nama_jadwal', '').strip()
        hari_indeks = request.POST.get('hari_indeks')
        jam_mulai = request.POST.get('jam_mulai')
        jam_selesai = request.POST.get('jam_selesai')
        nama_lokasi = request.POST.get('nama_lokasi', '').strip()
        radius_toleransi_meter = request.POST.get('radius_toleransi_meter', 100)
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None

        sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')
        if not nama_jadwal or hari_indeks is None or not jam_mulai or not jam_selesai or not nama_lokasi:
            messages.error(request, "Mohon lengkapi semua kolom wajib (*).")
            return render(request, 'schedule/schedule_create.html', {
                'hari_choices': JadwalLatihan.Hari.choices,
                'sekolah_list': sekolah_list,
                'form_data': request.POST,
            })

        if request.user.is_admin_role:
            # Jika Admin yang membuat, langsung disetujui & aktif
            jadwal = JadwalLatihan.objects.create(
                nama_jadwal=nama_jadwal,
                hari_indeks=hari_indeks,
                jam_mulai=jam_mulai,
                jam_selesai=jam_selesai,
                nama_lokasi=nama_lokasi,
                radius_toleransi_meter=radius_toleransi_meter,
                latitude=latitude,
                longitude=longitude,
                is_aktif=True,
                status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI,
                dibuat_oleh=request.user,
                disetujui_oleh=request.user,
            )
            messages.success(request, f"Jadwal latihan mingguan '{jadwal.nama_jadwal}' berhasil ditambahkan dan langsung aktif!")
        else:
            # Jika Pelatih yang mengajukan, butuh persetujuan Admin
            jadwal = JadwalLatihan.objects.create(
                nama_jadwal=nama_jadwal,
                hari_indeks=hari_indeks,
                jam_mulai=jam_mulai,
                jam_selesai=jam_selesai,
                nama_lokasi=nama_lokasi,
                radius_toleransi_meter=radius_toleransi_meter,
                latitude=latitude,
                longitude=longitude,
                is_aktif=False,
                status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU,
                dibuat_oleh=request.user,
            )
            messages.success(request, f"Jadwal latihan '{jadwal.nama_jadwal}' berhasil diajukan! Menunggu persetujuan Admin / Pembina eskul sebelum aktif.")

        return redirect('schedule:schedule_list')

    sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')
    return render(request, 'schedule/schedule_create.html', {
        'hari_choices': JadwalLatihan.Hari.choices,
        'sekolah_list': sekolah_list,
    })


@login_required
@require_POST
def schedule_delete(request, jadwal_id):
    """
    Hanya Admin yang berhak menghapus jadwal latihan mingguan.
    """
    if not request.user.is_admin_role:
        messages.error(request, "Akses ditolak. Hanya Admin / Pembina yang dapat menghapus jadwal latihan.")
        return redirect('schedule:schedule_list')

    jadwal = get_object_or_404(JadwalLatihan, id=jadwal_id)
    nama = jadwal.nama_jadwal
    hari = jadwal.get_hari_indeks_display()
    jadwal.delete()
    messages.success(request, f"Jadwal latihan '{nama}' ({hari}) berhasil dihapus dari sistem.")
    return redirect('schedule:schedule_list')


@login_required
@require_POST
def schedule_approve(request, jadwal_id):
    """
    Persetujuan pengajuan jadwal latihan pelatih oleh Admin.
    """
    if not request.user.is_admin_role:
        messages.error(request, "Akses ditolak. Hanya Admin / Pembina yang dapat menyetujui atau menolak jadwal.")
        return redirect('schedule:schedule_list')

    jadwal = get_object_or_404(JadwalLatihan, id=jadwal_id)
    action = request.POST.get('action', 'setuju')
    catatan = (request.POST.get('catatan') or request.POST.get('catatan_admin') or '').strip()

    if action == 'setuju':
        jadwal.status_persetujuan = JadwalLatihan.StatusPersetujuan.DISETUJUI
        jadwal.disetujui_oleh = request.user
        jadwal.is_aktif = True
        jadwal.catatan_admin = catatan
        jadwal.save()
        messages.success(request, f"Pengajuan jadwal '{jadwal.nama_jadwal}' telah disetujui dan kini aktif!")
    elif action == 'tolak':
        jadwal.status_persetujuan = JadwalLatihan.StatusPersetujuan.DITOLAK
        jadwal.disetujui_oleh = request.user
        jadwal.is_aktif = False
        jadwal.catatan_admin = catatan
        jadwal.save()
        messages.info(request, f"Pengajuan jadwal '{jadwal.nama_jadwal}' telah ditolak.")

    return redirect('schedule:schedule_list')
