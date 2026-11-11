from .models import AccountRequest


def pending_account_requests(request):
    """
    Inject jumlah permohonan akun yang pending ke semua template.
    Hanya dihitung untuk user yang sudah login dan berperan Admin.
    """
    count = 0
    if request.user.is_authenticated and hasattr(request.user, 'is_admin_role') and request.user.is_admin_role:
        count = AccountRequest.objects.filter(status=AccountRequest.Status.PENDING).count()
    return {'pending_account_requests_count': count}
