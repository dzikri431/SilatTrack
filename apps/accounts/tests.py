from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.members.models import AnggotaProfile, PelatihProfile
from apps.core.models import TingkatSabuk, KategoriTanding


class AuthenticationAndAdminUserCreationTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Tingkat Sabuk & Kategori dummy
        self.sabuk_putih = TingkatSabuk.objects.create(
            nama_sabuk="Putih",
            urutan_tingkat=1,
            warna_hex="#FFFFFF",
            min_kehadiran_ukt=75
        )
        self.kategori_tanding = KategoriTanding.objects.create(
            nama="Tanding Putra",
            kelas_tanding="Kelas A (39-43 kg)"
        )

        # Admin user
        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="adminpassword123",
            role=User.Role.ADMIN,
            first_name="Pembina",
            last_name="Utama"
        )

        # Regular Anggota user
        self.anggota_user = User.objects.create_user(
            username="siswa_test",
            password="siswapassword123",
            role=User.Role.ANGGOTA,
            first_name="Siswa",
            last_name="Pesilat"
        )
        AnggotaProfile.objects.create(
            user=self.anggota_user,
            nisn="1234567890",
            kelas_sekolah="X PPLG 1",
            sabuk_saat_ini=self.sabuk_putih
        )

    def test_login_page_renders_without_demo_and_register(self):
        """Form login tidak lagi menampilkan tombol akun demo dan link pendaftaran mandiri."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Masuk Sistem')
        self.assertContains(response, 'Username / NISN')
        self.assertContains(response, 'Kata Sandi')

        # Akun demo dan link register harus TIDAK ADA
        self.assertNotContains(response, '⚡ Masuk Cepat Akun Demo')
        self.assertNotContains(response, 'Daftar Akun Baru')
        self.assertNotContains(response, 'Pesilat baru belum terdaftar?')

    def test_register_view_redirects_anonymous_user(self):
        """Pendaftaran mandiri dinonaktifkan untuk publik dan diarahkan ke login."""
        response = self.client.get(reverse('accounts:register'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:login'))
        messages = list(response.context['messages'])
        self.assertTrue(any('dinonaktifkan' in str(m) for m in messages))

    def test_register_view_redirects_admin_user_to_admin_create(self):
        """Admin yang mengakses /auth/register/ langsung diarahkan ke halaman pembuatan akun admin."""
        self.client.login(username="admin_test", password="adminpassword123")
        response = self.client.get(reverse('accounts:register'))
        self.assertRedirects(response, reverse('accounts:admin_create_user'))

    def test_admin_create_user_access_restriction(self):
        """Halaman pembuatan akun hanya dapat diakses oleh Admin, bukan siswa/anggota biasa."""
        # Anonymous user -> login page
        response = self.client.get(reverse('accounts:admin_create_user'))
        self.assertEqual(response.status_code, 302)

        # Anggota biasa -> dashboard with error
        self.client.login(username="siswa_test", password="siswapassword123")
        response = self.client.get(reverse('accounts:admin_create_user'), follow=True)
        self.assertRedirects(response, reverse('core:dashboard'))
        messages = list(response.context['messages'])
        self.assertTrue(any('Akses ditolak' in str(m) for m in messages))

    def test_admin_create_coach_account_success(self):
        """Admin berhasil membuat akun Pelatih beserta lisensi dan profil kepelatihannya."""
        self.client.login(username="admin_test", password="adminpassword123")
        post_data = {
            'account_type': 'PELATIH',
            'username': 'pelatih_budi',
            'password': 'coachpass123',
            'password_confirm': 'coachpass123',
            'first_name': 'Budi',
            'last_name': 'Setiawan',
            'email': 'budi@silattrack.test',
            'phone_number': '08123456789',
            'nomor_registrasi': 'PLT-TEST-001',
            'tingkatan_pendekar': 'Pendekar Muda',
            'spesialisasi': 'Tanding & Fisik',
            'sertifikasi_sk': 'SK/IPSI/TEST/01',
        }
        response = self.client.post(reverse('accounts:admin_create_user'), post_data, follow=True)
        self.assertRedirects(response, reverse('members:member_list'))

        # Verifikasi user dan profil pelatih terbentuk
        new_user = User.objects.get(username='pelatih_budi')
        self.assertEqual(new_user.role, User.Role.PELATIH)
        self.assertEqual(new_user.first_name, 'Budi')
        self.assertTrue(new_user.check_password('coachpass123'))

        coach_profile = PelatihProfile.objects.get(user=new_user)
        self.assertEqual(coach_profile.nomor_registrasi, 'PLT-TEST-001')
        self.assertEqual(coach_profile.tingkatan_pendekar, 'Pendekar Muda')
        self.assertEqual(coach_profile.spesialisasi, 'Tanding & Fisik')

    def test_admin_create_member_account_success(self):
        """Admin berhasil membuat akun Anggota/Pesilat lengkap dengan profil siswa dan sabuk."""
        self.client.login(username="admin_test", password="adminpassword123")
        post_data = {
            'account_type': 'ANGGOTA',
            'username': 'pesilat_indah',
            'password': 'memberpass123',
            'password_confirm': 'memberpass123',
            'first_name': 'Indah',
            'last_name': 'Permata',
            'email': 'indah@silattrack.test',
            'phone_number': '08987654321',
            'nisn': '9988776655',
            'kelas_sekolah': 'X PPLG 2',
            'jenis_kelamin': 'P',
            'sabuk_id': str(self.sabuk_putih.id),
            'kategori_id': str(self.kategori_tanding.id),
            'nama_wali': 'Pak Joko',
            'no_hp_wali': '08555666777',
            'status_keanggotaan': 'AKTIF',
        }
        response = self.client.post(reverse('accounts:admin_create_user'), post_data, follow=True)
        self.assertRedirects(response, reverse('members:member_list'))

        # Verifikasi user dan profil anggota terbentuk
        new_user = User.objects.get(username='pesilat_indah')
        self.assertEqual(new_user.role, User.Role.ANGGOTA)
        self.assertEqual(new_user.first_name, 'Indah')
        self.assertTrue(new_user.check_password('memberpass123'))

        member_profile = AnggotaProfile.objects.get(user=new_user)
        self.assertEqual(member_profile.nisn, '9988776655')
        self.assertEqual(member_profile.kelas_sekolah, 'X PPLG 2')
        self.assertEqual(member_profile.jenis_kelamin, 'P')
        self.assertEqual(member_profile.sabuk_saat_ini, self.sabuk_putih)
        self.assertEqual(member_profile.kategori_fokus, self.kategori_tanding)
