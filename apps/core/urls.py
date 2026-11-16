from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('perguruan/', views.perguruan_settings, name='perguruan_settings'),
]

