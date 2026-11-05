import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import AnggotaProfile, PelatihProfile, RiwayatKenaikanSabuk, PengajuanHapusAnggota
from apps.core.models import TingkatSabuk, KategoriTanding, Sekolah
from apps.attendance.models import Presensi, SesiLatihan
from apps.accounts.models import User



@login_required
def member_list(request):
    if request.user.is_anggota_role:
        messages.error(request, "Akses ditolak. Fitur direktori anggota hanya dapat diakses oleh Admin atau Pelatih.")
        return redirect('core:dashboard')

    sabuk_id = request.GET.get('sabuk', '')
    sekolah_id = request.GET.get('sekolah', '').strip()
    query = request.GET.get('q', '').strip()
    tab = request.GET.get('tab', 'anggota').strip()

    members = AnggotaProfile.objects.all().select_related('user', 'sabuk_saat_ini', 'kategori_fokus', 'sekolah')
    coaches = PelatihProfile.objects.all().select_related('user')

    if sabuk_id:
        members = members.filter(sabuk_saat_ini_id=sabuk_id)
    if sekolah_id and sekolah_id.lower() not in ('none', 'null', 'undefined', ''):
        if sekolah_id.isdigit():
            members = members.filter(sekolah_id=int(sekolah_id))
        else:
            members = members.filter(sekolah__nama_sekolah__iexact=sekolah_id)
    if query:
        members = members.filter(
            user__first_name__icontains=query
        ) | members.filter(
            user__last_name__icontains=query
        ) | members.filter(
            nisn__icontains=query
        ) | members.filter(
            kelas_sekolah__icontains=query
        ) | members.filter(
            sekolah__nama_sekolah__icontains=query
        )


        coaches = coaches.filter(
            user__first_name__icontains=query
        ) | coaches.filter(
            user__last_name__icontains=query
        ) | coaches.filter(
            nomor_registrasi__icontains=query
        ) | coaches.filter(
            tingkatan_pendekar__icontains=query
        ) | coaches.filter(
            spesialisasi__icontains=query
        )

    sabuk_list = TingkatSabuk.objects.all().order_by('urutan_tingkat')
    kategori_list = KategoriTanding.objects.all().order_by('nama')
    sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')

    # Pengajuan Hapus Anggota (untuk admin review atau pelatih monitoring)
    pending_delete_requests = PengajuanHapusAnggota.objects.filter(
        status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
    ).select_related('anggota__user', 'anggota__sabuk_saat_ini', 'diajukan_oleh')

    if not request.user.is_admin_role:
        pending_delete_requests = pending_delete_requests.filter(diajukan_oleh=request.user)

    # Menghitung keaktifan kehadiran seluruh pesilat
    total_sesi = SesiLatihan.objects.count()
    pending_delete_map = {
        p.anggota_id: p
        for p in pending_delete_requests
    }

    members_list = list(members)
    kurang_aktif_list = []

    for m in members_list:
        hadir_count = m.riwayat_presensi.filter(status=Presensi.StatusPresensi.HADIR).count()
        pct = round((hadir_count / total_sesi * 100)) if total_sesi > 0 else 0
        min_ukt = m.sabuk_saat_ini.min_kehadiran_ukt if m.sabuk_saat_ini else 75
        m.hadir_count = hadir_count
        m.persentase_hadir = pct
        m.min_kehadiran_ukt = min_ukt
        m.is_kurang_aktif = (pct < 50) or (m.status_keanggotaan == AnggotaProfile.MembershipStatus.NONAKTIF)
        m.pending_delete = pending_delete_map.get(m.user_id)
        m.has_pending_delete = bool(m.pending_delete)

        if m.is_kurang_aktif:
            kurang_aktif_list.append(m)

    total_kurang_aktif = len(kurang_aktif_list)

    if tab == 'kurang_aktif':
        display_members = kurang_aktif_list
    else:
        display_members = members_list

    context = {
        'members': display_members,
        'all_members': members_list,
        'coaches': coaches,
        'total_members': AnggotaProfile.objects.count(),
        'total_coaches': PelatihProfile.objects.count(),
        'total_kurang_aktif': total_kurang_aktif,
        'sabuk_list': sabuk_list,
        'kategori_list': kategori_list,
        'sekolah_list': sekolah_list,
        'selected_sabuk': sabuk_id,
        'selected_sekolah': sekolah_id,
        'query': query,
        'active_tab': tab,
        'pending_delete_requests': pending_delete_requests,
        'total_pending_deletes': pending_delete_requests.count(),
        'total_sesi': total_sesi,
    }
    return render(request, 'members/member_list.html', context)



