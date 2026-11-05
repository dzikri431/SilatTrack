import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.core.models import TingkatSabuk, KategoriTanding
from apps.members.models import AnggotaProfile, PelatihProfile
from apps.schedule.models import JadwalLatihan
from apps.attendance.models import SesiLatihan, Presensi

User = get_user_model()


class Command(BaseCommand):
    help = "Seeding data awal untuk SilatTrack (Sabuk, Kategori, Jadwal, Akun Demo)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Menjalankan seed data SilatTrack...")

        # 1. Tingkat Sabuk
        sabuk_data = [
            {"nama": "Putih", "urutan": 1, "hex": "#F8FAFC", "min": 75, "desc": "Tingkat dasar/pemula. Materi: Kuda-kuda, Pasang 1-4, Pola Langkah, Pukulan Dasar."},
            {"nama": "Kuning", "urutan": 2, "hex": "#FACC15", "min": 75, "desc": "Tingkat pembinaan. Materi: Tangkisan luar/dalam, Elakan samping, Pukulan Bandul."},
            {"nama": "Hijau", "urutan": 3, "hex": "#22C55E", "min": 80, "desc": "Tingkat menengah. Materi: Tendangan Sabit/Lurus/T, Tangkapan Bawah, Kuncian Ringan."},
            {"nama": "Biru", "urutan": 4, "hex": "#3B82F6", "min": 80, "desc": "Tingkat mahir. Materi: Bantingan, Jatuhan, Hindaran Gunting, Sambung Rintis."},
            {"nama": "Cokelat", "urutan": 5, "hex": "#854D0E", "min": 85, "desc": "Calon Pendekar. Materi: Jurus Senjata Golok/Toya IPSI, Tanding Pra-Kadet, Kepemimpinan."},
            {"nama": "Hitam", "urutan": 6, "hex": "#0F172A", "min": 90, "desc": "Pendekar Muda / Pelatih Madya. Pembinaan mental spiritual, Wasit Juri, Kurikulum."},
        ]

        sabuk_objects = {}
        for s in sabuk_data:
            obj, _ = TingkatSabuk.objects.get_or_create(
                nama_sabuk=s["nama"],
                defaults={
                    "urutan_tingkat": s["urutan"],
                    "warna_hex": s["hex"],
                    "min_kehadiran_ukt": s["min"],
                    "deskripsi": s["desc"],
                }
            )
            sabuk_objects[s["nama"]] = obj
        self.stdout.write(self.style.SUCCESS(f" Berhasil membuat {len(sabuk_objects)} Tingkat Sabuk."))

        # 2. Kategori Tanding & Seni
        kategori_data = [
            {"nama": "Tanding Putra", "kelas": "Kelas A (39 - 43 kg)", "catatan": "Kategori pertarungan usia remaja/tanding."},
            {"nama": "Tanding Putra", "kelas": "Kelas B (43 - 47 kg)", "catatan": "Kategori pertarungan usia remaja/tanding."},
            {"nama": "Tanding Putri", "kelas": "Kelas A (39 - 43 kg)", "catatan": "Kategori pertarungan tanding putri."},
            {"nama": "Seni Tunggal Baku", "kelas": "Tunggal IPSI", "catatan": "Peragaan jurus baku 140 gerakan tanpa senjata & dengan senjata toya/golok."},
            {"nama": "Seni Ganda", "kelas": "Ganda Bebas", "catatan": "Peragaan koreografi pertarungan berpasangan 3 menit."},
        ]
        kategori_objects = []
        for k in kategori_data:
            obj, _ = KategoriTanding.objects.get_or_create(
                nama=k["nama"],
                kelas_tanding=k["kelas"],
                defaults={"catatan_teknis": k["catatan"]}
            )
            kategori_objects.append(obj)
        self.stdout.write(self.style.SUCCESS(f" Berhasil membuat {len(kategori_objects)} Kategori Tanding/Seni."))

        # 3. Jadwal Latihan Rutin
        jadwal1, _ = JadwalLatihan.objects.get_or_create(
            nama_jadwal="Latihan Rutin Teknik & Jurus",
            defaults={
                "hari_indeks": JadwalLatihan.Hari.SELASA,
                "jam_mulai": datetime.time(15, 30),
                "jam_selesai": datetime.time(17, 30),
                "nama_lokasi": "Aula Serbaguna / Dojo Sekolah",
                "radius_toleransi_meter": 100,
                "is_aktif": True,
            }
        )
        jadwal2, _ = JadwalLatihan.objects.get_or_create(
            nama_jadwal="Latihan Fisik & Sambung Tanding",
            defaults={
                "hari_indeks": JadwalLatihan.Hari.JUMAT,
                "jam_mulai": datetime.time(15, 30),
                "jam_selesai": datetime.time(17, 30),
                "nama_lokasi": "Lapangan Indoor Silat",
                "radius_toleransi_meter": 100,
                "is_aktif": True,
            }
        )
        self.stdout.write(self.style.SUCCESS(" Berhasil membuat Jadwal Latihan Rutin."))

        # 4. User Superadmin
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@sekolah.sch.id",
                "first_name": "Pak Hendra",
                "last_name": "Kurniawan, S.Pd",
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
                "phone_number": "081234567890",
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
        self.stdout.write(self.style.SUCCESS(" Akun Admin/Pembina siap: admin / admin123"))

        # 5. User Pelatih
        pelatih_user, created = User.objects.get_or_create(
            username="pelatih1",
            defaults={
                "email": "coach.joko@silattrack.id",
                "first_name": "Joko",
                "last_name": "Pratama, S.Or",
                "role": User.Role.PELATIH,
                "is_staff": True,
                "phone_number": "082198765432",
            }
        )
        if created:
            pelatih_user.set_password("pelatih123")
            pelatih_user.save()

        PelatihProfile.objects.get_or_create(
            user=pelatih_user,
            defaults={
                "nomor_registrasi": "PEL-IPSI-2024-001",
                "tingkatan_pendekar": "Pelatih Muda / Pendekar Pertama",
                "spesialisasi": "Teknik Tanding & Conditioning Fisik",
                "sertifikasi_sk": "SK-PENGKAB-IPSI-VIII-2023",
            }
        )
        self.stdout.write(self.style.SUCCESS(" Akun Pelatih siap: pelatih1 / pelatih123"))

        # 6. Pesilat Demo (5 Siswa)
        pesilat_list = [
            ("pesilat1", "Ahmad", "Rayhan", "0081122331", "X PPLG 1", "Kuning", AnggotaProfile.Gender.LAKI_LAKI, kategori_objects[0]),
            ("pesilat2", "Siti", "Nurhaliza", "0081122332", "X PPLG 2", "Hijau", AnggotaProfile.Gender.PEREMPUAN, kategori_objects[3]),
            ("pesilat3", "Budi", "Santoso", "0081122333", "XI TJKT 1", "Putih", AnggotaProfile.Gender.LAKI_LAKI, kategori_objects[1]),
            ("pesilat4", "Dian", "Permata", "0081122334", "XI DKV 2", "Biru", AnggotaProfile.Gender.PEREMPUAN, kategori_objects[4]),
            ("pesilat5", "Rizky", "Firmansyah", "0081122335", "XII RPL 1", "Cokelat", AnggotaProfile.Gender.LAKI_LAKI, kategori_objects[0]),
        ]

        created_pesilats = []
        for uname, fn, ln, nisn, kls, sbk, gender, kat in pesilat_list:
            u, c = User.objects.get_or_create(
                username=uname,
                defaults={
                    "email": f"{uname}@sekolah.sch.id",
                    "first_name": fn,
                    "last_name": ln,
                    "role": User.Role.ANGGOTA,
                    "phone_number": "085712345678",
                }
            )
            if c:
                u.set_password("pesilat123")
                u.save()

            prof, _ = AnggotaProfile.objects.get_or_create(
                user=u,
                defaults={
                    "nisn": nisn,
                    "jenis_kelamin": gender,
                    "kelas_sekolah": kls,
                    "sabuk_saat_ini": sabuk_objects[sbk],
                    "kategori_fokus": kat,
                    "status_keanggotaan": AnggotaProfile.MembershipStatus.AKTIF,
                }
            )
            created_pesilats.append(prof)
        self.stdout.write(self.style.SUCCESS(f" Berhasil membuat 5 Akun Pesilat demo (password: pesilat123)"))

        # 7. Sesi Latihan Aktif Hari Ini
        today = timezone.localdate()
        sesi_hari_ini, _ = SesiLatihan.objects.get_or_create(
            tanggal=today,
            status=SesiLatihan.StatusSesi.DIBUKA,
            defaults={
                "jadwal": jadwal1,
                "pelatih": pelatih_user,
                "tipe_sesi": SesiLatihan.TipeSesi.REGULER,
                "materi_latihan": "Pemanasan statis dinamis, Pemantapan Kuda-kuda Tengah, Jurus Tunggal Baku 1-4, dan Latihan Tangkisan Serang.",
                "total_hadir": 2,
            }
        )

        # 8. Data Presensi Awal untuk 2 Pesilat
        Presensi.objects.get_or_create(
            sesi=sesi_hari_ini,
            anggota=created_pesilats[0],
            defaults={
                "status": Presensi.StatusPresensi.HADIR,
                "metode_presensi": Presensi.MetodePresensi.QR_DYNAMIC,
            }
        )
        Presensi.objects.get_or_create(
            sesi=sesi_hari_ini,
            anggota=created_pesilats[1],
            defaults={
                "status": Presensi.StatusPresensi.HADIR,
                "metode_presensi": Presensi.MetodePresensi.QR_DYNAMIC,
            }
        )
        sesi_hari_ini.update_attendance_counters()

        self.stdout.write(self.style.SUCCESS(" Data awal SilatTrack berhasil dimuat sepenuhnya!"))
