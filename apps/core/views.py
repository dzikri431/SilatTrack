import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from apps.accounts.models import User
from apps.members.models import AnggotaProfile
from apps.schedule.models import JadwalLatihan
from apps.attendance.models import SesiLatihan, Presensi
from apps.core.models import Sekolah, Perguruan



@login_required
def dashboard(request):
    user = request.user
    today = timezone.localdate()
    current_weekday = today.weekday()  # 0=Senin, ..., 6=Minggu

    # Active session today (hanya yang sudah disetujui admin dan dibuka)
    active_session = SesiLatihan.objects.filter(
        tanggal=today,
        status=SesiLatihan.StatusSesi.DIBUKA,
        status_persetujuan=SesiLatihan.StatusPersetujuanSesi.DISETUJUI
    ).first()

    # Next / Today's regular schedule
    today_schedule = JadwalLatihan.objects.filter(
        hari_indeks=current_weekday,
        is_aktif=True,
        status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI
    ).first()

    context = {
        'today': today,
        'active_session': active_session,
        'today_schedule': today_schedule,
    }

    if user.is_admin_role or user.is_pelatih_role:
        # Metrics for Coaches & Admins
        total_pesilat = AnggotaProfile.objects.filter(status_keanggotaan=AnggotaProfile.MembershipStatus.AKTIF).count()
        total_sesi = SesiLatihan.objects.count()
        recent_sessions = SesiLatihan.objects.all().select_related('pelatih', 'jadwal')[:5]

        # Approval status items
        if user.is_admin_role:
            pending_sessions = SesiLatihan.objects.filter(
                status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU
            ).select_related('pelatih', 'jadwal').order_by('-tanggal', '-jam_buka')
            pending_schedules = JadwalLatihan.objects.filter(
                status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU
            ).select_related('dibuat_oleh').order_by('hari_indeks', 'jam_mulai')
        else:
            pending_sessions = SesiLatihan.objects.filter(
                pelatih=user,
                status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU
            ).select_related('pelatih', 'jadwal').order_by('-tanggal', '-jam_buka')
            pending_schedules = JadwalLatihan.objects.filter(
                dibuat_oleh=user,
                status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU
            ).select_related('dibuat_oleh').order_by('hari_indeks', 'jam_mulai')

        pending_total_count = pending_sessions.count() + pending_schedules.count()
        
        # Overall presence stats
        total_presensi = Presensi.objects.count()
        hadir_count = Presensi.objects.filter(status=Presensi.StatusPresensi.HADIR).count()
        izin_count = Presensi.objects.filter(status=Presensi.StatusPresensi.IZIN).count()
        sakit_count = Presensi.objects.filter(status=Presensi.StatusPresensi.SAKIT).count()
        alpa_count = Presensi.objects.filter(status=Presensi.StatusPresensi.ALPA).count()

        presence_rate = round((hadir_count / total_presensi * 100)) if total_presensi > 0 else 0

        # Donut Chart Data: Komposisi presensi eskul
        coach_donut_data = {
            'labels': ['Hadir', 'Izin', 'Sakit', 'Alpa'],
            'data': [hadir_count, izin_count, sakit_count, alpa_count],
        }

        # Trend Kehadiran Sesi Terakhir (maksimal 7 sesi)
        recent_sessions_qs = list(SesiLatihan.objects.all().order_by('-tanggal', '-jam_buka')[:7])
        recent_sessions_qs.reverse()

        trend_labels = []
        trend_hadir = []
        trend_izin_sakit = []
        trend_alpa = []
        for s in recent_sessions_qs:
            trend_labels.append(s.tanggal.strftime('%d/%m'))
            trend_hadir.append(s.daftar_presensi.filter(status=Presensi.StatusPresensi.HADIR).count())
            trend_izin_sakit.append(s.daftar_presensi.filter(status__in=[Presensi.StatusPresensi.IZIN, Presensi.StatusPresensi.SAKIT]).count())
            trend_alpa.append(s.daftar_presensi.filter(status=Presensi.StatusPresensi.ALPA).count())

        coach_trend_data = {
            'labels': trend_labels,
            'hadir': trend_hadir,
            'izin_sakit': trend_izin_sakit,
            'alpa': trend_alpa,
        }

        # Member Attendance Monitoring List (Dipantau langsung oleh Admin)
        all_active_members = AnggotaProfile.objects.filter(
            status_keanggotaan=AnggotaProfile.MembershipStatus.AKTIF
        ).select_related('user', 'sabuk_saat_ini', 'kategori_fokus')

        member_monitoring = []
        for m in all_active_members:
            m_hadir = Presensi.objects.filter(anggota=m, status=Presensi.StatusPresensi.HADIR).count()
            m_izin = Presensi.objects.filter(anggota=m, status=Presensi.StatusPresensi.IZIN).count()
            m_sakit = Presensi.objects.filter(anggota=m, status=Presensi.StatusPresensi.SAKIT).count()
            m_alpa = Presensi.objects.filter(anggota=m, status=Presensi.StatusPresensi.ALPA).count()
            
            m_pct = round((m_hadir / total_sesi * 100)) if total_sesi > 0 else 0
            min_ukt = m.sabuk_saat_ini.min_kehadiran_ukt if m.sabuk_saat_ini else 75
            
            if m_pct >= min_ukt:
                status_ukt = 'AMAN'
                status_label = 'Siap UKT'
                status_color = 'emerald'
            elif m_pct >= max(0, min_ukt - 20):
                status_ukt = 'PERINGATAN'
                status_label = 'Tingkatkan'
                status_color = 'amber'
            else:
                status_ukt = 'KRITIS'
                status_label = 'Di Bawah Target'
                status_color = 'red'

            member_monitoring.append({
                'anggota': m,
                'hadir': m_hadir,
                'izin': m_izin,
                'sakit': m_sakit,
                'alpa': m_alpa,
                'persentase': m_pct,
                'min_ukt': min_ukt,
                'status_ukt': status_ukt,
                'status_label': status_label,
                'status_color': status_color,
            })

        # Urutkan berdasarkan persentase kehadiran tertinggi
        member_monitoring.sort(key=lambda x: x['persentase'], reverse=True)

        context.update({
            'total_pesilat': total_pesilat,
            'total_sesi': total_sesi,
            'recent_sessions': recent_sessions,
            'presence_rate': presence_rate,
            'hadir_count': hadir_count,
            'izin_count': izin_count,
            'sakit_count': sakit_count,
            'alpa_count': alpa_count,
            'pending_sessions': pending_sessions,
            'pending_schedules': pending_schedules,
            'pending_total_count': pending_total_count,
            'coach_donut_json': json.dumps(coach_donut_data),
            'coach_trend_json': json.dumps(coach_trend_data),
            'member_monitoring': member_monitoring,
        })
        return render(request, 'core/dashboard_coach.html', context)

    else:
        # Pesilat Student View
        try:
            profile = user.anggota_profile
        except AnggotaProfile.DoesNotExist:
            profile = None

        user_presensi_today = None
        if active_session and profile:
            user_presensi_today = Presensi.objects.filter(
                sesi=active_session,
                anggota=profile
            ).first()

        # Member attendance analytics
        total_sesi_dijalankan = SesiLatihan.objects.filter(status=SesiLatihan.StatusSesi.SELESAI).count()
        if active_session:
            total_sesi_dijalankan += 1

        total_hadir_member = 0
        total_izin_member = 0
        total_sakit_member = 0
        total_alpa_member = 0
        persentase_hadir = 0
        min_kehadiran_ukt = 75
        is_eligible_ukt = False

        student_donut_data = {'labels': ['Hadir', 'Izin', 'Sakit', 'Alpa'], 'data': [0, 0, 0, 0]}
        student_trend_data = {'labels': [], 'cumulative_pct': [], 'target_ukt': []}

        if profile:
            total_hadir_member = Presensi.objects.filter(
                anggota=profile,
                status=Presensi.StatusPresensi.HADIR
            ).count()
            total_izin_member = Presensi.objects.filter(
                anggota=profile,
                status=Presensi.StatusPresensi.IZIN
            ).count()
            total_sakit_member = Presensi.objects.filter(
                anggota=profile,
                status=Presensi.StatusPresensi.SAKIT
            ).count()
            total_alpa_member = Presensi.objects.filter(
                anggota=profile,
                status=Presensi.StatusPresensi.ALPA
            ).count()

            # Perhitungkan sesi yang terlewat tanpa izin sebagai alpa
            recorded_count = total_hadir_member + total_izin_member + total_sakit_member + total_alpa_member
            if total_sesi_dijalankan > recorded_count:
                total_alpa_member += (total_sesi_dijalankan - recorded_count)

            if total_sesi_dijalankan > 0:
                persentase_hadir = min(100, round((total_hadir_member / total_sesi_dijalankan) * 100))

            if profile.sabuk_saat_ini:
                min_kehadiran_ukt = profile.sabuk_saat_ini.min_kehadiran_ukt

            is_eligible_ukt = persentase_hadir >= min_kehadiran_ukt

            student_donut_data = {
                'labels': ['Hadir', 'Izin', 'Sakit', 'Alpa'],
                'data': [total_hadir_member, total_izin_member, total_sakit_member, total_alpa_member],
            }

            # Tren kumulatif sesi latihan terakhir
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

            student_trend_data = {
                'labels': s_labels,
                'cumulative_pct': s_cum_pct,
                'target_ukt': s_targets,
            }

        riwayat_presensi_user = Presensi.objects.filter(anggota=profile).select_related('sesi')[:6] if profile else []

        context.update({
            'profile': profile,
            'user_presensi_today': user_presensi_today,
            'total_sesi_dijalankan': total_sesi_dijalankan,
            'total_hadir_member': total_hadir_member,
            'total_izin_member': total_izin_member,
            'total_sakit_member': total_sakit_member,
            'total_alpa_member': total_alpa_member,
            'persentase_hadir': persentase_hadir,
            'min_kehadiran_ukt': min_kehadiran_ukt,
            'is_eligible_ukt': is_eligible_ukt,
            'riwayat_presensi_user': riwayat_presensi_user,
            'student_donut_json': json.dumps(student_donut_data),
            'student_trend_json': json.dumps(student_trend_data),
            'streak': profile.calculate_attendance_streak() if profile else 0,
        })
        return render(request, 'core/dashboard_student.html', context)

