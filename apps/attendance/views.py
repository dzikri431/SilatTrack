import base64
import datetime
import io
import json
import math
import time
import qrcode
import qrcode.image.svg
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.files.base import ContentFile
from django.conf import settings
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from .models import SesiLatihan, Presensi
from apps.accounts.models import User
from apps.core.models import Sekolah
from apps.members.models import AnggotaProfile, PelatihProfile, PengajuanHapusAnggota
from apps.schedule.models import JadwalLatihan



@login_required
def session_list(request):
    tipe_filter = request.GET.get('tipe', '')
    status_filter = request.GET.get('status', '')

    sesi_qs = SesiLatihan.objects.all().select_related('pelatih', 'jadwal')

    # Anggota/siswa hanya dapat melihat sesi latihan yang sudah disetujui/dibuka oleh admin atau pelatih
    if request.user.is_anggota_role:
        sesi_qs = sesi_qs.filter(status_persetujuan=SesiLatihan.StatusPersetujuanSesi.DISETUJUI)

    if tipe_filter:
        sesi_qs = sesi_qs.filter(tipe_sesi=tipe_filter)
    if status_filter:
        sesi_qs = sesi_qs.filter(status=status_filter)

    pending_sessions = SesiLatihan.objects.none()
    if request.user.is_admin_role:
        pending_sessions = SesiLatihan.objects.filter(status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU).select_related('pelatih')
    elif request.user.is_pelatih_role:
        pending_sessions = SesiLatihan.objects.filter(
            status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU,
            pelatih=request.user
        ).select_related('pelatih')

    context = {
        'sessions': sesi_qs,
        'pending_sessions': pending_sessions,
        'total_pending': pending_sessions.count(),
        'tipe_filter': tipe_filter,
        'status_filter': status_filter,
        'tipe_choices': SesiLatihan.TipeSesi.choices,
        'status_choices': SesiLatihan.StatusSesi.choices,
    }
    return render(request, 'attendance/session_list.html', context)


@login_required
def session_create(request):
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Hanya pelatih atau pembina yang dapat membuat sesi latihan.")
        return redirect('attendance:session_list')

    if request.method == 'POST':
        tipe_sesi = request.POST.get('tipe_sesi')
        materi = request.POST.get('materi_latihan', '').strip()
        jadwal_id = request.POST.get('jadwal_id')
        nama_lokasi = request.POST.get('nama_lokasi', '').strip()
        tanggal_input = request.POST.get('tanggal')
        jam_mulai_input = request.POST.get('jam_mulai')
        jam_selesai_input = request.POST.get('jam_selesai')

        jadwal = JadwalLatihan.objects.filter(id=jadwal_id, is_aktif=True, status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI).first() if jadwal_id else None

        # Fallback lokasi ke jadwal jika tidak diisi secara eksplisit
        if not nama_lokasi and jadwal:
            nama_lokasi = jadwal.nama_lokasi
        if not nama_lokasi:
            nama_lokasi = "Dojo SMKN 1 Rongga"

        # Tentukan Tanggal Latihan
        if tanggal_input:
            try:
                tanggal = datetime.datetime.strptime(tanggal_input, '%Y-%m-%d').date()
            except ValueError:
                tanggal = timezone.localdate()
        else:
            tanggal = timezone.localdate()

        # Tentukan Jam Mulai & Jam Selesai
        jam_mulai_obj = None
        jam_selesai_obj = None

        if jam_mulai_input:
            try:
                jam_mulai_obj = datetime.datetime.strptime(jam_mulai_input, '%H:%M').time()
            except ValueError:
                jam_mulai_obj = None
        elif jadwal and jadwal.jam_mulai:
            jam_mulai_obj = jadwal.jam_mulai

        if jam_selesai_input:
            try:
                jam_selesai_obj = datetime.datetime.strptime(jam_selesai_input, '%H:%M').time()
            except ValueError:
                jam_selesai_obj = None
        elif jadwal and jadwal.jam_selesai:
            jam_selesai_obj = jadwal.jam_selesai

        # Tentukan jam buka
        if jam_mulai_obj:
            dt_buka = datetime.datetime.combine(tanggal, jam_mulai_obj)
            jam_buka = timezone.make_aware(dt_buka) if timezone.is_naive(dt_buka) else dt_buka
        else:
            jam_buka = timezone.now()

        if request.user.is_admin_role:
            # Admin dapat langsung membuka sesi latihan aktif
            sesi = SesiLatihan.objects.create(
                pelatih=request.user,
                jadwal=jadwal,
                tipe_sesi=tipe_sesi,
                nama_lokasi=nama_lokasi,
                jam_mulai=jam_mulai_obj,
                jam_selesai=jam_selesai_obj,
                materi_latihan=materi,
                tanggal=tanggal,
                jam_buka=jam_buka,
                status=SesiLatihan.StatusSesi.DIBUKA,
                status_persetujuan=SesiLatihan.StatusPersetujuanSesi.DISETUJUI,
                disetujui_oleh=request.user,
                waktu_disetujui=timezone.now(),
            )
            messages.success(
                request,
                f"Sesi latihan {sesi.get_tipe_sesi_display()} di '{sesi.lokasi_efektif}' ({sesi.tanggal.strftime('%d/%m/%Y')}) berhasil dibuka dan aktif!"
            )
            return redirect('attendance:session_detail', session_id=sesi.id)
        else:
            # Pelatih membuat sesi -> harus atas persetujuan Admin
            sesi = SesiLatihan.objects.create(
                pelatih=request.user,
                jadwal=jadwal,
                tipe_sesi=tipe_sesi,
                nama_lokasi=nama_lokasi,
                jam_mulai=jam_mulai_obj,
                jam_selesai=jam_selesai_obj,
                materi_latihan=materi,
                tanggal=tanggal,
                jam_buka=jam_buka,
                status=SesiLatihan.StatusSesi.TERJADWAL,
                status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU,
            )
            messages.success(
                request,
                f"Pengajuan sesi latihan {sesi.get_tipe_sesi_display()} di '{sesi.lokasi_efektif}' pada {sesi.tanggal.strftime('%d/%m/%Y')} berhasil dikirim! "
                "Sesi latihan ini menunggu persetujuan Admin / Pembina eskul sebelum dapat dibuka untuk presensi."
            )
            return redirect('attendance:session_detail', session_id=sesi.id)

    jadwal_list = JadwalLatihan.objects.filter(is_aktif=True, status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI)
    sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')
    today_date = timezone.localdate()
    now_time = timezone.localtime()
    return render(request, 'attendance/session_create.html', {
        'jadwal_list': jadwal_list,
        'sekolah_list': sekolah_list,
        'tipe_choices': SesiLatihan.TipeSesi.choices,
        'default_date': today_date.strftime('%Y-%m-%d'),
        'default_time': now_time.strftime('%H:%M'),
    })



@login_required
def session_detail(request, session_id):
    sesi = get_object_or_404(SesiLatihan.objects.select_related('pelatih', 'jadwal'), id=session_id)
    
    if request.user.is_anggota_role and sesi.status_persetujuan != SesiLatihan.StatusPersetujuanSesi.DISETUJUI:
        messages.error(request, "Sesi latihan ini belum disetujui atau dibuka oleh admin/pelatih.")
        return redirect('attendance:session_list')

    # Ambil seluruh pesilat aktif (dengan relasi sekolah)
    sekolah_id = request.GET.get('sekolah', '').strip()
    pesilat_qs = AnggotaProfile.objects.filter(
        status_keanggotaan=AnggotaProfile.MembershipStatus.AKTIF
    ).select_related('user', 'sabuk_saat_ini', 'kategori_fokus', 'sekolah').order_by('sekolah__nama_sekolah', 'kelas_sekolah', 'user__first_name')

    if sekolah_id:
        pesilat_list = pesilat_qs.filter(sekolah_id=sekolah_id)
    else:
        pesilat_list = pesilat_qs

    # Mapping record presensi yang sudah ada untuk sesi ini
    presensi_map = {
        p.anggota_id: p for p in sesi.daftar_presensi.select_related('anggota')
    }

    pesilat_with_attendance = []
    for p in pesilat_list:
        pesilat_with_attendance.append({
            'anggota': p,
            'presensi': presensi_map.get(p.user_id),
        })

    sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')

    # Summary counts
    total_hadir = sesi.daftar_presensi.filter(status=Presensi.StatusPresensi.HADIR).count()
    total_izin = sesi.daftar_presensi.filter(status=Presensi.StatusPresensi.IZIN).count()
    total_sakit = sesi.daftar_presensi.filter(status=Presensi.StatusPresensi.SAKIT).count()
    total_alpa = sesi.daftar_presensi.filter(status=Presensi.StatusPresensi.ALPA).count()
    total_pesilat = pesilat_list.count()

    context = {
        'sesi': sesi,
        'pesilat_rows': pesilat_with_attendance,
        'sekolah_list': sekolah_list,
        'selected_sekolah': sekolah_id,
        'total_hadir': total_hadir,
        'total_izin': total_izin,
        'total_sakit': total_sakit,
        'total_alpa': total_alpa,
        'total_pesilat': total_pesilat,
    }
    return render(request, 'attendance/session_detail.html', context)



