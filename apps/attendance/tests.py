import json
import time
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import User
from apps.core.models import TingkatSabuk, Sekolah
from apps.members.models import AnggotaProfile
from apps.attendance.models import SesiLatihan, Presensi


class AttendanceSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create coach user
        self.coach = User.objects.create_user(
            username='coach_test',
            password='password123',
            role=User.Role.PELATIH,
            first_name='Coach',
            last_name='Testing'
        )

        # Create admin user
        self.admin = User.objects.create_user(
            username='admin_test',
            password='password123',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True
        )

        # Create belt & member
        self.sabuk = TingkatSabuk.objects.create(
            nama_sabuk='Kuning',
            urutan_tingkat=2,
            warna_hex='#FACC15'
        )
        self.student_user = User.objects.create_user(
            username='student_test',
            password='password123',
            role=User.Role.ANGGOTA,
            first_name='Pesilat',
            last_name='Junior'
        )
        self.student = AnggotaProfile.objects.create(
            user=self.student_user,
            nisn='1234567890',
            kelas_sekolah='X PPLG 1',
            sabuk_saat_ini=self.sabuk
        )

        # Create session
        self.sesi = SesiLatihan.objects.create(
            pelatih=self.coach,
            tipe_sesi=SesiLatihan.TipeSesi.REGULER,
            status=SesiLatihan.StatusSesi.DIBUKA,
            tanggal=timezone.localdate(),
            jam_buka=timezone.now(),
        )

    def test_dynamic_qr_token_generation_and_verification(self):
        """Test QR code token HMAC algorithm and validation"""
        token = self.sesi.generate_current_qr_token()
        self.assertIsNotNone(token)
        
        # Verify valid token
        is_valid, msg = self.sesi.verify_qr_token(token)
        self.assertTrue(is_valid)

        # Tampered signature should fail
        tampered = token[:-4] + "ffff"
        is_valid, msg = self.sesi.verify_qr_token(tampered)
        self.assertFalse(is_valid)

        # Token for different session should fail
        other_token = "00000000-0000-0000-0000-000000000000:abcd"
        is_valid, msg = self.sesi.verify_qr_token(other_token)
        self.assertFalse(is_valid)

    def test_coach_quick_attendance_toggle(self):
        """Test HTMX quick attendance toggle endpoint"""
        self.client.login(username='coach_test', password='password123')
        
        url = reverse('attendance:toggle_member_attendance', kwargs={
            'session_id': self.sesi.id,
            'member_id': self.student.user_id
        }) + '?status=HADIR'

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        # Verify DB updated
        presensi = Presensi.objects.get(sesi=self.sesi, anggota=self.student)
        self.assertEqual(presensi.status, Presensi.StatusPresensi.HADIR)
        self.sesi.refresh_from_db()
        self.assertEqual(self.sesi.total_hadir, 1)

    def test_student_qr_scan_submission(self):
        """Test student submitting scanned QR token"""
        self.client.login(username='student_test', password='password123')
        
        token = self.sesi.generate_current_qr_token(interval_seconds=15)
        url = reverse('attendance:submit_qr_scan')

        # Dalam radius 100 meter (sama dengan koordinat SMKN 1 Rongga)
        response = self.client.post(url, {
            'qr_token': token,
            'user_latitude': '-7.0011',
            'user_longitude': '107.2721'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Presensi Berhasil')

        # Verify DB updated
        self.assertTrue(Presensi.objects.filter(sesi=self.sesi, anggota=self.student, status='HADIR').exists())

    def test_excel_export(self):
        """Test downloading attendance sheet in Excel format"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:export_attendance_excel', kwargs={'session_id': self.sesi.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_report_access_restriction_for_student(self):
        """Pastikan siswa / pesilat tidak dapat mengakses fitur laporan resmi sekolah"""
        self.client.login(username='student_test', password='password123')
        
        # Test report index
        res_index = self.client.get(reverse('attendance:report_index'))
        self.assertEqual(res_index.status_code, 302)  # Redirect ke dashboard dengan pesan error

        # Test report print
        res_print = self.client.get(reverse('attendance:report_print'))
        self.assertEqual(res_print.status_code, 302)

        # Test report excel export
        res_excel = self.client.get(reverse('attendance:report_export_excel'))
        self.assertEqual(res_excel.status_code, 403)

    def test_coach_report_index_monthly_and_annual(self):
        """Pastikan pelatih dapat melihat dashboard laporan bulanan dan tahunan dengan grafik"""
        self.client.login(username='coach_test', password='password123')

        # 1. Laporan Bulanan
        res_monthly = self.client.get(reverse('attendance:report_index') + '?periode_tipe=bulanan&bulan=9&tahun=2026')
        self.assertEqual(res_monthly.status_code, 200)
        self.assertIn('donut_chart_json', res_monthly.context)
        self.assertIn('trend_chart_json', res_monthly.context)
        self.assertIn('member_matrix', res_monthly.context)
        self.assertContains(res_monthly, 'reportDonutChart')
        self.assertContains(res_monthly, 'reportTrendChart')

        # 2. Laporan Tahunan
        res_annual = self.client.get(reverse('attendance:report_index') + '?periode_tipe=tahunan&tahun=2026')
        self.assertEqual(res_annual.status_code, 200)
        self.assertEqual(res_annual.context['periode_tipe'], 'tahunan')
        self.assertContains(res_annual, 'Tahun 2026')

    def test_coach_report_print_render(self):
        """Pastikan halaman cetak dokumen resmi A4 ter-render lengkap dengan Kop Surat & grafik"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:report_print') + '?periode_tipe=bulanan&bulan=9&tahun=2026'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'EKSTRAKURIKULER PENCAK SILAT')
        self.assertContains(response, 'LAPORAN REKAPITULASI PRESENSI')
        self.assertContains(response, 'printDonutChart')
        self.assertContains(response, 'printTrendChart')
        self.assertContains(response, 'Kepala Sekolah')

    def test_coach_report_export_excel(self):
        """Pastikan ekspor laporan bulanan/tahunan menghasilkan file spreadsheet Excel .xlsx"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:report_export_excel') + '?periode_tipe=bulanan&bulan=9&tahun=2026'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('Laporan_Presensi_Silat_bulanan', response['Content-Disposition'])

    def test_coach_delete_session_success(self):
        """Pastikan pelatih dapat menghapus sesi latihan dengan sukses"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_delete', kwargs={'session_id': self.sesi.id})
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('attendance:session_list'))
        self.assertFalse(SesiLatihan.objects.filter(id=self.sesi.id).exists())

    def test_student_delete_session_denied(self):
        """Pastikan siswa / anggota ditolak saat mencoba menghapus sesi latihan"""
        self.client.login(username='student_test', password='password123')
        url = reverse('attendance:session_delete', kwargs={'session_id': self.sesi.id})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('attendance:session_list'))
        self.assertTrue(SesiLatihan.objects.filter(id=self.sesi.id).exists())

    def test_session_delete_cascades_presensi(self):
        """Pastikan penghapusan sesi juga menghapus seluruh riwayat presensi terkait (CASCADE)"""
        # Buat presensi untuk sesi ini
        Presensi.objects.create(
            sesi=self.sesi,
            anggota=self.student,
            status=Presensi.StatusPresensi.HADIR,
            metode_presensi=Presensi.MetodePresensi.MANUAL_PELATIH,
            waktu_presensi=timezone.now()
        )
        self.assertTrue(Presensi.objects.filter(sesi=self.sesi).exists())

        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_delete', kwargs={'session_id': self.sesi.id})
        self.client.post(url)

        # Sesi dan presensinya harus terhapus
        self.assertFalse(SesiLatihan.objects.filter(id=self.sesi.id).exists())
        self.assertFalse(Presensi.objects.filter(sesi_id=self.sesi.id).exists())

    def test_delete_session_requires_post(self):
        """Pastikan endpoint hapus sesi menolak request GET (harus POST)"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_delete', kwargs={'session_id': self.sesi.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_coach_create_session_requires_admin_approval(self):
        """Pelatih membuka sesi baru statusnya TERJADWAL dan menunggu persetujuan admin"""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_create')
        data = {
            'tipe_sesi': 'REGULER',
            'materi_latihan': 'Latihan Jurus Tunggal Baku',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        created_session = SesiLatihan.objects.filter(materi_latihan='Latihan Jurus Tunggal Baku').first()
        self.assertIsNotNone(created_session)
        self.assertEqual(created_session.status, SesiLatihan.StatusSesi.TERJADWAL)
        self.assertEqual(created_session.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.MENUNGGU)

    def test_admin_create_session_is_direct_approved_and_open(self):
        """Admin membuka sesi langsung disetujui dan berstatus DIBUKA"""
        self.client.login(username='admin_test', password='password123')
        url = reverse('attendance:session_create')
        data = {
            'tipe_sesi': 'KHUSUS',
            'materi_latihan': 'Latihan Pemantapan TC Kejuaraan',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        created_session = SesiLatihan.objects.filter(materi_latihan='Latihan Pemantapan TC Kejuaraan').first()
        self.assertIsNotNone(created_session)
        self.assertEqual(created_session.status, SesiLatihan.StatusSesi.DIBUKA)
        self.assertEqual(created_session.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.DISETUJUI)

    def test_coach_cannot_open_unapproved_session(self):
        """Pelatih tidak dapat membuka sesi yang belum disetujui admin"""
        unapproved = SesiLatihan.objects.create(
            pelatih=self.coach,
            tipe_sesi=SesiLatihan.TipeSesi.REGULER,
            status=SesiLatihan.StatusSesi.TERJADWAL,
            status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU,
            tanggal=timezone.localdate(),
        )

        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_toggle_status', kwargs={'session_id': unapproved.id})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('attendance:session_detail', kwargs={'session_id': unapproved.id}))

        unapproved.refresh_from_db()
        self.assertEqual(unapproved.status, SesiLatihan.StatusSesi.TERJADWAL)

    def test_admin_approve_session_opens_it(self):
        """Admin menyetujui sesi latihan pelatih -> sesi disetujui & otomatis dibuka"""
        unapproved = SesiLatihan.objects.create(
            pelatih=self.coach,
            tipe_sesi=SesiLatihan.TipeSesi.REGULER,
            status=SesiLatihan.StatusSesi.TERJADWAL,
            status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU,
            tanggal=timezone.localdate(),
        )

        self.client.login(username='admin_test', password='password123')
        url = reverse('attendance:session_approve', kwargs={'session_id': unapproved.id})
        response = self.client.post(url, {
            'action': 'setuju',
            'catatan': 'Disetujui silakan laksanakan latihan.'
        })
        self.assertRedirects(response, reverse('attendance:session_detail', kwargs={'session_id': unapproved.id}))

        unapproved.refresh_from_db()
        self.assertEqual(unapproved.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.DISETUJUI)
        self.assertEqual(unapproved.status, SesiLatihan.StatusSesi.DIBUKA)
        self.assertEqual(unapproved.disetujui_oleh, self.admin)
        self.assertIsNotNone(unapproved.waktu_disetujui)

    def test_admin_reject_session(self):
        """Admin menolak sesi latihan yang diajukan pelatih"""
        unapproved = SesiLatihan.objects.create(
            pelatih=self.coach,
            tipe_sesi=SesiLatihan.TipeSesi.REGULER,
            status=SesiLatihan.StatusSesi.TERJADWAL,
            status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU,
            tanggal=timezone.localdate(),
        )

        self.client.login(username='admin_test', password='password123')
        url = reverse('attendance:session_approve', kwargs={'session_id': unapproved.id})
        response = self.client.post(url, {
            'action': 'tolak',
            'catatan': 'Gedung olahraga dipakai acara lain.'
        })
        self.assertRedirects(response, reverse('attendance:session_detail', kwargs={'session_id': unapproved.id}))

        unapproved.refresh_from_db()
        self.assertEqual(unapproved.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.DITOLAK)
        self.assertEqual(unapproved.status, SesiLatihan.StatusSesi.BATAL)
        self.assertEqual(unapproved.disetujui_oleh, self.admin)

    def test_coach_cannot_approve_session(self):
        """Pelatih tidak dapat menyetujui sesi latihan sendiri atau orang lain"""
        unapproved = SesiLatihan.objects.create(
            pelatih=self.coach,
            tipe_sesi=SesiLatihan.TipeSesi.REGULER,
            status=SesiLatihan.StatusSesi.TERJADWAL,
            status_persetujuan=SesiLatihan.StatusPersetujuanSesi.MENUNGGU,
            tanggal=timezone.localdate(),
        )

        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_approve', kwargs={'session_id': unapproved.id})
        response = self.client.post(url, {'action': 'setuju'})
        self.assertRedirects(response, reverse('attendance:session_detail', kwargs={'session_id': unapproved.id}))

        unapproved.refresh_from_db()
        self.assertEqual(unapproved.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.MENUNGGU)

    def test_face_scan_auto_enrollment(self):
        """Test auto-enrollment wajah pesilat saat pemindaian pertama"""
        self.client.login(username='student_test', password='password123')
        dummy_descriptor = [0.05] * 128

        url = reverse('attendance:submit_face_scan')
        response = self.client.post(url, {
            'sesi_id': self.sesi.id,
            'face_descriptor': json.dumps(dummy_descriptor),
            'face_snapshot': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...',
            'user_latitude': -7.0011,
            'user_longitude': 107.2721
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wajah Berhasil Didaftarkan')

        self.student.refresh_from_db()
        self.assertTrue(self.student.has_face_registered)
        self.assertEqual(len(self.student.face_descriptor), 128)
        self.assertIsNotNone(self.student.face_registered_at)

        # Cek presensi tersimpan
        presensi = Presensi.objects.get(sesi=self.sesi, anggota=self.student)
        self.assertEqual(presensi.status, Presensi.StatusPresensi.HADIR)
        self.assertEqual(presensi.metode_presensi, Presensi.MetodePresensi.FACE_SCAN)

    def test_face_scan_biometric_matching_success(self):
        """Test verifikasi 1:1 biometrik wajah yang cocok (jarak <= 0.60)"""
        # Daftarkan wajah terlebih dahulu
        stored_descriptor = [0.1] * 128
        self.student.face_descriptor = stored_descriptor
        self.student.face_registered_at = timezone.now()
        self.student.save()

        self.client.login(username='student_test', password='password123')
        # Kirim descriptor yang sangat mirip (jarak kecil)
        matching_descriptor = [0.105] * 128

        url = reverse('attendance:submit_face_scan')
        response = self.client.post(url, {
            'sesi_id': self.sesi.id,
            'face_descriptor': json.dumps(matching_descriptor),
            'face_snapshot': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...',
            'user_latitude': -7.0011,
            'user_longitude': 107.2721
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verifikasi Wajah Biometrik Berhasil')

        presensi = Presensi.objects.get(sesi=self.sesi, anggota=self.student)
        self.assertEqual(presensi.status, Presensi.StatusPresensi.HADIR)
        self.assertEqual(presensi.metode_presensi, Presensi.MetodePresensi.FACE_SCAN)
        self.assertLess(presensi.face_distance, 0.60)

    def test_face_scan_biometric_mismatch_rejected(self):
        """Test penolakan presensi saat wajah tidak cocok (jarak > 0.60)"""
        stored_descriptor = [0.1] * 128
        self.student.face_descriptor = stored_descriptor
        self.student.face_registered_at = timezone.now()
        self.student.save()

        self.client.login(username='student_test', password='password123')
        # Kirim descriptor yang jauh berbeda
        different_descriptor = [0.9] * 128

        url = reverse('attendance:submit_face_scan')
        response = self.client.post(url, {
            'sesi_id': self.sesi.id,
            'face_descriptor': json.dumps(different_descriptor),
            'face_snapshot': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...',
            'user_latitude': -7.0011,
            'user_longitude': 107.2721
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Verifikasi Biometrik Gagal')

        # Pastikan tidak tercatat HADIR
        self.assertFalse(Presensi.objects.filter(sesi=self.sesi, anggota=self.student, status=Presensi.StatusPresensi.HADIR).exists())

    def test_face_scan_rejected_outside_geofence(self):
        """Test penolakan presensi wajah jika berada di luar radius 100m"""
        self.client.login(username='student_test', password='password123')
        dummy_descriptor = [0.05] * 128

        url = reverse('attendance:submit_face_scan')
        # Koordinat Jakarta (~150 km dari Bandung dojo -6.914744, 107.609810)
        response = self.client.post(url, {
            'sesi_id': self.sesi.id,
            'face_descriptor': json.dumps(dummy_descriptor),
            'face_snapshot': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP...',
            'user_latitude': -6.2088,
            'user_longitude': 106.8456
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'di luar batas radius 100 meter')

    def test_report_custom_signatories_and_inactive_actions(self):
        """Memverifikasi penyesuaian tanda tangan (Admin, Pelatih, Kepala Sekolah) dan deteksi anggota kurang aktif di laporan."""
        self.client.login(username='admin_test', password='password123')

        custom_kepsek = 'Dr. Ir. H. Ahmad Subarjo, M.Pd'
        custom_nip = '19800101 200501 1 005'

        url = reverse('attendance:report_index') + f'?kepala_sekolah={custom_kepsek}&kepala_sekolah_nip={custom_nip}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['kepala_sekolah_nama'], custom_kepsek)
        self.assertEqual(response.context['kepala_sekolah_nip'], custom_nip)

        # Siswa tanpa kehadiran terdeteksi is_kurang_aktif = True
        member_row = next((item for item in response.context['member_matrix'] if item['anggota'] == self.student), None)
        self.assertIsNotNone(member_row)
        self.assertTrue(member_row['is_kurang_aktif'])

        # Cek halaman print
        print_url = reverse('attendance:report_print') + f'?kepala_sekolah={custom_kepsek}&kepala_sekolah_nip={custom_nip}'
        print_res = self.client.get(print_url)
        self.assertEqual(print_res.status_code, 200)
        self.assertContains(print_res, custom_kepsek)
        self.assertContains(print_res, custom_nip)

        # Cek halaman ekspor excel
        excel_url = reverse('attendance:report_export_excel') + f'?kepala_sekolah={custom_kepsek}&kepala_sekolah_nip={custom_nip}'
        excel_res = self.client.get(excel_url)
        self.assertEqual(excel_res.status_code, 200)
        self.assertEqual(excel_res['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_custom_session_creation_and_coach_approval(self):
        """Pelatih menentukan lokasi dan jam latihan, menunggu persetujuan admin."""
        self.client.login(username='coach_test', password='password123')
        url = reverse('attendance:session_create')

        # Pelatih submit sesi custom
        response = self.client.post(url, {
            'tipe_sesi': SesiLatihan.TipeSesi.REGULER,
            'nama_lokasi': 'Lapangan SMAN 1 Rongga',
            'tanggal': '2026-11-10',
            'jam_mulai': '16:00',
            'jam_selesai': '18:00',
            'materi_latihan': 'Latihan Jurus Tunggal Baku',
        })
        self.assertEqual(response.status_code, 302)

        sesi = SesiLatihan.objects.filter(nama_lokasi='Lapangan SMAN 1 Rongga').first()
        self.assertIsNotNone(sesi)
        self.assertEqual(sesi.lokasi_efektif, 'Lapangan SMAN 1 Rongga')
        self.assertEqual(str(sesi.tanggal), '2026-11-10')
        self.assertEqual(sesi.jam_mulai.strftime('%H:%M'), '16:00')
        self.assertEqual(sesi.jam_selesai.strftime('%H:%M'), '18:00')
        # Harus status MENUNGGU jika dibuat oleh pelatih
        self.assertEqual(sesi.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.MENUNGGU)
        self.assertEqual(sesi.status, SesiLatihan.StatusSesi.TERJADWAL)

        # Admin menyetujui sesi
        self.client.login(username='admin_test', password='password123')
        approve_url = reverse('attendance:session_approve', kwargs={'session_id': sesi.id})
        approve_res = self.client.post(approve_url, {'action': 'setuju'})
        self.assertEqual(approve_res.status_code, 302)

        sesi.refresh_from_db()
        self.assertEqual(sesi.status_persetujuan, SesiLatihan.StatusPersetujuanSesi.DISETUJUI)
        self.assertEqual(sesi.status, SesiLatihan.StatusSesi.DIBUKA)

    def test_save_kepala_sekolah_default_signature(self):
        """Memverifikasi fitur simpan data tanda tangan Kepala Sekolah per sekolah."""
        sek = Sekolah.objects.create(
            nama_sekolah="SMKN 1 Rongga",
            nama_kepala_sekolah="Drs. Lama",
            nip_kepala_sekolah="19600000 000000 1 001"
        )
        self.client.login(username='admin_test', password='password123')
        url = reverse('attendance:report_index')

        response = self.client.post(url, {
            'action': 'save_kepala_sekolah',
            'sekolah_id': sek.id,
            'kepala_sekolah': 'Dr. H. Baru, M.Pd',
            'kepala_sekolah_nip': '19750101 200003 1 002',
            'kepala_sekolah_jabatan': 'Plt. Kepala Sekolah',
        })
        self.assertEqual(response.status_code, 200)

        sek.refresh_from_db()
        self.assertEqual(sek.nama_kepala_sekolah, 'Dr. H. Baru, M.Pd')
        self.assertEqual(sek.nip_kepala_sekolah, '19750101 200003 1 002')
        self.assertEqual(sek.jabatan_kepala_sekolah, 'Plt. Kepala Sekolah')


