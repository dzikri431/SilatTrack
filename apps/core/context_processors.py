from apps.core.models import Perguruan


def perguruan_context(request):
    """
    Context processor global untuk menyediakan data identitas dan logo perguruan silat
    ke seluruh template aplikasi (Header, Navigasi, Login, Sertifikat, KTA, dan Laporan).
    """
    try:
        perguruan = Perguruan.get_solo()
    except Exception:
        perguruan = None

    return {
        'perguruan_info': perguruan,
    }
