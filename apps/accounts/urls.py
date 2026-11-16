from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ── Halaman pilih peran (landing login) ──
    path('login/',                        views.login_view,              name='login'),
    path('login/admin/',                  views.login_admin_view,        name='login_admin'),
    path('login/pelatih/',                views.login_pelatih_view,      name='login_pelatih'),
    path('login/anggota/',                views.login_anggota_view,      name='login_anggota'),
    path('logout/',                       views.logout_view,             name='logout'),
    path('register/',                     views.register_view,           name='register'),

    # ── Lupa & Reset Kata Sandi ──
    path('lupa-kata-sandi/',              views.forgot_password_view,    name='forgot_password'),
    path('reset-password/<str:token>/',   views.reset_password_view,     name='reset_password'),

    # ── Admin: kelola token reset ──
    path('admin/reset-tokens/',           views.admin_reset_tokens_view, name='admin_reset_tokens'),

    # ── Manajemen Akun ──
    path('admin/create-user/',            views.admin_create_user,       name='admin_create_user'),
    path('profile/',                      views.profile_view,            name='profile'),

    # Pelatih: ajukan permohonan akun
    path('request-account/',             views.pelatih_request_account, name='request_account'),
    path('request-account/riwayat/',     views.my_account_requests,     name='my_account_requests'),

    # Admin: kelola permohonan
    path('admin/permohonan-akun/',                       views.admin_account_requests, name='admin_account_requests'),
    path('admin/permohonan-akun/<uuid:request_id>/',     views.admin_review_request,   name='admin_review_request'),
]

