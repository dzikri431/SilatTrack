from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('<uuid:user_id>/', views.member_detail, name='member_detail'),
    path('<uuid:user_id>/edit/', views.member_edit, name='member_edit'),
    path('<uuid:user_id>/delete/', views.member_delete, name='member_delete'),
    path('<uuid:user_id>/reset-face/', views.reset_face_registration, name='reset_face_registration'),
    path('delete-request/<uuid:request_id>/approve/', views.approve_delete_request, name='approve_delete_request'),
    path('transparansi-wali/', views.public_parent_portal, name='public_parent_portal'),
]
