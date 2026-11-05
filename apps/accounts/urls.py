from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('admin/create-user/', views.admin_create_user, name='admin_create_user'),
    path('profile/', views.profile_view, name='profile'),
]
