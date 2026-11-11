from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',                        views.login_view,              name='login'),
    path('logout/',                       views.logout_view,             name='logout'),
    path('register/',                     views.register_view,           name='register'),
    path('admin/create-user/',            views.admin_create_user,       name='admin_create_user'),
    path('profile/',                      views.profile_view,            name='profile'),

    # Pelatih: ajukan permohonan akun
    path('request-account/',             views.pelatih_request_account, name='request_account'),
    path('request-account/riwayat/',     views.my_account_requests,     name='my_account_requests'),

    # Admin: kelola permohonan
    path('admin/permohonan-akun/',                       views.admin_account_requests, name='admin_account_requests'),
    path('admin/permohonan-akun/<uuid:request_id>/',     views.admin_review_request,   name='admin_review_request'),
]

