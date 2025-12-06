# cost_sharing/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Admin URLs
    path('create-user/', views.create_user, name='create_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:pk>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:pk>/', views.delete_user, name='delete_user'),
    path('clear-all-data/', views.clear_all_data, name='clear_all_data'),
    path('manage-bank-accounts/', views.manage_bank_accounts, name='manage_bank_accounts'),
    path('edit-bank-account/<int:pk>/', views.edit_bank_account, name='edit_bank_account'),
    path('delete-bank-account/<int:pk>/', views.delete_bank_account, name='delete_bank_account'),
    
    # Student URLs
    path('fill-cost-sharing/', views.fill_cost_sharing, name='fill_cost_sharing'),
    path('view-cost-sharing/<int:pk>/', views.view_cost_sharing, name='view_cost_sharing'),
    path('print-cost-sharing/<int:pk>/', views.print_cost_sharing, name='print_cost_sharing'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('payment-receipt/<int:pk>/', views.payment_receipt, name='payment_receipt'),
    
    # Cost Sharing Officer URLs
    path('manage-cost-structure/', views.manage_cost_structure, name='manage_cost_structure'),
    path('update-cost-structure/<int:pk>/', views.update_cost_structure, name='update_cost_structure'),
    path('view-students/', views.view_students, name='view_students'),
    path('generate-student-report/', views.generate_student_report, name='generate_student_report'),
    path('download-completed-student-data/', views.download_student_data_after_payment, name='download_completed_student_data'),
    path('download-student-data/', views.download_student_data, name='download_student_data'),
    path('cost-structure/delete/<int:pk>/', views.delete_cost_structure, name='delete_cost_structure'),
    # Inland Revenue Officer URLs
    path('manage-payments/', views.manage_payments, name='manage_payments'),
    path('update-payment/<int:pk>/', views.update_payment, name='update_payment'),
    path('view-payment-status/', views.view_payment_status, name='view_payment_status'),
    path('verify-payment/<int:pk>/', views.verify_payment, name='verify_payment'),
    path('agreement/<int:agreement_id>/', views.view_agreement, name='view_agreement'),
    path('agreement/<int:pk>/set/<str:status>/', views.agreement_set_status, name='agreement_set_status'),
    path('make-payment/', views.make_payment, name='make_payment'),
    path('inland/dashboard/', views.inland_dashboard, name='inland_dashboard'),
    path('bank-account/<int:account_id>/transactions/', views.bank_account_transactions, name='bank_account_transactions'),
    path('export/students.csv', views.export_students_csv, name='export_students_csv'),
    path('export/paid_students.csv', views.export_paid_students_csv, name='export_paid_students_csv'),
    
    # Notice URLs
    path('post-notice/', views.post_notice, name='post_notice'),
    path('view-notices/', views.view_notices, name='view_notices'),
    
    # Feedback URLs
    path('view-feedback/', views.view_feedback, name='view_feedback'),
    path('respond-feedback/<int:pk>/', views.respond_feedback, name='respond_feedback'),
    
    # Registrar Officer URLs
    path('upload-student-data/', views.upload_student_data, name='upload_student_data'),
    
    # Report URLs
    path('generate-report/', views.generate_report, name='generate_report'),
    path('update-account/', views.update_account, name='update_account'),
    path('change-password/', views.change_password, name='change_password'),
    path('view-bank-accounts/', views.view_bank_accounts, name='view_bank_accounts'),
    path('download-student-information/', views.download_student_information, name='download_student_information'),

    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notification/<int:pk>/delete/', views.delete_notification, name='delete_notification'),
     path('notifications/check-new/', views.check_new_notifications, name='check_new_notifications'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name= 'mark_all_notifications_read'),

    # Additional URLs
    path('cost-officer/assigned/', views.cost_officer_assigned_list, name='cost_officer_assigned_list'),
    path('cost-officer/forward/<int:pk>/', views.cost_officer_forward_graduates, name='cost_officer_forward'),
    path('cost-officer/dashboard/', views.cost_officer_dashboard, name='cost_officer_dashboard'),
    # API URLs for cost calculation
    path('api/cost-structure/', views.get_cost_structure, name='get_cost_structure'),
    path('api/available-departments/', views.get_available_departments, name='available_departments'),
    path('api/get-cost-data/', views.get_cost_data, name='get_cost_data'),
    path('fill-cost-sharing/', views.fill_cost_sharing, name='fill_cost_sharing'),
    path('payment-diagnostic/', views.payment_diagnostic, name='payment_diagnostic'),
    path('students-without-agreements/', views.students_without_agreements, name='students_without_agreements'),
    path('students-without-agreements/download/', views.download_students_without_agreements, name='download_students_without_agreements'),
    path('students-without-agreements/send-reminders/', views.send_reminder_notifications, name='send_reminder_notifications'),
    path('diagnostic/', views.diagnostic_view, name='diagnostic'),
    path('student/feedback/', views.student_feedback_list, name='student_feedback_list'),
    path('student/feedback/<int:feedback_id>/', views.student_feedback_detail, name='student_feedback_detail'),   
    path('registrar/students/<str:student_id>/edit/', views.edit_student, name='edit_student'),
    path('agreement/<int:pk>/print/', views.print_agreement, name='print_agreement'),
    path('cost-officer/agreement/<int:pk>/', views.cost_officer_agreement_detail, name='cost_officer_agreement_detail'),
    path('upload-students-to-cost-officer/', views.upload_students_to_cost_officer, name='upload_students_to_cost_officer'),
    path('assign-students-to-cost-officer/', views.upload_students_to_cost_officer, name='upload_students_to_cost_officer'),
    path('cost-officer/assigned/', views.cost_officer_assigned_list, name='cost_officer_assigned_list'),
    path('cost-officer/forward-graduate/<int:pk>/', views.cost_officer_forward_graduates, name='cost_officer_forward_graduates'),
    path('api/student/<int:student_id>/', views.get_student_details, name='get_student_details'),
    path('api/student/<int:student_id>/send-reminder/', views.send_student_reminder, name='send_student_reminder'),
    path('notices/edit/<int:pk>/', views.edit_notice, name='edit_notice'),
]