@login_required
@require_POST
def session_toggle_status(request, session_id):
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        return HttpResponse("Akses ditolak", status=403)

    sesi = get_object_or_404(SesiLatihan, id=session_id)

    # Pelatih tidak dapat membuka sesi yang belum disetujui oleh admin
    if sesi.status_persetujuan != SesiLatihan.StatusPersetujuanSesi.DISETUJUI:
        if request.user.is_admin_role:
            # Jika Admin yang men-toggle, otomatis setujui
            sesi.status_persetujuan = SesiLatihan.StatusPersetujuanSesi.DISETUJUI
            sesi.disetujui_oleh = request.user
            sesi.waktu_disetujui = timezone.now()
        else:
            messages.error(
                request,
                "Akses ditolak. Sesi latihan ini belum disetujui oleh Admin / Pembina eskul. "
                "Pelatih hanya dapat membuka sesi setelah mendapatkan persetujuan Admin."
            )
            return redirect('attendance:session_detail', session_id=sesi.id)

    if sesi.status == SesiLatihan.StatusSesi.DIBUKA:
        sesi.status = SesiLatihan.StatusSesi.SELESAI
        sesi.jam_tutup = timezone.now()
        messages.info(request, f"Sesi latihan {sesi.get_tipe_sesi_display()} telah resmi ditutup.")
    else:
        sesi.status = SesiLatihan.StatusSesi.DIBUKA
        sesi.jam_buka = timezone.now()
        messages.success(request, f"Sesi latihan dibuka kembali untuk presensi.")
    
    sesi.save()
    return redirect('attendance:session_detail', session_id=sesi.id)


@login_required
@require_POST
def session_approve(request, session_id):
    """
    Persetujuan pembukaan sesi latihan pelatih oleh Admin / Pembina eskul.
    """
    if not request.user.is_admin_role:
        messages.error(request, "Akses ditolak. Hanya Admin / Pembina yang berhak menyetujui sesi latihan.")
        return redirect('attendance:session_detail', session_id=session_id)

    sesi = get_object_or_404(SesiLatihan, id=session_id)
    action = request.POST.get('action', 'setuju')
    catatan = request.POST.get('catatan', '').strip()

    if action == 'setuju':
        sesi.status_persetujuan = SesiLatihan.StatusPersetujuanSesi.DISETUJUI
        sesi.disetujui_oleh = request.user
        sesi.waktu_disetujui = timezone.now()
        sesi.status = SesiLatihan.StatusSesi.DIBUKA
        sesi.jam_buka = timezone.now()
        if catatan:
            sesi.catatan_persetujuan = catatan
        sesi.save()
        messages.success(request, f"Sesi latihan '{sesi.get_tipe_sesi_display()}' pelatih telah disetujui dan resmi dibuka untuk presensi!")
    elif action == 'tolak':
        sesi.status_persetujuan = SesiLatihan.StatusPersetujuanSesi.DITOLAK
        sesi.disetujui_oleh = request.user
        sesi.waktu_disetujui = timezone.now()
        sesi.status = SesiLatihan.StatusSesi.BATAL
        if catatan:
            sesi.catatan_persetujuan = catatan
        sesi.save()
        messages.info(request, f"Pengajuan sesi latihan '{sesi.get_tipe_sesi_display()}' telah ditolak.")

    return redirect('attendance:session_detail', session_id=sesi.id)


@login_required
@require_POST
def session_delete(request, session_id):
    """
    Menghapus sesi latihan beserta seluruh riwayat presensi terkait (CASCADE).
    Hanya dapat diakses oleh Admin atau Pelatih.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak. Anda tidak memiliki izin untuk menghapus sesi latihan.")
        return redirect('attendance:session_list')

    sesi = get_object_or_404(SesiLatihan, id=session_id)
    tipe_display = sesi.get_tipe_sesi_display()
    tanggal_str = sesi.tanggal.strftime('%d/%m/%Y')
    
    sesi.delete()
    messages.success(request, f"Sesi latihan {tipe_display} ({tanggal_str}) beserta riwayat presensinya berhasil dihapus.")
    return redirect('attendance:session_list')


@login_required
@require_POST
def session_upload_photo(request, session_id):
    """
    Unggah atau perbarui foto dokumentasi kegiatan sesi latihan (Admin dan Pelatih).
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak. Hanya Admin dan Pelatih yang dapat mengunggah foto kegiatan.")
        return redirect('attendance:session_detail', session_id=session_id)

    sesi = get_object_or_404(SesiLatihan, id=session_id)
    action = request.POST.get('action', 'upload')

    if action == 'delete':
        if sesi.foto_kegiatan:
            sesi.foto_kegiatan.delete(save=False)
            sesi.foto_kegiatan = None
            sesi.keterangan_foto = None
            sesi.save()
        messages.success(request, "Foto dokumentasi kegiatan sesi latihan berhasil dihapus.")
    else:
        foto = request.FILES.get('foto_kegiatan')
        keterangan = request.POST.get('keterangan_foto', '').strip()
        if foto:
            sesi.foto_kegiatan = foto
        if keterangan:
            sesi.keterangan_foto = keterangan
        sesi.save()
        messages.success(request, "Laporan foto kegiatan sesi latihan berhasil diperbarui!")

    return redirect('attendance:session_detail', session_id=session_id)



@login_required
def get_session_qr(request, session_id):
    """
    HTMX Partial View: Mengembalikan SVG QR Code sesi latihan (statis untuk sesi tersebut)
    """
    sesi = get_object_or_404(SesiLatihan, id=session_id)
    
    # Generate Token Presensi Sesi (aman dengan HMAC salt, tetap selama sesi dibuka)
    qr_token = sesi.generate_current_qr_token()

    # Render QR Code sebagai pure SVG
    factory = qrcode.image.svg.SvgPathImage
    qr_img = qrcode.make(qr_token, image_factory=factory, box_size=10, border=2)
    svg_stream = io.BytesIO()
    qr_img.save(svg_stream)
    svg_data = svg_stream.getvalue().decode('utf-8')

    context = {
        'sesi': sesi,
        'svg_data': svg_data,
    }
    return render(request, 'attendance/partials/_qr_display.html', context)


@login_required
def qr_fullscreen(request, session_id):
    """
    Tampilan Layar Penuh QR Code untuk Proyektor / TV Dojo
    """
    sesi = get_object_or_404(SesiLatihan, id=session_id)
    return render(request, 'attendance/qr_fullscreen.html', {'sesi': sesi})


