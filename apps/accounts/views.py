from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import User
from apps.core.models import TingkatSabuk, KategoriTanding, Sekolah
from apps.members.models import AnggotaProfile, PelatihProfile



def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Selamat datang kembali, Pendekar {user.get_full_name() or user.username}!")
            return redirect('core:dashboard')
        else:
            messages.error(request, "Username atau kata sandi yang kamu masukkan salah.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Kamu telah berhasil keluar dari sistem.")
    return redirect('accounts:login')


def register_view(request):
    """
    Pendaftaran mandiri dinonaktifkan.
    Pembuatan akun pelatih dan anggota dipusatkan melalui Admin.
    """
    if request.user.is_authenticated and request.user.is_admin_role:
        return redirect('accounts:admin_create_user')

    messages.info(request, "Pendaftaran akun mandiri dinonaktifkan. Pembuatan akun pelatih dan anggota dilakukan langsung oleh Admin / Pembina eskul.")
    return redirect('accounts:login')


@login_required
def admin_create_user(request):
    """
    Fitur Pembuatan Akun Pelatih dan Anggota khusus Admin / Pembina Eskul.
    Mendukung pembuatan akun User sekaligus profil lengkap (PelatihProfile / AnggotaProfile).
    """
    if not request.user.is_admin_role:
        messages.error(request, "Akses ditolak. Fitur pembuatan akun hanya dapat diakses oleh Admin / Pembina Eskul.")
        return redirect('core:dashboard')

    sabuk_list = TingkatSabuk.objects.all().order_by('urutan_tingkat')
    kategori_list = KategoriTanding.objects.all().order_by('nama')
    sekolah_list = Sekolah.objects.filter(is_aktif=True).order_by('nama_sekolah')

    if request.method == 'POST':
        account_type = request.POST.get('account_type', 'ANGGOTA').upper()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        avatar = request.FILES.get('avatar')

        # Basic validations
        if not username or not password or not first_name:
            messages.error(request, "Username, Kata Sandi, dan Nama Depan wajib diisi.")
            return render(request, 'accounts/admin_create_user.html', {
                'sabuk_list': sabuk_list,
                'kategori_list': kategori_list,
                'sekolah_list': sekolah_list,
                'form_data': request.POST,
                'active_tab': account_type,
            })

        if password != password_confirm:
            messages.error(request, "Konfirmasi kata sandi tidak cocok. Silakan periksa kembali.")
            return render(request, 'accounts/admin_create_user.html', {
                'sabuk_list': sabuk_list,
                'kategori_list': kategori_list,
                'sekolah_list': sekolah_list,
                'form_data': request.POST,
                'active_tab': account_type,
            })

        if len(password) < 6:
            messages.error(request, "Kata sandi minimal harus terdiri dari 6 karakter.")
            return render(request, 'accounts/admin_create_user.html', {
                'sabuk_list': sabuk_list,
                'kategori_list': kategori_list,
                'sekolah_list': sekolah_list,
                'form_data': request.POST,
                'active_tab': account_type,
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' sudah digunakan. Silakan pilih username lain.")
            return render(request, 'accounts/admin_create_user.html', {
                'sabuk_list': sabuk_list,
                'kategori_list': kategori_list,
                'sekolah_list': sekolah_list,
                'form_data': request.POST,
                'active_tab': account_type,
            })


        # Process Pelatih Account Creation
        if account_type == 'PELATIH':
            nomor_registrasi = request.POST.get('nomor_registrasi', '').strip()
            tingkatan_pendekar = request.POST.get('tingkatan_pendekar', '').strip()
            spesialisasi = request.POST.get('spesialisasi', '').strip()
            sertifikasi_sk = request.POST.get('sertifikasi_sk', '').strip()

            if not nomor_registrasi:
                messages.error(request, "Nomor Registrasi / Lisensi Pelatih wajib diisi.")
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

            if PelatihProfile.objects.filter(nomor_registrasi=nomor_registrasi).exists():
                messages.error(request, f"Nomor Registrasi Pelatih '{nomor_registrasi}' sudah terdaftar.")
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

            try:
                with transaction.atomic():
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=User.Role.PELATIH,
                        phone_number=phone_number,
                    )
                    if avatar:
                        new_user.avatar = avatar
                        new_user.save()

                    PelatihProfile.objects.create(
                        user=new_user,
                        nomor_registrasi=nomor_registrasi,
                        tingkatan_pendekar=tingkatan_pendekar,
                        spesialisasi=spesialisasi,
                        sertifikasi_sk=sertifikasi_sk,
                    )

                messages.success(request, f"Akun Pelatih '{new_user.get_full_name() or new_user.username}' (No. Reg: {nomor_registrasi}) berhasil dibuat!")
                return redirect('members:member_list')

            except Exception as e:
                messages.error(request, f"Terjadi kesalahan saat membuat akun pelatih: {str(e)}")
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

        # Process Anggota Account Creation
        else:
            nisn = request.POST.get('nisn', '').strip()
            sekolah_id = request.POST.get('sekolah_id')
            nama_sekolah_baru = request.POST.get('nama_sekolah_baru', '').strip()
            kelas_sekolah = request.POST.get('kelas_sekolah', '').strip()
            jenis_kelamin = request.POST.get('jenis_kelamin', AnggotaProfile.Gender.LAKI_LAKI)
            tanggal_lahir = request.POST.get('tanggal_lahir') or None
            sabuk_id = request.POST.get('sabuk_id')
            kategori_id = request.POST.get('kategori_id')
            nama_wali = request.POST.get('nama_wali', '').strip()
            no_hp_wali = request.POST.get('no_hp_wali', '').strip()
            status_keanggotaan = request.POST.get('status_keanggotaan', AnggotaProfile.MembershipStatus.AKTIF)

            if not nisn or not kelas_sekolah:
                messages.error(request, "NISN dan Kelas & Jurusan wajib diisi.")
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

            if len(nisn) != 10 or not nisn.isdigit():
                messages.error(
                    request,
                    "NISN harus terdiri dari tepat 10 digit angka sesuai standar resmi Kementerian Pendidikan Pusat (Kemdikbudristek) untuk sinkronisasi nilai e-Rapor."
                )
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

            if AnggotaProfile.objects.filter(nisn=nisn).exists():
                messages.error(request, f"NISN '{nisn}' sudah terdaftar dalam sistem.")
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

            # Tentukan Sekolah
            sekolah_obj = None
            if nama_sekolah_baru:
                sekolah_obj, _ = Sekolah.objects.get_or_create(nama_sekolah=nama_sekolah_baru)
            elif sekolah_id:
                sekolah_obj = Sekolah.objects.filter(id=sekolah_id).first()
            if not sekolah_obj:
                sekolah_obj = Sekolah.objects.filter(is_aktif=True).first()

            try:
                with transaction.atomic():
                    new_user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=User.Role.ANGGOTA,
                        phone_number=phone_number,
                    )
                    if avatar:
                        new_user.avatar = avatar
                        new_user.save()

                    sabuk_obj = TingkatSabuk.objects.filter(id=sabuk_id).first() if sabuk_id else TingkatSabuk.objects.order_by('urutan_tingkat').first()
                    kategori_obj = KategoriTanding.objects.filter(id=kategori_id).first() if kategori_id else None

                    AnggotaProfile.objects.create(
                        user=new_user,
                        nisn=nisn,
                        sekolah=sekolah_obj,
                        jenis_kelamin=jenis_kelamin,
                        tanggal_lahir=tanggal_lahir,
                        kelas_sekolah=kelas_sekolah,
                        sabuk_saat_ini=sabuk_obj,
                        kategori_fokus=kategori_obj,
                        nama_wali=nama_wali,
                        no_hp_wali=no_hp_wali,
                        status_keanggotaan=status_keanggotaan,
                    )

                school_info = f" ({sekolah_obj.nama_sekolah})" if sekolah_obj else ""
                messages.success(request, f"Akun Anggota Pesilat '{new_user.get_full_name() or new_user.username}' (NISN: {nisn}){school_info} berhasil dibuat!")
                return redirect('members:member_list')

            except Exception as e:
                messages.error(request, f"Terjadi kesalahan saat membuat akun anggota: {str(e)}")
                return render(request, 'accounts/admin_create_user.html', {
                    'sabuk_list': sabuk_list,
                    'kategori_list': kategori_list,
                    'sekolah_list': sekolah_list,
                    'form_data': request.POST,
                    'active_tab': account_type,
                })

    return render(request, 'accounts/admin_create_user.html', {
        'sabuk_list': sabuk_list,
        'kategori_list': kategori_list,
        'sekolah_list': sekolah_list,
        'active_tab': 'ANGGOTA',
    })