def pitch_presentation(request):
    """
    Tampilan presentasi slide interaktif untuk calon investor (pitch deck).
    Dapat diakses langsung oleh investor atau founder untuk presentasi.
    """
    return render(request, 'presentation/pitch_deck.html')


@login_required
def perguruan_settings(request):
    """
    Manajemen Identitas Perguruan Silat & Logo Aplikasi serta Logo Sekolah Mitra.
    Hanya dapat diakses oleh Admin dan Pelatih.
    """
    if not (request.user.is_admin_role or request.user.is_pelatih_role):
        messages.error(request, "Akses ditolak: Hanya Admin dan Pelatih yang dapat mengubah identitas perguruan.")
        return redirect('core:dashboard')

    perguruan = Perguruan.get_solo()
    sekolah_list = Sekolah.objects.all().order_by('nama_sekolah')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_perguruan':
            perguruan.nama_perguruan = request.POST.get('nama_perguruan', perguruan.nama_perguruan).strip()
            perguruan.singkatan = request.POST.get('singkatan', perguruan.singkatan).strip()
            perguruan.semboyan = request.POST.get('semboyan', perguruan.semboyan).strip()
            perguruan.alamat_pusat = request.POST.get('alamat_pusat', perguruan.alamat_pusat).strip()
            perguruan.kontak = request.POST.get('kontak', perguruan.kontak).strip()

            if 'logo_perguruan' in request.FILES:
                perguruan.logo_perguruan = request.FILES['logo_perguruan']
            elif request.POST.get('hapus_logo_perguruan') == '1':
                perguruan.logo_perguruan = None

            perguruan.save()
            messages.success(request, "Identitas dan Logo Perguruan berhasil diperbarui! Logo terbaru otomatis diterapkan ke seluruh aplikasi.")
            return redirect('core:perguruan_settings')

        elif action == 'update_sekolah_logo':
            sekolah_id = request.POST.get('sekolah_id')
            sekolah_obj = get_object_or_404(Sekolah, id=sekolah_id)

            if 'logo_sekolah' in request.FILES:
                sekolah_obj.logo_sekolah = request.FILES['logo_sekolah']
            elif request.POST.get('hapus_logo_sekolah') == '1':
                sekolah_obj.logo_sekolah = None

            if request.POST.get('nama_kepala_sekolah'):
                sekolah_obj.nama_kepala_sekolah = request.POST.get('nama_kepala_sekolah').strip()
            if request.POST.get('nip_kepala_sekolah'):
                sekolah_obj.nip_kepala_sekolah = request.POST.get('nip_kepala_sekolah').strip()
            if request.POST.get('alamat'):
                sekolah_obj.alamat = request.POST.get('alamat').strip()

            sekolah_obj.save()
            messages.success(request, f"Logo dan data sekolah '{sekolah_obj.nama_sekolah}' berhasil diperbarui!")
            return redirect('core:perguruan_settings')

        elif action == 'create_sekolah':
            nama = request.POST.get('nama_sekolah', '').strip()
            if nama:
                Sekolah.objects.create(
                    nama_sekolah=nama,
                    npsn=request.POST.get('npsn', '').strip(),
                    alamat=request.POST.get('alamat', '').strip(),
                    nama_kepala_sekolah=request.POST.get('nama_kepala_sekolah', '').strip() or "Drs. H. Mulyadi, M.M",
                    nip_kepala_sekolah=request.POST.get('nip_kepala_sekolah', '').strip() or "19720412 199802 1 003",
                    logo_sekolah=request.FILES.get('logo_sekolah')
                )
                messages.success(request, f"Sekolah mitra '{nama}' berhasil ditambahkan!")
            return redirect('core:perguruan_settings')

    return render(request, 'core/perguruan_settings.html', {
        'perguruan': perguruan,
        'sekolah_list': sekolah_list,
    })