@login_required
def member_detail(request, user_id):
    if request.user.is_anggota_role and request.user.id != user_id:
        messages.error(request, "Akses ditolak. Anda tidak memiliki izin untuk melihat detail anggota lain.")
        return redirect('core:dashboard')

    profile = get_object_or_404(
        AnggotaProfile.objects.select_related('user', 'sabuk_saat_ini', 'kategori_fokus'),
        user_id=user_id
    )
    
    # Riwayat kenaikan sabuk
    riwayat_sabuk = profile.riwayat_kenaikan_sabuk.select_related('sabuk_asal', 'sabuk_baru', 'penguji_pelatih').order_by('-tanggal_ujian')
    
    # Riwayat absensi
    presensi_list = profile.riwayat_presensi.select_related('sesi').order_by('-waktu_presensi')
    
    total_sesi = SesiLatihan.objects.count()
    hadir_count = presensi_list.filter(status=Presensi.StatusPresensi.HADIR).count()
    izin_count = presensi_list.filter(status=Presensi.StatusPresensi.IZIN).count()
    sakit_count = presensi_list.filter(status=Presensi.StatusPresensi.SAKIT).count()
    alpa_count = presensi_list.filter(status=Presensi.StatusPresensi.ALPA).count()

    recorded_count = hadir_count + izin_count + sakit_count + alpa_count
    if total_sesi > recorded_count:
        alpa_count += (total_sesi - recorded_count)

    persentase_hadir = round((hadir_count / total_sesi * 100)) if total_sesi > 0 else 0
    min_kehadiran_ukt = profile.sabuk_saat_ini.min_kehadiran_ukt if profile.sabuk_saat_ini else 75
    is_eligible_ukt = persentase_hadir >= min_kehadiran_ukt

    member_donut_data = {
        'labels': ['Hadir', 'Izin', 'Sakit', 'Alpa'],
        'data': [hadir_count, izin_count, sakit_count, alpa_count],
    }

    # Trend kumulatif sesi latihan terakhir
    all_sessions = list(SesiLatihan.objects.all().order_by('-tanggal', '-jam_buka')[:7])
    all_sessions.reverse()

    s_labels = []
    s_cum_pct = []
    s_targets = []
    running_hadir = 0
    for idx, s in enumerate(all_sessions, 1):
        s_labels.append(s.tanggal.strftime('%d/%m'))
        p = Presensi.objects.filter(sesi=s, anggota=profile).first()
        if p and p.status == Presensi.StatusPresensi.HADIR:
            running_hadir += 1
        s_cum_pct.append(round((running_hadir / idx) * 100))
        s_targets.append(min_kehadiran_ukt)

    member_trend_data = {
        'labels': s_labels,
        'cumulative_pct': s_cum_pct,
        'target_ukt': s_targets,
    }

    # Cek apakah ada pengajuan izin hapus yang sedang pending untuk anggota ini
    pending_delete = PengajuanHapusAnggota.objects.filter(
        anggota=profile,
        status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
    ).first()

    sabuk_list = TingkatSabuk.objects.all().order_by('urutan_tingkat')
    kategori_list = KategoriTanding.objects.all().order_by('nama')

    context = {
        'profile': profile,
        'riwayat_sabuk': riwayat_sabuk,
        'presensi_list': presensi_list,
        'hadir_count': hadir_count,
        'izin_count': izin_count,
        'sakit_count': sakit_count,
        'alpa_count': alpa_count,
        'persentase_hadir': persentase_hadir,
        'total_sesi': total_sesi,
        'min_kehadiran_ukt': min_kehadiran_ukt,
        'is_eligible_ukt': is_eligible_ukt,
        'member_donut_json': json.dumps(member_donut_data),
        'member_trend_json': json.dumps(member_trend_data),
        'pending_delete': pending_delete,
        'sabuk_list': sabuk_list,
        'kategori_list': kategori_list,
        'sekolah_list': Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah'),
        'status_choices': AnggotaProfile.MembershipStatus.choices,
        'streak': profile.calculate_attendance_streak(),
    }
    return render(request, 'members/member_detail.html', context)


