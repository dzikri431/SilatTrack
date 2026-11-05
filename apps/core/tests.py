from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.members.models import AnggotaProfile
from apps.core.models import TingkatSabuk


class CoreAndAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sabuk_putih = TingkatSabuk.objects.create(
            nama_sabuk='Putih',
            urutan_tingkat=1,
            warna_hex='#FFFFFF'
        )
        self.sabuk_kuning = TingkatSabuk.objects.create(
            nama_sabuk='Kuning',
            urutan_tingkat=2,
            warna_hex='#FACC15'
        )
        self.user = User.objects.create_user(
            username='pesilat_core_test',
            password='password123',
            role=User.Role.ANGGOTA,
            first_name='Pesilat',
            last_name='Satu'
        )
        self.profile = AnggotaProfile.objects.create(
            user=self.user,
            nisn='999888777',
            kelas_sekolah='X RPL 1',
            sabuk_saat_ini=self.sabuk_putih
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SilatTrack')
        self.assertNotContains(response, 'Daftar Akun Baru')
        self.assertNotContains(response, '⚡ Masuk Cepat Akun Demo')

    def test_register_page_redirects_for_anonymous(self):
        """Pendaftaran mandiri dinonaktifkan, dialihkan ke login"""
        response = self.client.get(reverse('accounts:register'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_admin_member_creation_flow(self):
        """Pembuatan anggota sekarang dilakukan oleh admin melalui admin_create_user"""
        admin_user = User.objects.create_user(
            username='admin_creator',
            password='adminpassword123',
            role=User.Role.ADMIN,
            first_name='Admin',
            last_name='Pembina'
        )
        self.client.login(username='admin_creator', password='adminpassword123')
        payload = {
            'account_type': 'ANGGOTA',
            'first_name': 'Bambang',
            'last_name': 'Pamungkas',
            'username': 'bambang99',
            'nisn': '0098811223',
            'email': 'bambang@sekolah.sch.id',
            'phone_number': '081234567899',
            'kelas_sekolah': 'X DKV 1',
            'jenis_kelamin': 'L',
            'sabuk_id': str(self.sabuk_putih.id),
            'password': 'secretpassword',
            'password_confirm': 'secretpassword',
            'status_keanggotaan': 'AKTIF',
        }
        response = self.client.post(reverse('accounts:admin_create_user'), payload, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify User and AnggotaProfile exist
        new_user = User.objects.filter(username='bambang99').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.role, User.Role.ANGGOTA)

        new_profile = AnggotaProfile.objects.filter(nisn='0098811223').first()
        self.assertIsNotNone(new_profile)
        self.assertEqual(new_profile.user, new_user)
        self.assertEqual(new_profile.kelas_sekolah, 'X DKV 1')
        self.assertEqual(new_profile.sabuk_saat_ini, self.sabuk_putih)

    def test_profile_update_and_belt_info(self):
        """Test user editing personal details and belt info in profile page"""
        self.client.login(username='pesilat_core_test', password='password123')
        
        # Test profile page renders with belt info
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pengaturan Profil Pengguna')

        # Update profile
        payload = {
            'action': 'update_profile',
            'first_name': 'Pesilat Edit',
            'last_name': 'Hebat',
            'username': 'pesilat_core_test',
            'email': 'edited@email.com',
            'phone_number': '089999888877',
            'kelas_sekolah': 'XI RPL 1',
            'nisn': '999888777',
            'jenis_kelamin': 'L',
            'sabuk_id': self.sabuk_kuning.id,
        }
        response = self.client.post(reverse('accounts:profile'), payload, follow=True)
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Pesilat Edit')
        self.assertEqual(self.user.phone_number, '089999888877')
        self.assertEqual(self.profile.kelas_sekolah, 'XI RPL 1')
        self.assertEqual(self.profile.sabuk_saat_ini, self.sabuk_kuning)

    def test_password_change_flow(self):
        """Test changing password in profile"""
        self.client.login(username='pesilat_core_test', password='password123')
        payload = {
            'action': 'change_password',
            'current_password': 'password123',
            'new_password': 'newpassword123',
            'confirm_new_password': 'newpassword123',
        }
        response = self.client.post(reverse('accounts:profile'), payload, follow=True)
        self.assertEqual(response.status_code, 200)

        # Login with new password should succeed
        self.client.logout()
        login_success = self.client.login(username='pesilat_core_test', password='newpassword123')
        self.assertTrue(login_success)

    def test_authenticated_dashboard_redirect(self):
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)

        self.client.login(username='pesilat_core_test', password='password123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Pesilat')

    def test_member_directory_renders(self):
        # Anggota dialihkan kembali ke dashboard (fitur anggota dihapus dari role anggota)
        self.client.login(username='pesilat_core_test', password='password123')
        response = self.client.get(reverse('members:member_list'))
        self.assertEqual(response.status_code, 302)

        # Admin dapat mengakses direktori anggota
        admin_user = User.objects.create_user(
            username='admin_core_test',
            password='password123',
            role=User.Role.ADMIN
        )
        self.client.login(username='admin_core_test', password='password123')
        response = self.client.get(reverse('members:member_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Direktori Pendekar Silat')

    def test_schedule_list_renders(self):
        self.client.login(username='pesilat_core_test', password='password123')
        response = self.client.get(reverse('schedule:schedule_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jadwal Latihan Mingguan')

    def test_student_dashboard_charts_rendered(self):
        """Pastikan data analitik dan elemen grafik persentase kehadiran tampil di dashboard siswa"""
        self.client.login(username='pesilat_core_test', password='password123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('student_donut_json', response.context)
        self.assertIn('student_trend_json', response.context)
        self.assertContains(response, 'studentDonutChart')
        self.assertContains(response, 'studentTrendChart')
        self.assertContains(response, 'Komposisi Presensi Latihan')
        self.assertContains(response, 'Tren Kehadiran vs Target UKT')

    def test_coach_dashboard_charts_and_member_monitoring(self):
        """Pastikan admin/pelatih dapat melihat grafik eskul dan tabel monitoring persentase pesilat"""
        admin_user = User.objects.create_user(
            username='pelatih_test',
            password='password123',
            role=User.Role.PELATIH,
            first_name='Pelatih',
            last_name='Sakti'
        )
        self.client.login(username='pelatih_test', password='password123')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('coach_donut_json', response.context)
        self.assertIn('coach_trend_json', response.context)
        self.assertIn('member_monitoring', response.context)
        self.assertContains(response, 'coachDonutChart')
        self.assertContains(response, 'coachTrendChart')
        self.assertContains(response, 'Pemantauan Kehadiran & Kualifikasi UKT Pesilat')

    def test_member_detail_charts_rendered(self):
        """Pastikan halaman detail anggota memiliki grafik donat & tren kehadiran"""
        self.client.login(username='pesilat_core_test', password='password123')
        response = self.client.get(reverse('members:member_detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('member_donut_json', response.context)
        self.assertIn('member_trend_json', response.context)
        self.assertContains(response, 'memberDonutChart')
        self.assertContains(response, 'memberTrendChart')
        self.assertContains(response, 'Komposisi Presensi Pesilat')
