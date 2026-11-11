from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.members.models import AnggotaProfile, PelatihProfile, PengajuanHapusAnggota
from apps.core.models import TingkatSabuk, Sekolah


class MemberManagementAndDeletionTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Tingkat Sabuk
        self.sabuk_putih = TingkatSabuk.objects.create(
            nama_sabuk="Putih",
            urutan_tingkat=1,
            warna_hex="#FFFFFF",
            min_kehadiran_ukt=75
        )

        # Admin User
        self.admin = User.objects.create_user(
            username='admin_boss',
            password='adminpassword123',
            role=User.Role.ADMIN,
            first_name='Admin',
            last_name='Pembina'
        )

        # Pelatih User
        self.coach = User.objects.create_user(
            username='coach_budi',
            password='coachpassword123',
            role=User.Role.PELATIH,
            first_name='Budi',
            last_name='Setiawan'
        )
        self.pelatih_profile = PelatihProfile.objects.create(
            user=self.coach,
            nomor_registrasi='REG-PLT-001'
        )

        # Anggota User 1
        self.student_user = User.objects.create_user(
            username='pesilat_andi',
            password='studentpassword123',
            role=User.Role.ANGGOTA,
            first_name='Andi',
            last_name='Pratama'
        )
        self.member_profile = AnggotaProfile.objects.create(
            user=self.student_user,
            nisn='1234567890',
            kelas_sekolah='X PPLG 1',
            sabuk_saat_ini=self.sabuk_putih
        )

    def test_admin_can_edit_member_name_and_sync(self):
        """Admin mengedit nama dan profil anggota, otomatis tersinkronisasi."""
        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:member_edit', kwargs={'user_id': self.student_user.id})

        post_data = {
            'first_name': 'Andi',
            'last_name': 'Kurniawan Pratama',
            'nisn': '1234567890',
            'kelas_sekolah': 'X PPLG 2',
            'status_keanggotaan': 'AKTIF',
            'sabuk_id': str(self.sabuk_putih.id),
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.student_user.refresh_from_db()
        self.member_profile.refresh_from_db()
        self.assertEqual(self.student_user.get_full_name(), 'Andi Kurniawan Pratama')
        self.assertEqual(self.member_profile.kelas_sekolah, 'X PPLG 2')

    def test_admin_can_delete_member_directly(self):
        """Admin dapat menghapus anggota secara langsung."""
        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:member_delete', kwargs={'user_id': self.student_user.id})

        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(id=self.student_user.id).exists())
        self.assertFalse(AnggotaProfile.objects.filter(user_id=self.student_user.id).exists())

    def test_coach_delete_requires_admin_approval(self):
        """Pelatih yang ingin menghapus anggota tidak langsung menghapus, melainkan membuat permohonan izin ke Admin."""
        self.client.login(username='coach_budi', password='coachpassword123')
        url = reverse('members:member_delete', kwargs={'user_id': self.student_user.id})

        post_data = {
            'alasan_penghapusan': 'Siswa pindah sekolah ke luar kota.'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Anggota masih ada dalam database
        self.assertTrue(AnggotaProfile.objects.filter(user_id=self.student_user.id).exists())

        # Permohonan izin hapus dibuat dengan status MENUNGGU
        pengajuan = PengajuanHapusAnggota.objects.filter(anggota=self.member_profile).first()
        self.assertIsNotNone(pengajuan)
        self.assertEqual(pengajuan.diajukan_oleh, self.coach)
        self.assertEqual(pengajuan.status, PengajuanHapusAnggota.StatusPengajuan.MENUNGGU)
        self.assertEqual(pengajuan.alasan, 'Siswa pindah sekolah ke luar kota.')

    def test_admin_can_approve_coach_delete_request(self):
        """Admin menyetujui permohonan hapus dari pelatih -> anggota terhapus."""
        pengajuan = PengajuanHapusAnggota.objects.create(
            anggota=self.member_profile,
            diajukan_oleh=self.coach,
            alasan='Siswa mengundurkan diri.',
            status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
        )

        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:approve_delete_request', kwargs={'request_id': pengajuan.id})

        response = self.client.post(url, {'action': 'setuju'}, follow=True)
        self.assertEqual(response.status_code, 200)

        # Anggota terhapus dari sistem
        self.assertFalse(User.objects.filter(id=self.student_user.id).exists())

    def test_admin_can_reject_coach_delete_request(self):
        """Admin menolak permohonan hapus dari pelatih -> anggota tetap ada."""
        pengajuan = PengajuanHapusAnggota.objects.create(
            anggota=self.member_profile,
            diajukan_oleh=self.coach,
            alasan='Alasan tidak kuat.',
            status=PengajuanHapusAnggota.StatusPengajuan.MENUNGGU
        )

        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:approve_delete_request', kwargs={'request_id': pengajuan.id})

        response = self.client.post(url, {'action': 'tolak', 'catatan_admin': 'Alasan belum diverifikasi.'}, follow=True)
        self.assertEqual(response.status_code, 200)

        pengajuan.refresh_from_db()
        self.assertEqual(pengajuan.status, PengajuanHapusAnggota.StatusPengajuan.DITOLAK)
        self.assertTrue(AnggotaProfile.objects.filter(user_id=self.student_user.id).exists())

    def test_reset_face_registration(self):
        """Admin atau Pelatih dapat mereset data biometrik wajah siswa."""
        self.member_profile.face_descriptor = [0.1] * 128
        self.member_profile.save()

        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:reset_face_registration', kwargs={'user_id': self.student_user.id})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)

        self.member_profile.refresh_from_db()
        self.assertIsNone(self.member_profile.face_descriptor)
        self.assertFalse(self.member_profile.has_face_registered)

    def test_public_parent_portal(self):
        """Orang tua dapat melihat data kehadiran siswa tanpa login via NISN."""
        url = reverse('members:public_parent_portal') + '?nisn=1234567890'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Andi Pratama')
        self.assertContains(response, 'X PPLG 1')
        self.assertContains(response, 'Portal Transparansi Wali Murid')

    def test_calculate_attendance_streak(self):
        """Menghitung streak sesi hadir secara akurat."""
        self.assertEqual(self.member_profile.calculate_attendance_streak(), 0)

    def test_member_list_filter_kurang_aktif(self):
        """Memverifikasi filter tab kurang aktif menyaring anggota yang kehadirannya di bawah 50%."""
        self.client.login(username='admin_boss', password='adminpassword123')

        # Buat anggota aktif kedua
        student2_user = User.objects.create_user(
            username='pesilat_aktif',
            password='password123',
            role=User.Role.ANGGOTA,
            first_name='Bintang',
            last_name='Sakti'
        )
        AnggotaProfile.objects.create(
            user=student2_user,
            nisn='9998887776',
            kelas_sekolah='XI IPA 1',
            sabuk_saat_ini=self.sabuk_putih,
            status_keanggotaan=AnggotaProfile.MembershipStatus.AKTIF
        )

        url = reverse('members:member_list') + '?tab=kurang_aktif'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_kurang_aktif', response.context)
        self.assertEqual(response.context['active_tab'], 'kurang_aktif')
        # Siswa tanpa riwayat sesi hadir terdeteksi sebagai kurang aktif (0%)
        self.assertContains(response, 'Kurang Aktif')

    def test_delete_member_with_next_redirect(self):
        """Memverifikasi redirect parameter next saat Admin menghapus anggota kurang aktif."""
        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:member_delete', kwargs={'user_id': self.student_user.id})
        target_next = reverse('attendance:report_index') + '?tab=kurang_aktif'

        response = self.client.post(url, {'next': target_next})
        self.assertRedirects(response, target_next)
        self.assertFalse(User.objects.filter(id=self.student_user.id).exists())

    def test_nisn_strict_10_digit_validation(self):
        """Memverifikasi validasi NISN harus tepat 10 digit numerik."""
        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:member_edit', kwargs={'user_id': self.student_user.id})

        # Coba update dengan 7 digit -> harus ditolak
        self.client.post(url, {
            'first_name': 'Andi',
            'last_name': 'Pratama',
            'nisn': '1234567',
            'kelas_sekolah': 'X PPLG 1',
        })
        self.member_profile.refresh_from_db()
        self.assertNotEqual(self.member_profile.nisn, '1234567')

        # Update dengan 10 digit numerik -> harus sukses
        self.client.post(url, {
            'first_name': 'Andi',
            'last_name': 'Pratama',
            'nisn': '0098765432',
            'kelas_sekolah': 'X PPLG 1',
        })
        self.member_profile.refresh_from_db()
        self.assertEqual(self.member_profile.nisn, '0098765432')

    def test_member_school_filtering_and_assignment(self):
        """Memverifikasi filter anggota berdasarkan sekolah."""
        sek1 = Sekolah.objects.create(nama_sekolah="SMKN 1 Rongga")
        sek2 = Sekolah.objects.create(nama_sekolah="SMAN 1 Rongga")

        self.member_profile.sekolah = sek1
        self.member_profile.save()

        user2 = User.objects.create_user(
            username='pesilat_bambang',
            password='password123',
            role=User.Role.ANGGOTA,
            first_name='Bambang'
        )
        AnggotaProfile.objects.create(
            user=user2,
            nisn='0088776655',
            kelas_sekolah='XI IPS 2',
            sekolah=sek2
        )

        self.client.login(username='admin_boss', password='adminpassword123')
        # Filter sek1 -> hanya Andi
        res_sek1 = self.client.get(reverse('members:member_list') + f'?sekolah={sek1.id}')
        self.assertContains(res_sek1, 'Andi')
        self.assertNotContains(res_sek1, 'Bambang')

        # Filter sek2 -> hanya Bambang
        res_sek2 = self.client.get(reverse('members:member_list') + f'?sekolah={sek2.id}')
        self.assertContains(res_sek2, 'Bambang')
        self.assertNotContains(res_sek2, 'Andi')

    def test_member_id_card_view(self):
        """Memverifikasi tampilan KTA Pesilat memuat nama, NISN, sabuk, dan kode QR."""
        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:id_card', kwargs={'user_id': self.student_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Andi Pratama')
        self.assertContains(response, '1234567890')
        self.assertContains(response, 'Putih')
        self.assertContains(response, '<svg')
        self.assertContains(response, 'KARTU TANDA ANGGOTA (KTA)')

    def test_coach_id_card_view(self):
        """Memverifikasi tampilan ID Card Pelatih memuat lisensi, registrasi, dan kode QR."""
        self.client.login(username='admin_boss', password='adminpassword123')
        url = reverse('members:id_card', kwargs={'user_id': self.coach.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Budi Setiawan')
        self.assertContains(response, 'REG-PLT-001')
        self.assertContains(response, '<svg')
        self.assertContains(response, 'KARTU LISENSI PELATIH')

    def test_my_id_card_redirect(self):
        """Memverifikasi pintasan my-card mengarahkan ke ID Card pengguna aktif."""
        self.client.login(username='pesilat_andi', password='studentpassword123')
        url = reverse('members:my_id_card')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('members:id_card', kwargs={'user_id': self.student_user.id}))

    def test_id_card_print_permission_restriction(self):
        """
        Memverifikasi bahwa anggota hanya bisa melihat pratinjau KTA tanpa tombol cetak,
        sedangkan Pelatih dan Admin memiliki akses cetak fisik.
        """
        # 1. Login sebagai Anggota (Pesilat) -> Tidak boleh ada tombol cetak
        self.client.login(username='pesilat_andi', password='studentpassword123')
        url = reverse('members:id_card', kwargs={'user_id': self.student_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mode Pratinjau')
        self.assertNotContains(response, 'Cetak / Simpan PDF')

        # 2. Login sebagai Pelatih -> Harus memiliki tombol cetak
        self.client.login(username='coach_budi', password='coachpassword123')
        response_coach = self.client.get(url)
        self.assertEqual(response_coach.status_code, 200)
        self.assertContains(response_coach, 'Cetak / Simpan PDF')

        # 3. Login sebagai Admin -> Harus memiliki tombol cetak
        self.client.login(username='admin_boss', password='adminpassword123')
        response_admin = self.client.get(url)
        self.assertEqual(response_admin.status_code, 200)
        self.assertContains(response_admin, 'Cetak / Simpan PDF')

    def test_member_certificate_view(self):
        """Memverifikasi sertifikat resmi anggota menampilkan NISN, nama, nomor sertifikat dan QR Code."""
        self.client.login(username='pesilat_andi', password='studentpassword123')
        url = reverse('members:certificate', kwargs={'user_id': self.student_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Andi Pratama')
        self.assertContains(response, '1234567890')
        self.assertContains(response, 'SERTIFIKAT KOMPETENSI')
        self.assertContains(response, '<svg')

    def test_coach_certificate_view(self):
        """Memverifikasi sertifikat lisensi pelatih menampilkan lisensi kepelatihan resmi."""
        self.client.login(username='coach_budi', password='coachpassword123')
        url = reverse('members:certificate', kwargs={'user_id': self.coach.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Budi Setiawan')
        self.assertContains(response, 'REG-PLT-001')
        self.assertContains(response, 'SERTIFIKAT LISENSI KEPELATIHAN')
        self.assertContains(response, '<svg')

    def test_my_certificate_redirect(self):
        """Memverifikasi pintasan my-certificate mengarahkan ke sertifikat pengguna aktif."""
        self.client.login(username='pesilat_andi', password='studentpassword123')
        url = reverse('members:my_certificate')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('members:certificate', kwargs={'user_id': self.student_user.id}))