@login_required
@require_POST
def member_edit(request, user_id):
    """
    Fitur Edit Data Anggota Pesilat oleh Admin atau Pelatih.
    Memperbarui identitas akun User (Nama Depan, Nama Belakang, Email, No HP)
    serta profil spesifik eskul (NISN, Sekolah, Kelas, Sabuk, Kategori, Status, Kontak Wali).
    Otomatis terupdate sehingga laporan presensi dan riwayat langsung mengikuti nama baru.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak. Hanya Admin dan Pelatih yang dapat mengedit data anggota.")
        return redirect('members:member_detail', user_id=user_id)

    profile = get_object_or_404(AnggotaProfile.objects.select_related('user', 'sekolah'), user_id=user_id)
    user = profile.user

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone_number = request.POST.get('phone_number', '').strip()
    nisn = request.POST.get('nisn', '').strip()
    sekolah_id = request.POST.get('sekolah_id')
    nama_sekolah_baru = request.POST.get('nama_sekolah_baru', '').strip()
    kelas_sekolah = request.POST.get('kelas_sekolah', '').strip()
    sabuk_id = request.POST.get('sabuk_id')
    kategori_id = request.POST.get('kategori_id')
    status_keanggotaan = request.POST.get('status_keanggotaan', profile.status_keanggotaan)
    nama_wali = request.POST.get('nama_wali', '').strip()
    no_hp_wali = request.POST.get('no_hp_wali', '').strip()

    if not first_name:
        messages.error(request, "Nama depan wajib diisi.")
        return redirect('members:member_detail', user_id=user_id)

    if nisn:
        if len(nisn) != 10 or not nisn.isdigit():
            messages.error(
                request,
                "NISN harus terdiri dari tepat 10 digit angka sesuai standar resmi Kementerian Pendidikan Pusat (Kemdikbudristek) untuk sinkronisasi nilai e-Rapor."
            )
            return redirect('members:member_detail', user_id=user_id)

        if nisn != profile.nisn and AnggotaProfile.objects.filter(nisn=nisn).exclude(user_id=user.id).exists():
            messages.error(request, f"NISN '{nisn}' sudah terdaftar untuk siswa lain.")
            return redirect('members:member_detail', user_id=user_id)

    try:
        with transaction.atomic():
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number = phone_number
            user.save()

            if nisn:
                profile.nisn = nisn
            if kelas_sekolah:
                profile.kelas_sekolah = kelas_sekolah
            profile.status_keanggotaan = status_keanggotaan
            profile.nama_wali = nama_wali
            profile.no_hp_wali = no_hp_wali

            # Asal Sekolah
            if nama_sekolah_baru:
                sekolah_obj, _ = Sekolah.objects.get_or_create(nama_sekolah=nama_sekolah_baru)
                profile.sekolah = sekolah_obj
            elif sekolah_id:
                profile.sekolah = Sekolah.objects.filter(id=sekolah_id).first()
            elif sekolah_id == '':
                profile.sekolah = None

            if sabuk_id:
                profile.sabuk_saat_ini = TingkatSabuk.objects.filter(id=sabuk_id).first()
            if kategori_id:
                profile.kategori_fokus = KategoriTanding.objects.filter(id=kategori_id).first()
            elif kategori_id == '':
                profile.kategori_fokus = None

            profile.save()

        messages.success(request, f"Data anggota '{user.get_full_name() or user.username}' berhasil diperbarui! Identitas terbaru otomatis tersinkronisasi ke seluruh laporan presensi.")
    except Exception as e:
        messages.error(request, f"Gagal memperbarui data anggota: {str(e)}")

    return redirect('members:member_detail', user_id=user_id)



@login_required
@require_POST
def member_delete(request, user_id):
    """
    Fitur Penghapusan Anggota Pesilat:
    - Admin: Dapat menghapus langsung secara permanen.
    - Pelatih: Wajib mengajukan izin ke Admin terlebih dahulu dengan mencantumkan alasan.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak. Anda tidak memiliki wewenang untuk menghapus anggota.")
        return redirect('members:member_list')

    profile = get_object_or_404(AnggotaProfile.objects.select_related('user'), user_id=user_id)
    target_user = profile.user
    nama_lengkap = target_user.get_full_name() or target_user.username
    next_url = request.POST.get('next') or request.GET.get('next')

    # JALUR 1: ADMIN (Bisa hapus langsung)
    if request.user.is_admin_role:
        with transaction.atomic():
            # Hapus user (akan cascade ke AnggotaProfile dan Presensi)
            target_user.delete()

        messages.success(request, f"Anggota pesilat '{nama_lengkap}' beserta seluruh data riwayatnya berhasil dihapus secara permanen.")
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('members:member_list')

    # JALUR 2: PELATIH (Wajib memiliki izin dari Admin)
    else:
        alasan = request.POST.get('alasan_penghapusan', '').strip()
        if not alasan:
            messages.error(request, "Pelatih wajib menyertakan alasan penghapusan anggota untuk persetujuan Admin.")
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('members:member_detail', user_id=user_id)

        # Cek apakah sudah ada pengajuan pending
        existing = PengajuanHapusAnggota.objects.filter(
            anggota=profile,
            status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
        ).first()

        if existing:
            messages.info(request, f"Permohonan izin hapus untuk pesilat '{nama_lengkap}' sudah diajukan sebelumnya dan saat ini sedang menunggu persetujuan Admin.")
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('members:member_detail', user_id=user_id)

        PengajuanHapusAnggota.objects.create(
            anggota=profile,
            diajukan_oleh=request.user,
            alasan=alasan,
            status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
        )

        messages.success(
            request,
            f"Permohonan izin hapus anggota '{nama_lengkap}' berhasil diajukan kepada Admin / Pembina eskul. "
            "Anggota akan dihapus setelah Admin menyetujui permohonan ini."
        )
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect('members:member_detail', user_id=user_id)