@login_required
@require_POST
def toggle_member_attendance(request, session_id, member_id):
    """
    HTMX Inline Toggle: Mengubah status absensi pesilat secara instan tanpa reload halaman
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        return HttpResponse("Akses ditolak", status=403)

    sesi = get_object_or_404(SesiLatihan, id=session_id)
    anggota = get_object_or_404(AnggotaProfile, user_id=member_id)
    new_status = request.GET.get('status', Presensi.StatusPresensi.HADIR)

    with transaction.atomic():
        presensi, created = Presensi.objects.get_or_create(
            sesi=sesi,
            anggota=anggota,
            defaults={
                'status': new_status,
                'metode_presensi': Presensi.MetodePresensi.MANUAL_PELATIH,
                'verified_by': request.user,
                'waktu_presensi': timezone.now()
            }
        )
        if not created:
            presensi.status = new_status
            presensi.metode_presensi = Presensi.MetodePresensi.MANUAL_PELATIH
            presensi.verified_by = request.user
            presensi.waktu_presensi = timezone.now()
            presensi.save()

        sesi.update_attendance_counters()

    total_hadir = Presensi.objects.filter(sesi=sesi, status=Presensi.StatusPresensi.HADIR).count()
    total_izin = Presensi.objects.filter(sesi=sesi, status=Presensi.StatusPresensi.IZIN).count()
    total_sakit = Presensi.objects.filter(sesi=sesi, status=Presensi.StatusPresensi.SAKIT).count()

    context = {
        'sesi': sesi,
        'item': {'anggota': anggota, 'presensi': presensi},
        'is_htmx': True,
        'total_hadir': total_hadir,
        'total_izin': total_izin,
        'total_sakit': total_sakit,
    }
    response = render(request, 'attendance/partials/_pesilat_row.html', context)
    response['HX-Trigger'] = json.dumps({
        'updateAttendanceCounters': {
            'hadir': total_hadir,
            'izin': total_izin,
            'sakit': total_sakit,
        }
    })
    return response


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Menghitung jarak antara 2 titik koordinat bumi (dalam meter) menggunakan formula Haversine.
    """
    R = 6371000  # radius bumi dalam meter
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c)


def calculate_euclidean_distance(v1, v2):
    """
    Menghitung jarak Euclidean antara 2 vektor descriptor 128-d (face-api.js).
    """
    if not v1 or not v2 or len(v1) != len(v2):
        return float('inf')
    return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(v1, v2)))


DEFAULT_DOJO_LAT = -7.0011
DEFAULT_DOJO_LNG = 107.2721
DEFAULT_DOJO_NAME = "SMKN 1 Rongga (Dojo Pencak Silat)"


@login_required
def scanner_view(request):
    """
    Halaman Presensi Hub untuk Murid / Pesilat:
    Presensi langsung masuk ke Sesi Latihan yang dibuka oleh Admin atau Pelatih.
    """
    today = timezone.localdate()
    active_session = SesiLatihan.objects.filter(
        status=SesiLatihan.StatusSesi.DIBUKA,
        status_persetujuan=SesiLatihan.StatusPersetujuanSesi.DISETUJUI
    ).select_related('jadwal', 'pelatih').order_by('-jam_buka').first()

    if not active_session:
        active_session = SesiLatihan.objects.filter(
            status=SesiLatihan.StatusSesi.DIBUKA
        ).select_related('jadwal', 'pelatih').order_by('-jam_buka').first()

    mode = request.GET.get('mode', 'qr')  # Default 'qr', opsi: 'face', 'manual'
    user_presensi = None
    anggota = getattr(request.user, 'anggota_profile', None)
    if active_session and anggota:
        user_presensi = Presensi.objects.filter(
            sesi=active_session,
            anggota=anggota
        ).first()

    # Data Biometrik Siswa
    has_face_registered = anggota.has_face_registered if anggota else False
    face_descriptor_json = json.dumps(anggota.face_descriptor) if (anggota and anggota.has_face_registered) else 'null'
    face_registered_at = anggota.face_registered_at if anggota else None

    # Koordinat acuan tempat latihan: SMKN 1 Rongga
    dojo_lat = DEFAULT_DOJO_LAT
    dojo_lng = DEFAULT_DOJO_LNG
    lokasi_nama = DEFAULT_DOJO_NAME
    if active_session:
        if active_session.latitude_aktual and active_session.longitude_aktual:
            dojo_lat = float(active_session.latitude_aktual)
            dojo_lng = float(active_session.longitude_aktual)
        elif active_session.jadwal and active_session.jadwal.latitude and active_session.jadwal.longitude:
            dojo_lat = float(active_session.jadwal.latitude)
            dojo_lng = float(active_session.jadwal.longitude)
        if active_session.nama_lokasi:
            lokasi_nama = active_session.nama_lokasi
        elif active_session.jadwal and active_session.jadwal.nama_lokasi:
            lokasi_nama = active_session.jadwal.nama_lokasi


    context = {
        'active_session': active_session,
        'initial_mode': mode,
        'user_presensi': user_presensi,
        'dojo_lat': dojo_lat,
        'dojo_lng': dojo_lng,
        'dojo_lat_unlocalized': f"{dojo_lat:.6f}",
        'dojo_lng_unlocalized': f"{dojo_lng:.6f}",
        'lokasi_nama': lokasi_nama,
        'max_radius_meter': 100,
        'anggota': anggota,
        'has_face_registered': has_face_registered,
        'face_descriptor_json': face_descriptor_json,
        'face_registered_at': face_registered_at,
    }
    return render(request, 'attendance/scanner.html', context)


@login_required
@require_POST
def self_checkin_submit(request):
    """
    Fitur Presensi Manual Mandiri untuk Siswa / Pesilat:
    Memeriksa konfirmasi radius lokasi tempat latihan (maksimal 100 meter).
    """
    user = request.user
    try:
        anggota = user.anggota_profile
    except AnggotaProfile.DoesNotExist:
        if request.htmx:
            return render(request, 'attendance/partials/_scan_result.html', {
                'success': False,
                'message': 'Akun kamu bukan profil pesilat aktif.'
            })
        messages.error(request, "Akun kamu bukan profil pesilat aktif.")
        return redirect('core:dashboard')

    sesi_id = request.POST.get('sesi_id')
    sesi = None
    if sesi_id:
        sesi = SesiLatihan.objects.filter(id=sesi_id, status=SesiLatihan.StatusSesi.DIBUKA).first()
    else:
        sesi = SesiLatihan.objects.filter(status=SesiLatihan.StatusSesi.DIBUKA).order_by('-jam_buka').first()

    if not sesi:
        if request.htmx:
            return render(request, 'attendance/partials/_scan_result.html', {
                'success': False,
                'message': 'Tidak ada sesi latihan yang sedang dibuka saat ini.'
            })
        messages.error(request, "Tidak ada sesi latihan yang sedang dibuka saat ini.")
        return redirect('attendance:scanner')

    # Validasi Radius Lokasi (100 Meter)
    user_lat_str = request.POST.get('user_latitude', '').strip()
    user_lng_str = request.POST.get('user_longitude', '').strip()

    target_lat = DEFAULT_DOJO_LAT
    target_lng = DEFAULT_DOJO_LNG
    if sesi.latitude_aktual and sesi.longitude_aktual:
        target_lat = float(sesi.latitude_aktual)
        target_lng = float(sesi.longitude_aktual)
    elif sesi.jadwal and sesi.jadwal.latitude and sesi.jadwal.longitude:
        target_lat = float(sesi.jadwal.latitude)
        target_lng = float(sesi.jadwal.longitude)

    user_lat = None
    user_lng = None
    if user_lat_str and user_lng_str:
        try:
            user_lat = float(user_lat_str)
            user_lng = float(user_lng_str)
            dist_meters = calculate_haversine_distance(target_lat, target_lng, user_lat, user_lng)
            if dist_meters > 100:
                if not settings.DEBUG:
                    msg = f"Presensi ditolak! Posisi Anda ({dist_meters} meter) berada di luar batas radius 100 meter dari tempat latihan."
                    if request.htmx:
                        return render(request, 'attendance/partials/_scan_result.html', {
                            'success': False,
                            'message': msg
                        })
                    messages.error(request, msg)
                    return redirect('attendance:scanner')
        except (ValueError, TypeError):
            pass
    else:
        if not settings.DEBUG:
            msg = "Presensi gagal: Konfirmasi lokasi GPS wajib diizinkan untuk memastikan posisi Anda berada dalam radius 100 meter tempat latihan."
            if request.htmx:
                return render(request, 'attendance/partials/_scan_result.html', {
                    'success': False,
                    'message': msg
                })
            messages.error(request, msg)
            return redirect('attendance:scanner')

    status_pilihan = request.POST.get('status', Presensi.StatusPresensi.HADIR)
    catatan = request.POST.get('catatan_alasan', '').strip()

    with transaction.atomic():
        presensi, created = Presensi.objects.get_or_create(
            sesi=sesi,
            anggota=anggota,
            defaults={
                'status': status_pilihan,
                'metode_presensi': Presensi.MetodePresensi.MANUAL_MANDIRI,
                'catatan_alasan': catatan,
                'waktu_presensi': timezone.now(),
                'user_latitude': user_lat,
                'user_longitude': user_lng,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'device_user_agent': request.META.get('HTTP_USER_AGENT', '')[:250],
            }
        )
        if not created:
            presensi.status = status_pilihan
            presensi.metode_presensi = Presensi.MetodePresensi.MANUAL_MANDIRI
            if catatan:
                presensi.catatan_alasan = catatan
            if user_lat and user_lng:
                presensi.user_latitude = user_lat
                presensi.user_longitude = user_lng
            presensi.waktu_presensi = timezone.now()
            presensi.save()

        sesi.update_attendance_counters()

    if request.htmx:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': True,
            'message': f'Presensi Mandiri Berhasil! Tercatat {presensi.get_status_display()} ({user.get_full_name() or user.username}).',
            'sesi': sesi,
            'presensi': presensi,
        })

    messages.success(request, f"Presensi mandiri berhasil dicatat! Status: {presensi.get_status_display()}.")
    return redirect('core:dashboard')


