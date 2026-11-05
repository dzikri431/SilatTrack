from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('presentation/', views.pitch_presentation, name='presentation'),
    path('pitch/', views.pitch_presentation, name='pitch_presentation'),
]