@login_required
@require_POST
def approve_delete_request(request, request_id):
    """
    Fitur Persetujuan Permohonan Hapus Anggota (Khusus Admin / Pembina Eskul).
    - Setujui: Anggota dan akun user dihapus permanen.
    - Tolak: Permohonan ditolak dengan catatan.
    """
    if not request.user.is_admin_role:
        messages.error(request, "Akses ditolak. Hanya Admin / Pembina Eskul yang dapat memproses izin penghapusan.")
        return redirect('members:member_list')

    pengajuan = get_object_or_404(PengajuanHapusAnggota.objects.select_related('anggota__user', 'diajukan_oleh'), id=request_id)
    action = request.POST.get('action', '').strip().lower()
    catatan = request.POST.get('catatan_admin', '').strip()
    next_url = request.POST.get('next') or request.GET.get('next')

    nama_anggota = pengajuan.anggota.user.get_full_name() or pengajuan.anggota.user.username
    nama_pelatih = pengajuan.diajukan_oleh.get_full_name() or pengajuan.diajukan_oleh.username

    if action == 'setuju':
        with transaction.atomic():
            pengajuan.status = PengajuanHapusAnggota.StatusPengajuan.DISETUJUI
            pengajuan.disetujui_oleh = request.user
            pengajuan.catatan_admin = catatan
            pengajuan.save()

            # Hapus akun User target (cascade profil & presensi)
            target_user = pengajuan.anggota.user
            target_user.delete()

        messages.success(request, f"Izin penghapusan anggota '{nama_anggota}' (diajukan oleh {nama_pelatih}) telah disetujui. Data anggota telah resmi dihapus dari sistem.")
    elif action == 'tolak':
        pengajuan.status = PengajuanHapusAnggota.StatusPengajuan.DITOLAK
        pengajuan.disetujui_oleh = request.user
        pengajuan.catatan_admin = catatan
        pengajuan.save()
        messages.info(request, f"Permohonan hapus anggota '{nama_anggota}' dari pelatih {nama_pelatih} telah ditolak.")

    if next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect('members:member_list')