@login_required
@require_POST
def bulk_mark_all_present(request, session_id):
    """
    Aksi Input Manual Pelatih: Menandai seluruh pesilat aktif sebagai HADIR sekaligus
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        return HttpResponse("Akses ditolak", status=403)

    sesi = get_object_or_404(SesiLatihan, id=session_id)
    pesilat_list = AnggotaProfile.objects.filter(status_keanggotaan=AnggotaProfile.MembershipStatus.AKTIF)

    with transaction.atomic():
        for anggota in pesilat_list:
            presensi, created = Presensi.objects.get_or_create(
                sesi=sesi,
                anggota=anggota,
                defaults={
                    'status': Presensi.StatusPresensi.HADIR,
                    'metode_presensi': Presensi.MetodePresensi.MANUAL_PELATIH,
                    'verified_by': request.user,
                    'waktu_presensi': timezone.now(),
                }
            )
            if not created and presensi.status != Presensi.StatusPresensi.HADIR:
                presensi.status = Presensi.StatusPresensi.HADIR
                presensi.metode_presensi = Presensi.MetodePresensi.MANUAL_PELATIH
                presensi.verified_by = request.user
                presensi.waktu_presensi = timezone.now()
                presensi.save()

        sesi.update_attendance_counters()

    messages.success(request, f"Seluruh {pesilat_list.count()} pesilat aktif berhasil ditandai HADIR secara manual.")
    return redirect('attendance:session_detail', session_id=sesi.id)


@login_required
@require_POST
def submit_qr_scan(request):
    """
    HTMX Endpoint: Dipanggil oleh kamera HTML5-QRCode saat mendeteksi QR Code
    """
    user = request.user
    try:
        anggota = user.anggota_profile
    except AnggotaProfile.DoesNotExist:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Akun kamu bukan profil pesilat aktif.'
        })

    token_str = request.POST.get('qr_token', '').strip()
    if not token_str:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Token QR Code kosong.'
        })

    parts = token_str.split(':')
    if len(parts) not in (2, 3):
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Format QR Code tidak dikenali oleh sistem SilatTrack.'
        })

    sesi_id = parts[0]
    sesi = SesiLatihan.objects.filter(id=sesi_id, status=SesiLatihan.StatusSesi.DIBUKA).first()
    if not sesi:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Sesi latihan tidak ditemukan atau sudah ditutup oleh pelatih.'
        })

    # Verifikasi Dynamic HMAC Token
    is_valid, err_msg = sesi.verify_qr_token(token_str)
    if not is_valid:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': err_msg
        })

    # Validasi Radius Lokasi (100 Meter)
    user_lat_str = request.POST.get('user_latitude', '').strip()
    user_lng_str = request.POST.get('user_longitude', '').strip()

    target_lat = DEFAULT_DOJO_LAT
    target_lng = DEFAULT_DOJO_LNG
    if sesi.latitude_aktual and sesi.longitude_aktual:
        target_lat = float(sesi.latitude_aktual)
        target_lng = float(sesi.longitude_aktual)
    elif sesi.jadwal and sesi.jadwal.latitude and sesi.jadwal.longitude:
        target_lat = float(sesi.jadwal.latitude)
        target_lng = float(sesi.jadwal.longitude)

    user_lat = None
    user_lng = None
    if user_lat_str and user_lng_str:
        try:
            user_lat = float(user_lat_str)
            user_lng = float(user_lng_str)
            dist_meters = calculate_haversine_distance(target_lat, target_lng, user_lat, user_lng)
            if dist_meters > 100:
                if not settings.DEBUG:
                    return render(request, 'attendance/partials/_scan_result.html', {
                        'success': False,
                        'message': f'Presensi ditolak! Posisi Anda ({dist_meters} meter) berada di luar batas radius 100 meter dari tempat latihan.'
                    })
        except (ValueError, TypeError):
            pass
    else:
        if not settings.DEBUG:
            return render(request, 'attendance/partials/_scan_result.html', {
                'success': False,
                'message': 'Presensi gagal: Konfirmasi lokasi GPS wajib diaktifkan untuk memastikan posisi Anda dalam radius 100 meter tempat latihan.'
            })

    # Catat Presensi
    with transaction.atomic():
        presensi, created = Presensi.objects.get_or_create(
            sesi=sesi,
            anggota=anggota,
            defaults={
                'status': Presensi.StatusPresensi.HADIR,
                'metode_presensi': Presensi.MetodePresensi.QR_DYNAMIC,
                'waktu_presensi': timezone.now(),
                'user_latitude': user_lat,
                'user_longitude': user_lng,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'device_user_agent': request.META.get('HTTP_USER_AGENT', '')[:250],
            }
        )
        if not created and presensi.status != Presensi.StatusPresensi.HADIR:
            presensi.status = Presensi.StatusPresensi.HADIR
            presensi.metode_presensi = Presensi.MetodePresensi.QR_DYNAMIC
            if user_lat and user_lng:
                presensi.user_latitude = user_lat
                presensi.user_longitude = user_lng
            presensi.waktu_presensi = timezone.now()
            presensi.save()

        sesi.update_attendance_counters()

    return render(request, 'attendance/partials/_scan_result.html', {
        'success': True,
        'message': f'Presensi Berhasil! Selamat berlatih, {user.get_full_name() or user.username}.',
        'sesi': sesi,
        'presensi': presensi,
    })


@login_required
@require_POST
def submit_face_scan(request):
    """
    Core Feature (PRD 3.3.1): AI Biometric Face Recognition Attendance
    - Menerima 128-d face embedding descriptor dari face-api.js client-side.
    - Menerima snapshot foto bukti kehadiran (base64).
    - Memvalidasi batas radius 100 meter tempat latihan (Geofence).
    - Auto-Registration: Jika belum ada referensi wajah, otomatis simpan descriptor & update avatar.
    - Biometric Matching: Jika sudah terdaftar, verifikasi jarak Euclidean (toleransi <= 0.60).
    - Menyimpan presensi HADIR, snapshot wajah, dan mengupdate counter sesi.
    """
    user = request.user
    try:
        anggota = user.anggota_profile
    except AnggotaProfile.DoesNotExist:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Akun kamu bukan profil pesilat aktif.'
        })

    sesi_id = request.POST.get('sesi_id')
    sesi = None
    if sesi_id:
        sesi = SesiLatihan.objects.filter(id=sesi_id, status=SesiLatihan.StatusSesi.DIBUKA).first()
    else:
        sesi = SesiLatihan.objects.filter(status=SesiLatihan.StatusSesi.DIBUKA).order_by('-jam_buka').first()

    if not sesi:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Tidak ada sesi latihan yang sedang dibuka saat ini.'
        })

    # 1. Validasi Radius Lokasi (Maksimal 100 Meter)
    user_lat_str = request.POST.get('user_latitude', '').strip()
    user_lng_str = request.POST.get('user_longitude', '').strip()

    target_lat = DEFAULT_DOJO_LAT
    target_lng = DEFAULT_DOJO_LNG
    if sesi.latitude_aktual and sesi.longitude_aktual:
        target_lat = float(sesi.latitude_aktual)
        target_lng = float(sesi.longitude_aktual)
    elif sesi.jadwal and sesi.jadwal.latitude and sesi.jadwal.longitude:
        target_lat = float(sesi.jadwal.latitude)
        target_lng = float(sesi.jadwal.longitude)

    user_lat = None
    user_lng = None
    if user_lat_str and user_lng_str:
        try:
            user_lat = float(user_lat_str)
            user_lng = float(user_lng_str)
            dist_meters = calculate_haversine_distance(target_lat, target_lng, user_lat, user_lng)
            if dist_meters > 100:
                if not settings.DEBUG:
                    return render(request, 'attendance/partials/_scan_result.html', {
                        'success': False,
                        'message': f'Presensi Biometrik ditolak! Posisi Anda ({dist_meters} meter) berada di luar batas radius 100 meter dari tempat latihan.'
                    })
        except (ValueError, TypeError):
            pass
    else:
        if not settings.DEBUG:
            return render(request, 'attendance/partials/_scan_result.html', {
                'success': False,
                'message': 'Presensi gagal: Konfirmasi lokasi GPS wajib diaktifkan untuk memastikan posisi Anda dalam radius 100 meter tempat latihan.'
            })

    # 2. Parsing Biometric Descriptor (128-d Vector)
    descriptor_str = request.POST.get('face_descriptor', '').strip()
    submitted_descriptor = None
    if descriptor_str:
        try:
            parsed = json.loads(descriptor_str)
            if isinstance(parsed, list) and len(parsed) == 128:
                submitted_descriptor = [float(x) for x in parsed]
        except Exception:
            submitted_descriptor = None

    if not submitted_descriptor:
        return render(request, 'attendance/partials/_scan_result.html', {
            'success': False,
            'message': 'Gagal mengekstrak data biometrik wajah. Pastikan wajah berada tepat di dalam reticle oval kamera dengan pencahayaan cukup.'
        })

    # 3. Snapshot Foto Biometrik Base64
    snapshot_b64 = request.POST.get('face_snapshot', '').strip()
    snapshot_file = None
    if snapshot_b64:
        try:
            format_header, img_data = snapshot_b64.split(';base64,') if ';base64,' in snapshot_b64 else ('', snapshot_b64)
            ext = 'jpg' if ('jpeg' in format_header or 'jpg' in format_header) else 'png'
            decoded_bytes = base64.b64decode(img_data)
            filename = f"face_{anggota.user.id}_{int(time.time())}.{ext}"
            snapshot_file = ContentFile(decoded_bytes, name=filename)
        except Exception:
            snapshot_file = None

    # 4. Auto-Registration (Enrollment Pertama) vs Biometric Matching (1:1 Verification)
    is_auto_enrollment = False
    face_distance = 0.0

    if not anggota.has_face_registered:
        # AUTO-ENROLLMENT WAJAH PERTAMA KALI
        is_auto_enrollment = True
        anggota.face_descriptor = submitted_descriptor
        anggota.face_registered_at = timezone.now()
        anggota.save(update_fields=['face_descriptor', 'face_registered_at'])

        # Jika foto profil user masih kosong, gunakan snapshot wajah ini
        if not user.avatar and snapshot_file:
            user.avatar = snapshot_file
            user.save(update_fields=['avatar'])
    else:
        # VERIFIKASI BIOMETRIK 1:1 SERVER-SIDE (Proteksi Ganda)
        face_distance = calculate_euclidean_distance(submitted_descriptor, anggota.face_descriptor)
        # Ambang batas toleransi server-side <= 0.60
        if face_distance > 0.60:
            return render(request, 'attendance/partials/_scan_result.html', {
                'success': False,
                'message': f'Verifikasi Biometrik Gagal! Wajah di kamera tidak cocok dengan profil biometrik wajah terdaftar Anda (Jarak: {face_distance:.2f}, toleransi maks: 0.60).'
            })

    # 5. Catat Presensi Biometrik HADIR
    with transaction.atomic():
        presensi, created = Presensi.objects.get_or_create(
            sesi=sesi,
            anggota=anggota,
            defaults={
                'status': Presensi.StatusPresensi.HADIR,
                'metode_presensi': Presensi.MetodePresensi.FACE_SCAN,
                'waktu_presensi': timezone.now(),
                'user_latitude': user_lat,
                'user_longitude': user_lng,
                'ip_address': request.META.get('REMOTE_ADDR'),
                'device_user_agent': request.META.get('HTTP_USER_AGENT', '')[:250],
                'face_distance': face_distance,
            }
        )
        if not created:
            presensi.status = Presensi.StatusPresensi.HADIR
            presensi.metode_presensi = Presensi.MetodePresensi.FACE_SCAN
            if user_lat and user_lng:
                presensi.user_latitude = user_lat
                presensi.user_longitude = user_lng
            presensi.face_distance = face_distance
            presensi.waktu_presensi = timezone.now()

        if snapshot_file:
            presensi.foto_face_scan = snapshot_file
        presensi.save()

        sesi.update_attendance_counters()

    accuracy_pct = max(0, min(100, round((1.0 - (face_distance / 0.60)) * 100))) if not is_auto_enrollment else 100

    pesan = (
        f'Wajah Berhasil Didaftarkan & Presensi Sukses! Selamat datang pendekar, {user.get_full_name() or user.username}.'
        if is_auto_enrollment else
        f'Verifikasi Wajah Biometrik Berhasil! (Akurasi: {accuracy_pct}%). Presensi Hadir tercatat untuk {user.get_full_name() or user.username}.'
    )

    return render(request, 'attendance/partials/_scan_result.html', {
        'success': True,
        'message': pesan,
        'sesi': sesi,
        'presensi': presensi,
        'is_face_scan': True,
        'is_auto_enrollment': is_auto_enrollment,
        'accuracy_pct': accuracy_pct,
    })


@login_required
def permit_create(request):
    """
    Form pengajuan izin / sakit bagi pesilat
    """
    try:
        anggota = request.user.anggota_profile
    except AnggotaProfile.DoesNotExist:
        messages.error(request, "Hanya pesilat yang dapat mengajukan surat izin.")
        return redirect('core:dashboard')

    today = timezone.localdate()
    sesi_list = SesiLatihan.objects.filter(status=SesiLatihan.StatusSesi.DIBUKA)

    if request.method == 'POST':
        sesi_id = request.POST.get('sesi_id')
        status = request.POST.get('status', Presensi.StatusPresensi.IZIN)
        alasan = request.POST.get('catatan_alasan', '').strip()
        bukti_file = request.FILES.get('bukti_foto')

        sesi = get_object_or_404(SesiLatihan, id=sesi_id)

        presensi, _ = Presensi.objects.update_or_create(
            sesi=sesi,
            anggota=anggota,
            defaults={
                'status': status,
                'metode_presensi': Presensi.MetodePresensi.MANUAL_PELATIH,
                'catatan_alasan': alasan,
                'bukti_foto': bukti_file,
                'waktu_presensi': timezone.now(),
                'is_verified': False,  # Menunggu verifikasi pelatih
            }
        )
        messages.success(request, "Surat izin berhasil diajukan dan sedang menunggu persetujuan pelatih.")
        return redirect('core:dashboard')

    return render(request, 'attendance/permit_create.html', {'sesi_list': sesi_list})


@login_required
def export_attendance_excel(request, session_id):
    """
    Ekspor rekapitulasi presensi sesi ke file Excel (.xlsx)
    """
    sesi = get_object_or_404(SesiLatihan.objects.select_related('pelatih', 'jadwal'), id=session_id)
    presensi_list = sesi.daftar_presensi.select_related('anggota__user', 'anggota__sabuk_saat_ini').order_by('anggota__user__first_name')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Presensi"

    # Header Styling
    header_fill = PatternFill(start_color="8A1C14", end_color="8A1C14", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=16, bold=True, color="8A1C14")
    border_thin = Border(
        left=Side(style='thin', color='D8C2BE'),
        right=Side(style='thin', color='D8C2BE'),
        top=Side(style='thin', color='D8C2BE'),
        bottom=Side(style='thin', color='D8C2BE')
    )

    # Sheet Header
    ws.merge_cells("A1:G1")
    ws["A1"] = "SILATTRACK - REKAPITULASI PRESENSI EKSTRAKURIKULER PENCAK SILAT"
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center")

    ws["A3"] = "Tipe Sesi:"
    ws["B3"] = sesi.get_tipe_sesi_display()
    ws["A4"] = "Tanggal Latihan:"
    ws["B4"] = sesi.tanggal.strftime("%d-%m-%Y")
    ws["A5"] = "Pelatih:"
    ws["B5"] = sesi.pelatih.get_full_name() or sesi.pelatih.username
    ws["A6"] = "Total Hadir:"
    ws["B6"] = sesi.total_hadir

    for r in range(3, 7):
        ws[f"A{r}"].font = Font(bold=True)

    # Columns
    headers = ["No", "NISN", "Nama Pesilat", "Kelas", "Sabuk", "Status", "Waktu Presensi"]
    row_idx = 8
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=row_idx, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Rows
    for idx, p in enumerate(presensi_list, 1):
        row_idx += 1
        ws.cell(row=row_idx, column=1, value=idx).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=2, value=p.anggota.nisn).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=3, value=p.anggota.user.get_full_name() or p.anggota.user.username)
        ws.cell(row=row_idx, column=4, value=p.anggota.kelas_sekolah).alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=5, value=p.anggota.sabuk_saat_ini.nama_sabuk if p.anggota.sabuk_saat_ini else "-")
        status_cell = ws.cell(row=row_idx, column=6, value=p.get_status_display())
        status_cell.alignment = Alignment(horizontal="center")
        ws.cell(row=row_idx, column=7, value=p.waktu_presensi.strftime("%H:%M:%S")).alignment = Alignment(horizontal="center")

        # Borders
        for c in range(1, 8):
            ws.cell(row=row_idx, column=c).border = border_thin

    # Column Widths
    from openpyxl.utils import get_column_letter
    for col_idx in range(1, 8):
        col_letter = get_column_letter(col_idx)
        max_len = max(len(str(ws.cell(row=r, column=col_idx).value or '')) for r in range(8, row_idx + 1)) if row_idx >= 8 else 10
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Presensi_Silat_{sesi.tanggal.strftime("%Y%m%d")}_{sesi.id.hex[:6]}.xlsx'
    wb.save(response)
    return response


# ==============================================================================
# FITUR CETAK LAPORAN BULANAN & TAHUNAN (ADMIN & PELATIH)
# ==============================================================================

def _get_report_data(request):
    """
    Helper untuk menghimpun data analitik laporan presensi bulanan/tahunan:
    - Periode Bulanan / Tahunan
    - Matriks Kehadiran Anggota (Hadir, Izin, Sakit, Alpa, %, Status UKT)
    - Ringkasan Eksekutif Kehadiran
    - Log Sesi Latihan & Materi yang Diajarkan
    - Data Grafik Chart.js
    """
    today = timezone.localdate()
    periode_tipe = request.GET.get('periode_tipe', 'bulanan')

    try:
        tahun = int(request.GET.get('tahun', today.year))
    except (ValueError, TypeError):
        tahun = today.year

    try:
        bulan = int(request.GET.get('bulan', today.month))
    except (ValueError, TypeError):
        bulan = today.month

    bulan_names = {
        1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
        5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
        9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
    }

    if periode_tipe == 'tahunan':
        sesi_qs = SesiLatihan.objects.filter(
            tanggal__year=tahun
        ).select_related('pelatih', 'jadwal').order_by('tanggal', 'jam_buka')
        periode_label = f"Tahun {tahun}"
        periode_sub = f"Tahun Ajaran / Kalender {tahun}"
    else:
        periode_tipe = 'bulanan'
        sesi_qs = SesiLatihan.objects.filter(
            tanggal__year=tahun,
            tanggal__month=bulan
        ).select_related('pelatih', 'jadwal').order_by('tanggal', 'jam_buka')
        nama_bulan = bulan_names.get(bulan, 'Bulan')
        periode_label = f"{nama_bulan} {tahun}"
        periode_sub = f"Bulan {nama_bulan} {tahun}"

    total_sesi = sesi_qs.count()

    # Filter Sekolah Binaan
    sekolah_id = (request.GET.get('sekolah_id') or request.GET.get('sekolah') or '').strip()
    sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')
    selected_sekolah = None
    if sekolah_id:
        selected_sekolah = sekolah_list.filter(id=sekolah_id).first()

    # Seluruh pesilat aktif (terfilter sekolah jika dipilih)
    members = AnggotaProfile.objects.filter(
        status_keanggotaan=AnggotaProfile.MembershipStatus.AKTIF
    ).select_related('user', 'sabuk_saat_ini', 'kategori_fokus', 'sekolah').order_by('sabuk_saat_ini__urutan_tingkat', 'user__first_name')

    if selected_sekolah:
        members = members.filter(sekolah=selected_sekolah)

    total_pesilat = members.count()

    # Data Penandatangan Laporan (Admin/Pembina, Pelatih, Kepala Sekolah)
    admin_id = request.GET.get('admin_id')
    pelatih_id = request.GET.get('pelatih_id')

    # Default Kepala Sekolah disesuaikan dengan sekolah yang dipilih atau default umum
    if selected_sekolah:
        default_ks_nama = selected_sekolah.nama_kepala_sekolah or 'Drs. H. Mulyadi, M.M'
        default_ks_nip = selected_sekolah.nip_kepala_sekolah or '19720412 199802 1 003'
        default_ks_jabatan = selected_sekolah.jabatan_kepala_sekolah or f"Kepala {selected_sekolah.nama_sekolah}"
    else:
        default_ks_nama = 'Drs. H. Mulyadi, M.M'
        default_ks_nip = '19720412 199802 1 003'
        default_ks_jabatan = "Kepala Sekolah / Waka Kesiswaan"

    kepala_sekolah = request.GET.get('kepala_sekolah', '').strip() or default_ks_nama
    kepala_sekolah_nip = (request.GET.get('kepala_sekolah_nip') or request.GET.get('nip_kepala_sekolah', '')).strip() or default_ks_nip
    kepala_sekolah_jabatan = request.GET.get('kepala_sekolah_jabatan', '').strip() or default_ks_jabatan
    admin_nip = request.GET.get('admin_nip', '19850315 201001 1 012').strip()

    admin_qs = User.objects.filter(role=User.Role.ADMIN).order_by('first_name', 'username')
    pelatih_qs = PelatihProfile.objects.select_related('user').order_by('user__first_name', 'user__username')

    selected_admin = None
    if admin_id:
        selected_admin = admin_qs.filter(id=admin_id).first()
    if not selected_admin:
        if request.user.is_authenticated and request.user.is_admin_role:
            selected_admin = request.user
        else:
            selected_admin = admin_qs.first()

    admin_nama = selected_admin.get_full_name() or selected_admin.username if selected_admin else "Dian Haerudin, S.Pd"

    selected_pelatih = None
    if pelatih_id:
        selected_pelatih = pelatih_qs.filter(user_id=pelatih_id).first()
    if not selected_pelatih:
        if request.user.is_authenticated and request.user.is_pelatih_role and hasattr(request.user, 'pelatih_profile'):
            selected_pelatih = request.user.pelatih_profile
        else:
            selected_pelatih = pelatih_qs.first()

    pelatih_nama = selected_pelatih.user.get_full_name() or selected_pelatih.user.username if selected_pelatih else "Joko Pratama, S.Or"
    pelatih_reg = selected_pelatih.nomor_registrasi if (selected_pelatih and selected_pelatih.nomor_registrasi) else "PEL-IPSI-2024-001"


    # Presensi dalam rentang sesi periode ini
    presensi_qs = Presensi.objects.filter(sesi__in=sesi_qs)
    total_hadir = presensi_qs.filter(status=Presensi.StatusPresensi.HADIR).count()
    total_izin = presensi_qs.filter(status=Presensi.StatusPresensi.IZIN).count()
    total_sakit = presensi_qs.filter(status=Presensi.StatusPresensi.SAKIT).count()
    total_alpa_explicit = presensi_qs.filter(status=Presensi.StatusPresensi.ALPA).count()

    pending_delete_map = {
        p.anggota_id: p
        for p in PengajuanHapusAnggota.objects.filter(
            status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
        ).select_related('diajukan_oleh')
    }

    member_matrix = []
    total_unrecorded_alpa = 0

    for idx, m in enumerate(members, 1):
        m_hadir = presensi_qs.filter(anggota=m, status=Presensi.StatusPresensi.HADIR).count()
        m_izin = presensi_qs.filter(anggota=m, status=Presensi.StatusPresensi.IZIN).count()
        m_sakit = presensi_qs.filter(anggota=m, status=Presensi.StatusPresensi.SAKIT).count()
        m_alpa = presensi_qs.filter(anggota=m, status=Presensi.StatusPresensi.ALPA).count()

        # Sesi yang tidak dihadiri tanpa surat izin diperhitungkan sebagai alpa
        recorded = m_hadir + m_izin + m_sakit + m_alpa
        if total_sesi > recorded:
            missing = total_sesi - recorded
            m_alpa += missing
            total_unrecorded_alpa += missing

        pct = round((m_hadir / total_sesi * 100)) if total_sesi > 0 else 0
        min_ukt = m.sabuk_saat_ini.min_kehadiran_ukt if m.sabuk_saat_ini else 75
        is_eligible = pct >= min_ukt

        if pct >= min_ukt:
            status_ukt = 'AMAN'
            status_label = 'Memenuhi Syarat UKT'
            status_color = 'emerald'
        elif pct >= max(0, min_ukt - 20):
            status_ukt = 'PERINGATAN'
            status_label = 'Perlu Ditingkatkan'
            status_color = 'amber'
        else:
            status_ukt = 'KRITIS'
            status_label = 'Di Bawah Target'
            status_color = 'red'

        # Kriteria Anggota Kurang Aktif: persentase kehadiran di bawah 50% atau status UKT Kritis
        is_kurang_aktif = (pct < 50) or (status_ukt == 'KRITIS')
        pending_del = pending_delete_map.get(m.user_id)

        member_matrix.append({
            'no': idx,
            'anggota': m,
            'hadir': m_hadir,
            'izin': m_izin,
            'sakit': m_sakit,
            'alpa': m_alpa,
            'persentase': pct,
            'min_ukt': min_ukt,
            'is_eligible': is_eligible,
            'status_ukt': status_ukt,
            'status_label': status_label,
            'status_color': status_color,
            'is_kurang_aktif': is_kurang_aktif,
            'pending_delete': pending_del,
            'has_pending_delete': bool(pending_del),
        })

    total_alpa = total_alpa_explicit + total_unrecorded_alpa
    total_ekspektasi = total_pesilat * total_sesi
    attendance_rate = round((total_hadir / total_ekspektasi * 100)) if total_ekspektasi > 0 else 0

    # Donut Chart Data: Distribusi Presensi
    donut_chart_data = {
        'labels': ['Hadir', 'Izin', 'Sakit', 'Alpa'],
        'data': [total_hadir, total_izin, total_sakit, total_alpa]
    }

    # Trend Chart Data: Per Sesi dalam Periode Ini
    trend_labels = []
    trend_hadir = []
    trend_izin_sakit = []
    trend_alpa = []

    for s in sesi_qs:
        trend_labels.append(s.tanggal.strftime('%d/%m'))
        s_hadir = s.daftar_presensi.filter(status=Presensi.StatusPresensi.HADIR).count()
        s_izin_sakit = s.daftar_presensi.filter(status__in=[Presensi.StatusPresensi.IZIN, Presensi.StatusPresensi.SAKIT]).count()
        s_alpa = s.daftar_presensi.filter(status=Presensi.StatusPresensi.ALPA).count()
        trend_hadir.append(s_hadir)
        trend_izin_sakit.append(s_izin_sakit)
        trend_alpa.append(s_alpa)

    trend_chart_data = {
        'labels': trend_labels,
        'hadir': trend_hadir,
        'izin_sakit': trend_izin_sakit,
        'alpa': trend_alpa,
    }

    available_years = list(range(today.year - 2, today.year + 2))

    return {
        'periode_tipe': periode_tipe,
        'bulan': bulan,
        'tahun': tahun,
        'nama_bulan': bulan_names.get(bulan, ''),
        'bulan_names': bulan_names,
        'available_years': available_years,
        'periode_label': periode_label,
        'periode_sub': periode_sub,
        'sesi_list': sesi_qs,
        'total_sesi': total_sesi,
        'total_pesilat': total_pesilat,
        'total_hadir': total_hadir,
        'total_izin': total_izin,
        'total_sakit': total_sakit,
        'total_alpa': total_alpa,
        'attendance_rate': attendance_rate,
        'member_matrix': member_matrix,
        'donut_chart_json': json.dumps(donut_chart_data),
        'trend_chart_json': json.dumps(trend_chart_data),
        'today': today,
        # Penandatangan Laporan Resmi
        'admin_list': admin_qs,
        'pelatih_list': pelatih_qs,
        'selected_admin': selected_admin,
        'selected_pelatih': selected_pelatih,
        'admin_id': str(selected_admin.id) if selected_admin else '',
        'pelatih_id': str(selected_pelatih.user_id) if selected_pelatih else '',
        'admin_nama': admin_nama,
        'admin_nip': admin_nip,
        'admin_jabatan': "Pembina Ekstrakurikuler Silat",
        'pelatih_nama': pelatih_nama,
        'pelatih_reg': pelatih_reg,
        'pelatih_jabatan': "Pelatih Utama Silat",
        # Data Asal Sekolah & Tanda Tangan Kepala Sekolah
        'sekolah_list': sekolah_list,
        'selected_sekolah': selected_sekolah,
        'sekolah_id': str(selected_sekolah.id) if selected_sekolah else '',
        'sekolah_nama': selected_sekolah.nama_sekolah if selected_sekolah else 'Seluruh Sekolah',
        'kepala_sekolah_nama': kepala_sekolah,
        'kepala_sekolah_nip': kepala_sekolah_nip,
        'kepala_sekolah_jabatan': kepala_sekolah_jabatan,
    }


@login_required
def attendance_report_index(request):
    """
    Dashboard Kontrol & Pratinjau Cetak Laporan Presensi Ekstrakurikuler Silat:
    Menyediakan filter periode bulanan/tahunan, filter asal sekolah binaan,
    pengeditan tanda tangan Kepala Sekolah, grafik ringkasan metrik, dan tabel rekapitulasi.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak: Fitur laporan hanya untuk Admin dan Pelatih.")
        return redirect('core:dashboard')

    # Fitur Simpan Pembaruan Data Tanda Tangan Kepala Sekolah ke Database
    if request.method == 'POST' and request.POST.get('action') == 'save_kepala_sekolah':
        sekolah_target_id = request.POST.get('sekolah_id') or request.POST.get('sekolah')
        ks_nama = request.POST.get('kepala_sekolah', '').strip()
        ks_nip = request.POST.get('kepala_sekolah_nip', '').strip()
        ks_jabatan = request.POST.get('kepala_sekolah_jabatan', '').strip()
        if sekolah_target_id:
            target_sekolah = Sekolah.objects.filter(id=sekolah_target_id).first()
            if target_sekolah:
                if ks_nama:
                    target_sekolah.nama_kepala_sekolah = ks_nama
                if ks_nip:
                    target_sekolah.nip_kepala_sekolah = ks_nip
                if ks_jabatan:
                    target_sekolah.jabatan_kepala_sekolah = ks_jabatan
                target_sekolah.save()
                messages.success(
                    request,
                    f"Data tanda tangan Kepala Sekolah untuk {target_sekolah.nama_sekolah} berhasil diperbarui dan disimpan sebagai default!"
                )
        else:
            messages.info(request, "Pilih salah satu sekolah terlebih dahulu untuk menyimpan data Kepala Sekolah default.")

    context = _get_report_data(request)
    return render(request, 'attendance/report_index.html', context)



