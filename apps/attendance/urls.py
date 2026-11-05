from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/create/', views.session_create, name='session_create'),
    path('sessions/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('sessions/<uuid:session_id>/toggle-status/', views.session_toggle_status, name='session_toggle_status'),
    path('sessions/<uuid:session_id>/persetujuan/', views.session_approve, name='session_approve'),
    path('sessions/<uuid:session_id>/delete/', views.session_delete, name='session_delete'),
    path('sessions/<uuid:session_id>/qr-token/', views.get_session_qr, name='get_session_qr'),
    path('sessions/<uuid:session_id>/qr-fullscreen/', views.qr_fullscreen, name='qr_fullscreen'),
    path('sessions/<uuid:session_id>/toggle-attendance/<uuid:member_id>/', views.toggle_member_attendance, name='toggle_member_attendance'),
    path('sessions/<uuid:session_id>/bulk-mark-all/', views.bulk_mark_all_present, name='bulk_mark_all'),
    path('sessions/<uuid:session_id>/export-excel/', views.export_attendance_excel, name='export_attendance_excel'),
    path('sessions/<uuid:session_id>/upload-photo/', views.session_upload_photo, name='session_upload_photo'),
    
    # Presensi Siswa: AI Biometric Face Scanner, Barcode, & Input Manual Mandiri
    path('scanner/', views.scanner_view, name='scanner'),
    path('face-scan/submit/', views.submit_face_scan, name='submit_face_scan'),
    path('scanner/submit/', views.submit_qr_scan, name='submit_qr_scan'),
    path('self-checkin/submit/', views.self_checkin_submit, name='self_checkin_submit'),
    path('permit/create/', views.permit_create, name='permit_create'),

    # Laporan Eksekutif: Cetak Laporan Bulanan / Tahunan & Ekspor Excel
    path('reports/', views.attendance_report_index, name='report_index'),
    path('reports/print/', views.attendance_report_print, name='report_print'),
    path('reports/export-excel/', views.attendance_report_export_excel, name='report_export_excel'),
]
