from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.schedule.models import JadwalLatihan


class ScheduleApprovalAndManagementTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Admin User
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )

        # Coach User
        self.coach = User.objects.create_user(
            username='coach_test',
            password='password123',
            role=User.Role.PELATIH,
            first_name='Coach',
            last_name='Silat'
        )

        # Student User
        self.student = User.objects.create_user(
            username='student_test',
            password='password123',
            role=User.Role.ANGGOTA
        )

        # Default Active Schedule
        self.schedule_active = JadwalLatihan.objects.create(
            nama_jadwal='Latihan Rutin Jumat',
            hari_indeks=4,  # Jumat
            jam_mulai='15:30:00',
            jam_selesai='17:30:00',
            nama_lokasi='Lapangan Utama',
            is_aktif=True,
            status_persetujuan=JadwalLatihan.StatusPersetujuan.DISETUJUI,
            dibuat_oleh=self.admin
        )

    def test_admin_create_schedule_direct_active(self):
        """Admin membuat jadwal mingguan langsung aktif & disetujui"""
        self.client.login(username='admin_test', password='password123')
        url = reverse('schedule:schedule_create')
        data = {
            'nama_jadwal': 'Latihan Rutin Rabu',
            'hari_indeks': 2,  # Rabu
            'jam_mulai': '16:00',
            'jam_selesai': '18:00',
            'nama_lokasi': 'Dojo Silat',
            'radius_toleransi_meter': 100,
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('schedule:schedule_list'))

        created = JadwalLatihan.objects.get(hari_indeks=2, nama_lokasi='Dojo Silat')
        self.assertEqual(created.status_persetujuan, JadwalLatihan.StatusPersetujuan.DISETUJUI)
        self.assertTrue(created.is_aktif)
        self.assertEqual(created.dibuat_oleh, self.admin)

    def test_coach_propose_schedule_pending_approval(self):
        """Pelatih mengajukan jadwal mingguan, harus menunggu persetujuan admin & nonaktif sementara"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('schedule:schedule_create')
        data = {
            'nama_jadwal': 'Fisik Pagi Sabtu',
            'hari_indeks': 5,  # Sabtu
            'jam_mulai': '07:30',
            'jam_selesai': '10:00',
            'nama_lokasi': 'Halaman Belakang',
            'radius_toleransi_meter': 100,
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('schedule:schedule_list'))

        proposed = JadwalLatihan.objects.get(hari_indeks=5, nama_lokasi='Halaman Belakang')
        self.assertEqual(proposed.status_persetujuan, JadwalLatihan.StatusPersetujuan.MENUNGGU)
        self.assertFalse(proposed.is_aktif)
        self.assertEqual(proposed.dibuat_oleh, self.coach)

    def test_student_cannot_create_schedule(self):
        """Pesilat/Anggota tidak diizinkan mengakses halaman form jadwal"""
        self.client.login(username='student_test', password='password123')
        url = reverse('schedule:schedule_create')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('schedule:schedule_list'))

    def test_admin_approve_proposed_schedule(self):
        """Admin menyetujui jadwal latihan yang diajukan pelatih"""
        proposed = JadwalLatihan.objects.create(
            nama_jadwal='Latihan Teknik Selasa',
            hari_indeks=1,  # Selasa
            jam_mulai='16:00:00',
            jam_selesai='18:00:00',
            nama_lokasi='Aula Barat',
            is_aktif=False,
            status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU,
            dibuat_oleh=self.coach
        )

        self.client.login(username='admin_test', password='password123')
        url = reverse('schedule:schedule_approve', kwargs={'jadwal_id': proposed.id})
        response = self.client.post(url, {
            'action': 'setuju',
            'catatan_admin': 'Disetujui untuk semester ini.'
        })
        self.assertRedirects(response, reverse('schedule:schedule_list'))

        proposed.refresh_from_db()
        self.assertEqual(proposed.status_persetujuan, JadwalLatihan.StatusPersetujuan.DISETUJUI)
        self.assertTrue(proposed.is_aktif)
        self.assertEqual(proposed.disetujui_oleh, self.admin)
        self.assertEqual(proposed.catatan_admin, 'Disetujui untuk semester ini.')

    def test_admin_reject_proposed_schedule(self):
        """Admin menolak jadwal latihan yang diajukan pelatih"""
        proposed = JadwalLatihan.objects.create(
            nama_jadwal='Latihan Sparring Minggu',
            hari_indeks=6,  # Minggu
            jam_mulai='13:00:00',
            jam_selesai='15:00:00',
            nama_lokasi='Aula Barat',
            is_aktif=False,
            status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU,
            dibuat_oleh=self.coach
        )

        self.client.login(username='admin_test', password='password123')
        url = reverse('schedule:schedule_approve', kwargs={'jadwal_id': proposed.id})
        response = self.client.post(url, {
            'action': 'tolak',
            'catatan_admin': 'Jadwal bentrok dengan kegiatan lain.'
        })
        self.assertRedirects(response, reverse('schedule:schedule_list'))

        proposed.refresh_from_db()
        self.assertEqual(proposed.status_persetujuan, JadwalLatihan.StatusPersetujuan.DITOLAK)
        self.assertFalse(proposed.is_aktif)
        self.assertEqual(proposed.disetujui_oleh, self.admin)

    def test_coach_cannot_approve_schedule(self):
        """Pelatih tidak memiliki wewenang untuk menyetujui jadwal"""
        proposed = JadwalLatihan.objects.create(
            nama_jadwal='Latihan Gabungan',
            hari_indeks=0,
            jam_mulai='16:00:00',
            jam_selesai='18:00:00',
            nama_lokasi='Dojo',
            is_aktif=False,
            status_persetujuan=JadwalLatihan.StatusPersetujuan.MENUNGGU,
            dibuat_oleh=self.coach
        )

        self.client.login(username='coach_test', password='password123')
        url = reverse('schedule:schedule_approve', kwargs={'jadwal_id': proposed.id})
        response = self.client.post(url, {'action': 'setuju'})
        self.assertRedirects(response, reverse('schedule:schedule_list'))

        proposed.refresh_from_db()
        self.assertEqual(proposed.status_persetujuan, JadwalLatihan.StatusPersetujuan.MENUNGGU)

    def test_admin_delete_schedule_success(self):
        """Admin berhasil menghapus jadwal latihan"""
        self.client.login(username='admin_test', password='password123')
        url = reverse('schedule:schedule_delete', kwargs={'jadwal_id': self.schedule_active.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('schedule:schedule_list'))
        self.assertFalse(JadwalLatihan.objects.filter(id=self.schedule_active.id).exists())

    def test_coach_cannot_delete_schedule(self):
        """Pelatih dilarang menghapus jadwal latihan mingguan"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('schedule:schedule_delete', kwargs={'jadwal_id': self.schedule_active.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('schedule:schedule_list'))
        self.assertTrue(JadwalLatihan.objects.filter(id=self.schedule_active.id).exists())

    def test_student_cannot_delete_schedule(self):
        """Pesilat dilarang menghapus jadwal latihan mingguan"""
        self.client.login(username='student_test', password='password123')
        url = reverse('schedule:schedule_delete', kwargs={'jadwal_id': self.schedule_active.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('schedule:schedule_list'))
        self.assertTrue(JadwalLatihan.objects.filter(id=self.schedule_active.id).exists())

    def test_delete_schedule_requires_post(self):
        """Endpoint hapus jadwal menolak request GET"""
        self.client.login(username='admin_test', password='password123')
        url = reverse('schedule:schedule_delete', kwargs={'jadwal_id': self.schedule_active.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
