from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('tambah/', views.schedule_create, name='schedule_create'),
    path('<int:jadwal_id>/hapus/', views.schedule_delete, name='schedule_delete'),
    path('<int:jadwal_id>/persetujuan/', views.schedule_approve, name='schedule_approve'),
]