@login_required
def profile_view(request):
    """
    Halaman manajemen profil pengguna:
    - Edit identitas pribadi (Nama, Username, Email, No HP, Foto Profil)
    - Edit profil spesifik eskul (Kelas, NISN, Keterangan Sabuk, Kategori, Kontak Wali)
    - Ubah Kata Sandi (Password Change)
    """
    user = request.user
    anggota_profile = getattr(user, 'anggota_profile', None)
    pelatih_profile = getattr(user, 'pelatih_profile', None)
    
    sabuk_list = TingkatSabuk.objects.all().order_by('urutan_tingkat')
    kategori_list = KategoriTanding.objects.all().order_by('nama')

    if request.method == 'POST':
        action = request.POST.get('action', 'update_profile')

        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            avatar = request.FILES.get('avatar')

            if not username or not first_name:
                messages.error(request, "Nama Depan dan Username tidak boleh kosong.")
                return redirect('accounts:profile')

            # Periksa keunikan username jika diganti
            if username != user.username and User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, f"Username '{username}' sudah digunakan oleh pengguna lain.")
                return redirect('accounts:profile')

            user.first_name = first_name
            user.last_name = last_name
            user.username = username
            user.email = email
            user.phone_number = phone_number
            if avatar:
                user.avatar = avatar
            user.save()

            # Update spesifik Anggota
            if anggota_profile:
                kelas_sekolah = request.POST.get('kelas_sekolah', '').strip()
                nisn = request.POST.get('nisn', '').strip()
                jenis_kelamin = request.POST.get('jenis_kelamin', anggota_profile.jenis_kelamin)
                nama_wali = request.POST.get('nama_wali', '').strip()
                no_hp_wali = request.POST.get('no_hp_wali', '').strip()
                sabuk_id = request.POST.get('sabuk_id')
                kategori_id = request.POST.get('kategori_id')

                if nisn and nisn != anggota_profile.nisn and AnggotaProfile.objects.filter(nisn=nisn).exclude(user_id=user.id).exists():
                    messages.error(request, f"NISN '{nisn}' sudah terdaftar untuk siswa lain.")
                    return redirect('accounts:profile')

                if nisn:
                    anggota_profile.nisn = nisn
                if kelas_sekolah:
                    anggota_profile.kelas_sekolah = kelas_sekolah
                anggota_profile.jenis_kelamin = jenis_kelamin
                anggota_profile.nama_wali = nama_wali
                anggota_profile.no_hp_wali = no_hp_wali

                if sabuk_id:
                    anggota_profile.sabuk_saat_ini = TingkatSabuk.objects.filter(id=sabuk_id).first()
                if kategori_id:
                    anggota_profile.kategori_fokus = KategoriTanding.objects.filter(id=kategori_id).first()
                elif kategori_id == '':
                    anggota_profile.kategori_fokus = None

                anggota_profile.save()

            # Update spesifik Pelatih
            elif pelatih_profile:
                pelatih_profile.tingkatan_pendekar = request.POST.get('tingkatan_pendekar', '').strip()
                pelatih_profile.spesialisasi = request.POST.get('spesialisasi', '').strip()
                pelatih_profile.sertifikasi_sk = request.POST.get('sertifikasi_sk', '').strip()
                pelatih_profile.save()

            messages.success(request, "Profil berhasil diperbarui!")
            return redirect('accounts:profile')

        elif action == 'change_password':
            current_password = request.POST.get('current_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_new_password = request.POST.get('confirm_new_password', '').strip()

            if not user.check_password(current_password):
                messages.error(request, "Kata sandi saat ini yang kamu masukkan salah.")
                return redirect('accounts:profile')

            if new_password != confirm_new_password:
                messages.error(request, "Kata sandi baru dan konfirmasi tidak cocok.")
                return redirect('accounts:profile')

            if len(new_password) < 6:
                messages.error(request, "Kata sandi baru minimal harus 6 karakter.")
                return redirect('accounts:profile')

            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Pertahankan sesi login
            messages.success(request, "Kata sandi berhasil diperbarui dengan aman!")
            return redirect('accounts:profile')

    context = {
        'user': user,
        'anggota_profile': anggota_profile,
        'pelatih_profile': pelatih_profile,
        'sabuk_list': sabuk_list,
        'kategori_list': kategori_list,
    }
    return render(request, 'accounts/profile.html', context)