@login_required
@require_POST
def reset_face_registration(request, user_id):
    """
    Mereset data biometrik wajah anggota agar bisa melakukan auto-enrollment ulang.
    Bisa dilakukan oleh Admin, Pelatih, atau pesilat itu sendiri.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role or str(request.user.id) == str(user_id)):
        messages.error(request, "Akses ditolak.")
        return redirect('members:member_list')

    profile = get_object_or_404(AnggotaProfile.objects.select_related('user'), user_id=user_id)
    profile.face_descriptor = None
    profile.face_registered_at = None
    profile.save(update_fields=['face_descriptor', 'face_registered_at'])

    nama = profile.user.get_full_name() or profile.user.username
    messages.success(request, f"Data biometrik wajah '{nama}' berhasil direset! Siswa dapat mendaftarkan wajah baru saat pemindaian berikutnya.")
    return redirect('members:member_detail', user_id=user_id)


def public_parent_portal(request):
    """
    PRD Section 2: Orang Tua / Wali Murid (Viewer / Public Transparency Portal)
    Akses transparansi kehadiran dan keaktifan anak tanpa login wajib, cukup menggunakan NISN & Tanggal Lahir.
    """
    query_nisn = request.GET.get('nisn', '').strip()
    query_tgl = request.GET.get('tanggal_lahir', '').strip()

    anggota = None
    presensi_list = []
    stats = {}
    searched = False

    if query_nisn:
        searched = True
        qs = AnggotaProfile.objects.select_related('user', 'sabuk_saat_ini', 'kategori_fokus').filter(nisn=query_nisn)
        if query_tgl:
            qs = qs.filter(tanggal_lahir=query_tgl)
        anggota = qs.first()

        if anggota:
            presensi_list = anggota.riwayat_presensi.select_related('sesi').order_by('-waktu_presensi')[:10]
            total_sesi = SesiLatihan.objects.filter(status=SesiLatihan.StatusSesi.SELESAI).count()
            hadir = anggota.riwayat_presensi.filter(status=Presensi.StatusPresensi.HADIR).count()
            izin = anggota.riwayat_presensi.filter(status=Presensi.StatusPresensi.IZIN).count()
            sakit = anggota.riwayat_presensi.filter(status=Presensi.StatusPresensi.SAKIT).count()
            alpa = anggota.riwayat_presensi.filter(status=Presensi.StatusPresensi.ALPA).count()

            persentase = round((hadir / total_sesi * 100)) if total_sesi > 0 else 0
            min_ukt = anggota.sabuk_saat_ini.min_kehadiran_ukt if anggota.sabuk_saat_ini else 75
            streak = anggota.calculate_attendance_streak()

            stats = {
                'total_sesi': total_sesi,
                'hadir': hadir,
                'izin': izin,
                'sakit': sakit,
                'alpa': alpa,
                'persentase': persentase,
                'min_ukt': min_ukt,
                'is_eligible_ukt': persentase >= min_ukt,
                'streak': streak,
            }

    return render(request, 'members/parent_portal.html', {
        'anggota': anggota,
        'presensi_list': presensi_list,
        'stats': stats,
        'searched': searched,
        'query_nisn': query_nisn,
        'query_tgl': query_tgl,
    })