@login_required
def attendance_report_print(request):
    """
    Halaman Cetak Dokumen Resmi (Print / Save as PDF):
    Didesain khusus dengan standar dokumen resmi dinas sekolah: Kop Surat, garis pembatas,
    grafik analitik, tabel rekapitulasi lengkap, log materi kurikulum, dan lembar 3 tanda tangan.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak: Fitur cetak laporan hanya untuk Admin dan Pelatih.")
        return redirect('core:dashboard')

    context = _get_report_data(request)
    return render(request, 'attendance/report_print.html', context)


@login_required
def attendance_report_export_excel(request):
    """
    Ekspor Dokumen Laporan Rekapitulasi Presensi Lengkap ke Format Spreadsheet Excel (.xlsx)
    Berisi Sheet 1 (Rekapitulasi Anggota) dan Sheet 2 (Log Sesi & Materi Latihan).
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        return HttpResponse("Akses ditolak: Hanya untuk Admin dan Pelatih.", status=403)

    data = _get_report_data(request)

    wb = openpyxl.Workbook()

    # Styling Palette: SilatTrack Crimson Maroon & Soft Borders
    header_fill = PatternFill(start_color="8A1C14", end_color="8A1C14", fill_type="solid")
    sub_fill = PatternFill(start_color="FCEAE6", end_color="FCEAE6", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Calibri", size=15, bold=True, color="8A1C14")
    bold_font = Font(name="Calibri", size=10, bold=True)
    regular_font = Font(name="Calibri", size=10)
    border_thin = Border(
        left=Side(style='thin', color='D8C2BE'),
        right=Side(style='thin', color='D8C2BE'),
        top=Side(style='thin', color='D8C2BE'),
        bottom=Side(style='thin', color='D8C2BE')
    )

    # --------------------------------------------------------------------------
    # SHEET 1: Rekapitulasi Kehadiran Pesilat
    # --------------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Rekap Kehadiran Pesilat"

    ws1.merge_cells("A1:L1")
    ws1["A1"] = "LAPORAN REKAPITULASI PRESENSI EKSTRAKURIKULER PENCAK SILAT"
    ws1["A1"].font = title_font
    ws1["A1"].alignment = Alignment(horizontal="center", vertical="center")

    school_info = f" • SEKOLAH: {data['selected_sekolah'].nama_sekolah.upper()}" if data.get('selected_sekolah') else ""
    ws1.merge_cells("A2:L2")
    ws1["A2"] = f"PERIODE: {data['periode_label'].upper()} ({data['periode_sub']}){school_info}"
    ws1["A2"].font = Font(name="Calibri", size=11, bold=True, color="534341")
    ws1["A2"].alignment = Alignment(horizontal="center", vertical="center")

    # Metadata Ringkasan
    ws1["A4"] = "Periode Laporan:"
    ws1["B4"] = data['periode_label']
    ws1["A5"] = "Total Sesi Terlaksana:"
    ws1["B5"] = f"{data['total_sesi']} Pertemuan"
    ws1["A6"] = "Total Pesilat Aktif:"
    ws1["B6"] = f"{data['total_pesilat']} Siswa"
    ws1["A7"] = "Rata-rata Kehadiran:"
    ws1["B7"] = f"{data['attendance_rate']}%"

    ws1["D4"] = "Total Hadir:"
    ws1["E4"] = data['total_hadir']
    ws1["D5"] = "Total Izin:"
    ws1["E5"] = data['total_izin']
    ws1["D6"] = "Total Sakit:"
    ws1["E6"] = data['total_sakit']
    ws1["D7"] = "Total Alpa:"
    ws1["E7"] = data['total_alpa']

    for r in range(4, 8):
        ws1[f"A{r}"].font = bold_font
        ws1[f"D{r}"].font = bold_font

    # Headers Tabel Rekap Pesilat (Termasuk Asal Sekolah)
    headers1 = [
        "No", "NISN", "Nama Lengkap Pesilat", "Asal Sekolah", "Kelas", "Sabuk",
        "Hadir (H)", "Izin (I)", "Sakit (S)", "Alpa (A)",
        "Persentase (%)", "Kualifikasi UKT"
    ]
    row_idx = 9
    for col_idx, h in enumerate(headers1, 1):
        c = ws1.cell(row=row_idx, column=col_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")

    for item in data['member_matrix']:
        row_idx += 1
        ws1.cell(row=row_idx, column=1, value=item['no']).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=2, value=item['anggota'].nisn).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=3, value=item['anggota'].user.get_full_name() or item['anggota'].user.username)
        ws1.cell(row=row_idx, column=4, value=item['anggota'].sekolah.nama_sekolah if item['anggota'].sekolah else "-").alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=5, value=item['anggota'].kelas_sekolah).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=6, value=item['anggota'].sabuk_saat_ini.nama_sabuk if item['anggota'].sabuk_saat_ini else "-").alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=7, value=item['hadir']).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=8, value=item['izin']).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=9, value=item['sakit']).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=10, value=item['alpa']).alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=11, value=f"{item['persentase']}%").alignment = Alignment(horizontal="center")
        ws1.cell(row=row_idx, column=12, value=item['status_label']).alignment = Alignment(horizontal="center")

        for col_idx in range(1, 13):
            cell = ws1.cell(row=row_idx, column=col_idx)
            cell.font = regular_font
            cell.border = border_thin

    # Signatures (Pembina Eskul, Pelatih Utama, Kepala Sekolah)
    sign_row = row_idx + 3
    ws1.cell(row=sign_row, column=2, value="Pembina Ekstrakurikuler,").font = bold_font
    ws1.cell(row=sign_row, column=6, value="Pelatih Utama Silat,").font = bold_font
    ws1.cell(row=sign_row, column=10, value=f"Mengetahui, {data['kepala_sekolah_jabatan']},").font = bold_font

    ws1.cell(row=sign_row + 4, column=2, value=data['admin_nama']).font = bold_font
    ws1.cell(row=sign_row + 5, column=2, value=f"NIP. {data['admin_nip']}").font = regular_font

    ws1.cell(row=sign_row + 4, column=6, value=data['pelatih_nama']).font = bold_font
    ws1.cell(row=sign_row + 5, column=6, value=f"Reg. IPSI: {data['pelatih_reg']}").font = regular_font

    ws1.cell(row=sign_row + 4, column=10, value=data['kepala_sekolah_nama']).font = bold_font
    ws1.cell(row=sign_row + 5, column=10, value=f"NIP. {data['kepala_sekolah_nip']}").font = regular_font

    # Column Widths Auto-fit
    from openpyxl.utils import get_column_letter
    for col_idx in range(1, 13):
        col_letter = get_column_letter(col_idx)
        max_len = max(len(str(ws1.cell(row=r, column=col_idx).value or '')) for r in range(9, row_idx + 1)) if row_idx >= 9 else 10
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 12)

    # --------------------------------------------------------------------------
    # SHEET 2: Log Sesi & Materi Latihan
    # --------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="Log Sesi Latihan")

    ws2.merge_cells("A1:G1")
    ws2["A1"] = f"LOG PERTEMUAN & MATERI LATIHAN - PERIODE {data['periode_label'].upper()}"
    ws2["A1"].font = title_font
    ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")

    headers2 = ["No", "Tanggal", "Waktu", "Tipe Latihan", "Pelatih Pengampu", "Materi Latihan yang Disampaikan", "Pesilat Hadir"]
    row_idx2 = 3
    for col_idx, h in enumerate(headers2, 1):
        c = ws2.cell(row=row_idx2, column=col_idx, value=h)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center")

    for idx, s in enumerate(data['sesi_list'], 1):
        row_idx2 += 1
        ws2.cell(row=row_idx2, column=1, value=idx).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx2, column=2, value=s.tanggal.strftime("%d-%m-%Y")).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx2, column=3, value=s.jam_buka.strftime("%H:%M WIB")).alignment = Alignment(horizontal="center")
        ws2.cell(row=row_idx2, column=4, value=s.get_tipe_sesi_display())
        ws2.cell(row=row_idx2, column=5, value=s.pelatih.get_full_name() or s.pelatih.username)
        ws2.cell(row=row_idx2, column=6, value=s.materi_latihan or "Latihan teknik rutin")
        ws2.cell(row=row_idx2, column=7, value=s.total_hadir).alignment = Alignment(horizontal="center")

        for col_idx in range(1, 8):
            cell = ws2.cell(row=row_idx2, column=col_idx)
            cell.font = regular_font
            cell.border = border_thin

    for col_idx in range(1, 8):
        col_letter = get_column_letter(col_idx)
        max_len = max(len(str(ws2.cell(row=r, column=col_idx).value or '')) for r in range(3, row_idx2 + 1)) if row_idx2 >= 3 else 10
        ws2.column_dimensions[col_letter].width = max(max_len + 4, 14)

    # Response Streaming
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    clean_period = data['periode_label'].replace(" ", "_")
    school_slug = f"_{data['selected_sekolah'].nama_sekolah.replace(' ', '_')}" if data.get('selected_sekolah') else ""
    response['Content-Disposition'] = f'attachment; filename=Laporan_Presensi_Silat_{data["periode_tipe"]}_{clean_period}{school_slug}.xlsx'
    wb.save(response)
    return response

