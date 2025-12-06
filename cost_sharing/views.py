import io
import csv
import json
import random
import datetime
import traceback
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import models 
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

from .models import (
    User, CostSharingAgreement, CostStructure, Payment, Notice, Feedback, 
    StudentData, BankAccount, Notification
)
from django.conf import settings
from .forms import (
    CustomUserCreationForm, UserUpdateForm, CostSharingForm, CostStructureForm, 
    PaymentForm, StudentPaymentForm, PaymentVerificationForm, NoticeForm, 
    FeedbackForm, StudentDataForm, BankAccountForm, AdminUserUpdateForm
)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_admin(user):
    return user.role == 'admin'

def is_cost_sharing_officer(user):
    return user.role == 'cost_sharing_officer'

def is_registrar_officer(user):
    return user.role == 'registrar_officer'

def is_inland_revenue_officer(user):
    return user.role == 'inland_revenue_officer'

def is_student(user):
    return user.role == 'student'

def get_current_academic_year():
    """
    Get current academic year as an integer (just the starting year)
    """
    current_year = datetime.datetime.now().year
    return current_year  # Returns 2025 
def create_notification(recipient, title, message, notification_type='system', 
                       related_object_id=None, related_object_type=None):
    """Helper function to create notifications AND send emails"""
    
    # Create the notification in database
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_object_id=related_object_id,
        related_object_type=related_object_type
    )
    
    # Send email notification (if recipient has email)
    if recipient.email:
        try:
            subject = f"🔔 OCSMS Notification: {title}"
            
            # Create beautiful email template
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 5px; }}
        .notification {{ background: white; padding: 20px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        .btn {{ display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 OCSMS Notification</h1>
            <p>Mekdela Amba University - Cost Sharing Management System</p>
        </div>
        
        <div class="content">
            <h2>{title}</h2>
            
            <div class="notification">
                <p><strong>Hello {recipient.first_name or recipient.username},</strong></p>
                <p>{message}</p>
                <p><strong>Time:</strong> {timezone.now().strftime('%Y-%m-%d %H:%M')}</p>
                <p><strong>Notification Type:</strong> {notification_type.title()}</p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="{settings.SITE_URL}/notifications/" class="btn">
                    View All Notifications
                </a>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated notification from OCSMS.</p>
            <p>If you believe you received this in error, please ignore this email.</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Plain text version
            plain_message = f"""
OCSMS Notification

Hello {recipient.first_name or recipient.username},

{title}

{message}

Time: {timezone.now().strftime('%Y-%m-%d %H:%M')}
Notification Type: {notification_type}

View all notifications: {settings.SITE_URL}/notifications/

This is an automated notification from OCSMS.
            """
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_message,
                fail_silently=True,  # Set to True to avoid breaking the app if email fails
            )
            
            print(f"✅ Email notification sent to {recipient.email}")
            
        except Exception as e:
            print(f"❌ Failed to send email notification to {recipient.email}: {e}")
            # Don't raise exception - we don't want to break the main functionality
    
    return notification
    
def get_notices_for_role(role):
    """
    Return active notices visible to the given role.
    """
    now = timezone.now()
    qs = Notice.objects.filter(is_active=True, expiry_date__gt=now)
    result = []

    for notice in qs:
        # audience 'all' is always visible
        if notice.audience == 'all':
            result.append(notice)
            continue

        # For role-based audience, check if user's role is in target_roles
        if notice.audience == 'role_based' and role:
            target_roles = notice.target_roles or []
            if role in target_roles:
                result.append(notice)

    # Sort by created_at descending
    return sorted(result, key=lambda x: x.created_at, reverse=True)

def _model_has_field(model, name):
    return name in [f.name for f in model._meta.get_fields()]

# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me', False)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if remember_me:
                # Remember for 30 days
                request.session.set_expiry(30 * 24 * 60 * 60)
            else:
                # Session expires when browser closes
                request.session.set_expiry(0)
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    """Handle forgot password with REAL email sending"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            # Create beautiful email content
            subject = 'Password Reset Request - OCSMS'
            
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ background: #f8f9fa; padding: 30px; border-radius: 5px; }}
        .button {{ display: inline-block; background: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        .reset-link {{ background: #e9ecef; padding: 15px; border-radius: 5px; word-break: break-all; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 OCSMS</h1>
            <p>Mekdela Amba University - Cost Sharing Management System</p>
        </div>
        
        <div class="content">
            <h2>Password Reset Request</h2>
            
            <p>Hello <strong>{user.first_name or user.username}</strong>,</p>
            
            <p>You requested a password reset for your OCSMS account.</p>
            
            <div style="text-align: center;">
                <a href="{reset_link}" class="button">
                    Reset Your Password
                </a>
            </div>
            
            <p>Or copy and paste this link in your browser:</p>
            <div class="reset-link">
                {reset_link}
            </div>
            
            <p><strong>Important:</strong> This link will expire in 24 hours.</p>
            
            <p>If you didn't request this password reset, please ignore this email.</p>
        </div>
        
        <div class="footer">
            <p>Best regards,<br>OCSMS Team<br>Mekdela Amba University</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Plain text version for email clients that don't support HTML
            plain_message = f"""
Password Reset Request - OCSMS

Hello {user.first_name or user.username},

You requested a password reset for your OCSMS account at Mekdela Amba University.

Click the link below to reset your password:
{reset_link}

This link will expire in 24 hours.

If you didn't request this reset, please ignore this email.

Best regards,
OCSMS Team
Mekdela Amba University
"""
            try:
                print(f"🔄 Attempting to send email to: {email}")
                print(f"📧 Using SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
                
                # Send email with both HTML and plain text
                send_mail(
                    subject=subject,
                    message=plain_message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                print(f"✅ Email sent successfully to: {email}")
                
                messages.success(request, 
                    '✅ Password reset link has been sent to your email address! '
                    'Please check your inbox (and spam folder if you don\'t see it).'
                )
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Email sending failed: {error_msg}")
                
                # Provide specific error messages
                if "authentication failed" in error_msg.lower():
                    messages.error(request, 
                        '❌ Email authentication failed. '
                        'Please check your email configuration in settings.py'
                    )
                elif "connection refused" in error_msg.lower():
                    messages.error(request, 
                        '❌ Cannot connect to email server. '
                        'Please check your internet connection and email settings.'
                    )
                else:
                    messages.error(request, 
                        f'❌ Failed to send email: {error_msg}'
                    )
                
                # Fallback: show link on page
                return render(request, 'forgot_password.html', {
                    'manual_reset_link': reset_link,
                    'username': user.username,
                    'email_failed': True,
                    'error_details': error_msg
                })
            
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, '❌ No user found with this email address.')
    
    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):
    """Handle password reset with token validation"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            # Validate passwords
            if not password1 or not password2:
                messages.error(request, 'Please fill in both password fields.')
                return render(request, 'reset_password.html')
            
            if password1 != password2:
                messages.error(request, 'Passwords do not match. Please try again.')
                return render(request, 'reset_password.html')
            
            # Check password strength
            if len(password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'reset_password.html')
            
            # Check for uppercase, lowercase, and numbers
            has_upper = any(c.isupper() for c in password1)
            has_lower = any(c.islower() for c in password1)
            has_digit = any(c.isdigit() for c in password1)
            
            if not (has_upper and has_lower and has_digit):
                messages.error(request, 
                    'Password must contain at least one uppercase letter, one lowercase letter, and one number.'
                )
                return render(request, 'reset_password.html')
            
            try:
                # Set new password
                user.set_password(password1)
                user.save()
                
                # Update session auth hash if user is logged in
                if request.user.is_authenticated:
                    update_session_auth_hash(request, user)
                
                # Create success notification
                create_notification(
                    recipient=user,
                    title="Password Reset Successful",
                    message="Your password has been reset successfully.",
                    notification_type='system'
                )
                
                messages.success(request, 
                    'Your password has been reset successfully! You can now login with your new password.'
                )
                
                # Print success message to console
                print(f"✅ Password reset successful for user: {user.username}")
                
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error resetting password: {str(e)}')
                print(f"❌ Password reset error: {e}")
        
        # GET request - show reset form
        return render(request, 'reset_password.html', {
            'valid_link': True,
            'user': user
        })
    else:
        messages.error(request, 
            'Invalid or expired password reset link. '
            'Please request a new password reset link.'
        )
        return redirect('forgot_password')

# =============================================================================
# DASHBOARD & ACCOUNT MANAGEMENT
# =============================================================================
@login_required
def dashboard(request):
    user = request.user

    # Ensure superusers have admin role
    if user.is_superuser and not user.role:
        user.role = 'admin'
        user.save()

    current_year = get_current_academic_year()

    # Initialize variables for registrar officer
    students_uploaded = 0
    students_without_agreements_count = 0
    students_with_agreements = 0
    compliance_rate = 0
    recent_students = []
    all_students = StudentData.objects.none()
    departments = []
    selected_department = None

    # Base querysets
    agreements_qs = CostSharingAgreement.objects.none()
    cost_structures_qs = CostStructure.objects.all()
    
    # Handle feedback status field
    if _model_has_field(Feedback, 'status'):
        pending_feedback_qs = Feedback.objects.filter(status__iexact='pending')
    else:
        pending_feedback_qs = Feedback.objects.filter()

    # Get user role and notices
    role = getattr(user, 'role', None)
    try:
        active_notices = get_notices_for_role(role)
    except NameError:
        active_notices = list(Notice.objects.filter(is_active=True).order_by('-created_at')[:10])

    # Get accepted agreements
    accepted_agreements_qs = CostSharingAgreement.objects.filter(status__iexact='accepted')
    if _model_has_field(CostSharingAgreement, 'date_accepted'):
        accepted_agreements_qs = accepted_agreements_qs.order_by('-date_accepted')
    accepted_agreements_qs = accepted_agreements_qs[:5]

    # Base statistics
    total_users = User.objects.count()
    total_agreements = CostSharingAgreement.objects.count()
    total_payments = Payment.objects.count()
    total_bank_accounts = BankAccount.objects.count()
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    recent_feedbacks = Feedback.objects.all().order_by('-date_submitted')[:5]

    # Base context shared by all roles
    base_context = {
        'agreements': agreements_qs,
        'cost_structures': cost_structures_qs,
        'pending_feedback': pending_feedback_qs,
        'active_notices': active_notices,
        'accepted_agreements': accepted_agreements_qs,
        'total_users': total_users,
        'total_agreements': total_agreements,
        'total_payments': total_payments,
        'total_bank_accounts': total_bank_accounts,
        'recent_users': recent_users,
        'recent_feedbacks': recent_feedbacks,
        'current_year': current_year,
    }

    # Admin role
    if role == 'admin' or user.is_superuser:
        return render(request, 'dashboard_admin.html', base_context)

    # Cost sharing officer role
    if role == 'cost_sharing_officer':
        pending_qs = CostSharingAgreement.objects.filter(status__iexact='pending')
        if _model_has_field(CostSharingAgreement, 'date_filled'):
            pending_qs = pending_qs.order_by('-date_filled')
        
        # Get assigned students
        assigned_students = StudentData.objects.all().order_by('-created_at')
        
        # Find students with agreements
        all_agreements = CostSharingAgreement.objects.all()
        students_with_agreements_from_relations = all_agreements.exclude(
            student__isnull=True
        ).values_list('student__student_id', flat=True).distinct()
        
        agreement_full_names = all_agreements.values_list('full_name', flat=True).distinct()
        students_with_matching_names = StudentData.objects.filter(
            full_name__in=agreement_full_names
        ).values_list('student_id', flat=True)
        
        students_with_agreements_ids = list(students_with_agreements_from_relations) + list(students_with_matching_names)
        students_with_agreements_ids = list(filter(None, students_with_agreements_ids))
        students_with_agreements_ids = list(set(students_with_agreements_ids))
        
        # Mark students with agreements
        for student in assigned_students:
            student.has_agreement = student.student_id in students_with_agreements_ids
        
        context = {
            **base_context,
            'agreements': pending_qs,
            'assigned_students': assigned_students,
        }
        return render(request, 'dashboard_cost_sharing_officer.html', context)

    # Registrar officer role
    if role == 'registrar_officer':
        students_uploaded = StudentData.objects.count()
        all_agreements = CostSharingAgreement.objects.all()
        
        # Find students with agreements
        students_with_agreements_from_relations = all_agreements.exclude(
            student__isnull=True
        ).values_list('student__student_id', flat=True).distinct()
        
        agreement_full_names = all_agreements.values_list('full_name', flat=True).distinct()
        students_with_matching_names = StudentData.objects.filter(
            full_name__in=agreement_full_names
        ).values_list('student_id', flat=True)
        
        students_with_agreements_ids = list(students_with_agreements_from_relations) + list(students_with_matching_names)
        students_with_agreements_ids = list(filter(None, students_with_agreements_ids))
        students_with_agreements_ids = list(set(students_with_agreements_ids))
        
        # Calculate statistics
        students_without_agreements_count = StudentData.objects.exclude(
            student_id__in=students_with_agreements_ids
        ).count()
        
        students_with_agreements = students_uploaded - students_without_agreements_count
        
        if students_uploaded > 0:
            compliance_rate = (students_with_agreements / students_uploaded) * 100
        
        recent_students = StudentData.objects.all().order_by('-created_at')[:5]
        all_students = StudentData.objects.all().order_by('-created_at')
        
        # Mark students with agreements
        for student in all_students:
            student.has_agreement = student.student_id in students_with_agreements_ids
        
        # Department filtering
        department_filter = request.GET.get('department')
        if department_filter:
            all_students = all_students.filter(department__icontains=department_filter)
        
        # Pagination
        paginator = Paginator(all_students, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        departments = StudentData.objects.values_list('department', flat=True).distinct()
        cost_officers = User.objects.filter(role='cost_sharing_officer', is_active=True)
        
        context = {
            **base_context,
            'students_uploaded': students_uploaded,
            'students_without_agreements_count': students_without_agreements_count,
            'students_with_agreements': students_with_agreements,
            'compliance_rate': compliance_rate,
            'recent_students': recent_students,
            'all_students': page_obj,
            'departments': departments,
            'selected_department': department_filter,
            'cost_officers': cost_officers,
            'students_with_agreements_ids': students_with_agreements_ids,
        }
        return render(request, 'dashboard_registrar_officer.html', context)

    # Inland revenue officer role
    if role == 'inland_revenue_officer':
        # Get graduate students
        graduate_students = StudentData.objects.filter(is_graduate=True)
        
        # Calculate totals for each graduate student
        student_totals = []
        
        for student_data in graduate_students:
            # Find all agreements for this student
            agreements = CostSharingAgreement.objects.filter(
                Q(student__student_id=student_data.student_id) | 
                Q(full_name=student_data.full_name)
            )
            
            # Calculate totals across ALL agreements
            total_cost_all = 0
            total_paid_all = 0
            
            for agreement in agreements:
                # Add agreement cost
                if hasattr(agreement, 'total_cost') and agreement.total_cost:
                    total_cost_all += float(agreement.total_cost)
                
                # Add payments for this agreement
                payments = Payment.objects.filter(agreement=agreement)
                agreement_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
                total_paid_all += float(agreement_paid)
            
            # Calculate remaining balance
            remaining_balance_all = total_cost_all - total_paid_all
            
            # Determine payment status
            if total_cost_all > 0:
                if remaining_balance_all <= 0:
                    payment_status = 'Paid'
                    status_class = 'bg-success'
                elif total_paid_all > 0:
                    payment_status = 'Partial'
                    status_class = 'bg-warning'
                else:
                    payment_status = 'Unpaid'
                    status_class = 'bg-danger'
            else:
                payment_status = 'No Agreement'
                status_class = 'bg-secondary'
            
            student_totals.append({
                'student_id': student_data.student_id,
                'full_name': student_data.full_name,
                'department': student_data.department,
                'total_cost_all': total_cost_all,
                'total_paid_all': total_paid_all,
                'remaining_balance_all': remaining_balance_all,
                'payment_status': payment_status,
                'status_class': status_class,
                'agreement_count': agreements.count(),
                'has_agreement': agreements.exists(),
                'is_graduate': student_data.is_graduate,
            })
        
        # Get payment statistics
        payments = Payment.objects.all()
        total_collected = payments.filter(status__in=['partial','verified','completed']).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0
        
        context = {
            **base_context,
            'student_totals': student_totals,
            'payments': payments,
            'total_collected': total_collected,
            'total_students': len(student_totals),
            'graduate_students_count': len(student_totals),
        }
        return render(request, 'dashboard_inland_revenue_officer.html', context)

    # Student role
    if role == 'student':
        agreements = CostSharingAgreement.objects.filter(student=user)
        
        non_rejected_agreements = agreements.exclude(status='rejected')
        approved_agreements = agreements.filter(status='approved')
        pending_agreements = agreements.filter(status='pending')
        active_agreement = non_rejected_agreements.filter(status__in=['approved', 'pending']).first()
        
        payments = Payment.objects.filter(agreement__student=user)
        recent_payments = payments.order_by('-date_paid')[:5]
        all_payments = payments.order_by('-date_paid')
        bank_accounts = BankAccount.objects.all()
        notices = Notice.objects.filter(is_active=True).order_by('-created_at')[:5]
        
        context = {
            **base_context,
            'agreements': agreements,
            'non_rejected_agreements': non_rejected_agreements,
            'approved_agreements': approved_agreements,
            'pending_agreements': pending_agreements,
            'active_agreement': active_agreement,
            'recent_payments': recent_payments,
            'all_payments': all_payments,
            'payments': payments,
            'feedbacks': Feedback.objects.filter(student=user),
            'bank_accounts': bank_accounts,
            'notices': notices,
            'current_academic_year': f"{current_year}-{current_year + 1}",
            
            'has_agreements': agreements.exists(),
            'has_approved_agreements': approved_agreements.exists(),
            'has_pending_agreements': pending_agreements.exists(),
            'has_payments': payments.exists(),
            'has_bank_accounts': bank_accounts.exists(),
        }
        
        # Debug logging
        print(f"🎯 DEBUG for student {user.username}:")
        print(f"   - Agreements: {agreements.count()}")
        print(f"   - Approved: {approved_agreements.count()}")
        print(f"   - Pending: {pending_agreements.count()}")
        print(f"   - Payments: {payments.count()}")
        print(f"   - Bank accounts: {bank_accounts.count()}")
        
        return render(request, 'dashboard_student.html', context)
    
    # Fallback for unrecognized roles
    return render(request, 'dashboard_base.html', base_context)
@login_required
def update_account(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.email = form.cleaned_data.get('email', user.email)
            user.phone = form.cleaned_data.get('phone', user.phone)
            user.student_id = form.cleaned_data.get('student_id', user.student_id)
            user.department = form.cleaned_data.get('department', user.department)
            user.year_of_study = form.cleaned_data.get('year_of_study', user.year_of_study)
            user.save()
            messages.success(request, 'Your account has been updated successfully!')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'update_account.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verify current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('update_account')
        
        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('update_account')
        
        # Check password length
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('update_account')
        
        # Set new password
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Your password has been changed successfully!')
        return redirect('login')
    
    return redirect('update_account')

# =============================================================================
# USER MANAGEMENT (ADMIN)
# =============================================================================

@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'User {user.username} created successfully')
                return redirect('manage_users')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'create_user.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})
@login_required
@user_passes_test(is_admin)
def edit_user(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user_obj)  # CHANGED HERE
        if form.is_valid():
            user = form.save()  # REMOVED the manual role handling since it's in the form
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('manage_users')
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form =AdminUserUpdateForm(instance=user_obj)  # CHANGED HERE
    
    return render(request, 'edit_user.html', {
        'form': form, 
        'user_obj': user_obj
        # REMOVED role_choices since it's now in the form
    })

@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('manage_users')
    
    return render(request, 'delete_user.html', {'user': user})
@login_required
@user_passes_test(is_admin)
def clear_all_data(request):
    if request.method == 'POST':
        # Confirm deletion
        if request.POST.get('confirm') == 'yes':
            # Delete all data
            User.objects.all().delete()
            CostSharingAgreement.objects.all().delete()
            Payment.objects.all().delete()
            Notice.objects.all().delete()
            Feedback.objects.all().delete()
            StudentData.objects.all().delete()
            BankAccount.objects.all().delete()
            
            messages.success(request, 'All data has been cleared successfully.')
            return redirect('dashboard')
    return render(request, 'clear_all_data.html')


# =============================================================================
# COST SHARING AGREEMENTS
# =============================================================================

@login_required
@user_passes_test(is_student)
def fill_cost_sharing(request):
    current_year = timezone.now().year
    
    print(f"=== DEBUG: User: {request.user}, Year: {current_year} ===")
    print(f"=== DEBUG: User Department: {getattr(request.user, 'department', 'None')} ===")
    print(f"=== DEBUG: User Year of Study: {getattr(request.user, 'year_of_study', 'None')} ===")
    
    # Check if student has required information from registrar
    student_department = getattr(request.user, 'department', None)
    student_year_of_study = getattr(request.user, 'year_of_study', None)
    
    if not student_department or not student_year_of_study:
        messages.error(request, 
            'Your academic information (department and year of study) is not complete. '
            'Please contact the registrar office to update your information before filling the cost sharing agreement.'
        )
        return redirect('dashboard')
    
    # Validate year of study
    if not (1 <= student_year_of_study <= 6):
        messages.error(request, 
            f'Invalid year of study ({student_year_of_study}). Year of study must be between 1 and 6. '
            'Please contact the registrar office to correct your information.'
        )
        return redirect('dashboard')
    
    # ✅ CHANGED: Check for existing agreements in CURRENT YEAR OF STUDY (not academic year)
    existing_agreements = CostSharingAgreement.objects.filter(
        student=request.user,
        year=student_year_of_study  # Changed from academic_year to year
    )
    
    print(f"=== DEBUG: Found {existing_agreements.count()} existing agreements for Year {student_year_of_study} ===")
    for agreement in existing_agreements:
        print(f"  - Agreement {agreement.id}: Status={agreement.status}, Year={agreement.year}")
    
    # Find rejected agreement for resubmission
    rejected_agreement = existing_agreements.filter(status='rejected').first()
    
    # Check for non-rejected agreements (pending or approved)
    non_rejected_agreement = existing_agreements.exclude(status='rejected').first()
    
    print(f"=== DEBUG: Rejected agreement: {rejected_agreement} ===")
    print(f"=== DEBUG: Non-rejected agreement: {non_rejected_agreement} ===")
    
    # ✅ CHANGED: Block if there's a pending or approved agreement for THIS YEAR OF STUDY
    if non_rejected_agreement:
        messages.error(request, 
            f'You already have a {non_rejected_agreement.status} cost sharing agreement for Year {student_year_of_study}. '
            f'You can only submit one agreement per year of study.'
        )
        return redirect('dashboard')
    
    # If there's a rejected agreement, allow resubmission
    if rejected_agreement:
        messages.info(request, 
            f'Your previous agreement for Year {student_year_of_study} was rejected. You can update and resubmit it.'
        )
    
    # Check if there are any cost structures available for student's department and year
    cost_structures_exist = CostStructure.objects.filter(
        department=student_department,
        year=student_year_of_study
    ).exists()
    
    print(f"=== DEBUG: Cost structures exist for {student_department} year {student_year_of_study}: {cost_structures_exist} ===")
    
    if request.method == 'POST':
        print("=== DEBUG: POST REQUEST RECEIVED ===")
        print("POST data keys:", list(request.POST.keys()))
        print("FILES data:", dict(request.FILES))
        
        # Debug: Print phone numbers and dates for validation
        print(f"=== DEBUG: Phone number: {request.POST.get('phone_number', 'Not provided')} ===")
        print(f"=== DEBUG: Mother phone: {request.POST.get('mother_phone', 'Not provided')} ===")
        print(f"=== DEBUG: Date of birth: {request.POST.get('date_of_birth', 'Not provided')} ===")
        print(f"=== DEBUG: Year of entrance: {request.POST.get('year_of_entrance', 'Not provided')} ===")
        
        # If editing a rejected agreement, pass the instance
        if rejected_agreement:
            print("=== DEBUG: Processing RESUBMISSION ===")
            form = CostSharingForm(request.POST, request.FILES, instance=rejected_agreement, user=request.user)
        else:
            print("=== DEBUG: Processing NEW SUBMISSION ===")
            form = CostSharingForm(request.POST, request.FILES, user=request.user)
            
        if form.is_valid():
            print("=== DEBUG: FORM IS VALID ===")
            try:
                agreement = form.save(commit=False)
                
                # Only set student for NEW submissions
                if not rejected_agreement:
                    agreement.student = request.user
                    print("=== DEBUG: Set student for new agreement ===")
                else:
                    print("=== DEBUG: Using existing student for resubmission ===")
                
                agreement.status = 'pending'  # Reset status to pending
                agreement.academic_year = current_year  # Current calendar year for reporting
                agreement.year = student_year_of_study  # Student's year of study for restrictions
                
                print(f"=== DEBUG: Saving agreement - Student: {agreement.student}, Department: {agreement.department}, Year of Study: {agreement.year} ===")
                print(f"=== DEBUG: Academic Year: {agreement.academic_year}, Status: {agreement.status} ===")
                
                agreement.save()
                print("=== DEBUG: Agreement saved successfully! ===")
                print(f"=== DEBUG: Agreement ID: {agreement.id} ===")
                
                # Create notification for cost sharing officers
                officers = User.objects.filter(role='cost_sharing_officer')
                for officer in officers:
                    create_notification(
                        recipient=officer,
                        title="Cost Sharing Agreement Resubmitted" if rejected_agreement else "New Cost Sharing Agreement Pending",
                        message=f"Student {request.user.get_full_name()} has {'resubmitted' if rejected_agreement else 'submitted'} a cost sharing agreement for Year {student_year_of_study}.",
                        notification_type='agreement',
                        related_object_id=agreement.id,
                        related_object_type='agreement'
                    )
                
                # Also notify the student
                create_notification(
                    recipient=request.user,
                    title="Cost Sharing Agreement Submitted",
                    message=f"Your cost sharing agreement for Year {student_year_of_study} has been submitted successfully and is pending review.",
                    notification_type='agreement',
                    related_object_id=agreement.id,
                    related_object_type='agreement'
                )
                
                action = "resubmitted" if rejected_agreement else "submitted"
                messages.success(request, 
                    f'Cost sharing agreement {action} successfully for Year {student_year_of_study}. '
                    'It will be reviewed by the Cost Sharing Officer.'
                )
                print("=== DEBUG: Redirecting to dashboard ===")
                return redirect('dashboard')
                
            except Exception as e:
                print(f"=== DEBUG: Error saving agreement: {str(e)} ===")
                import traceback
                print(f"=== DEBUG: Traceback: {traceback.format_exc()} ===")
                messages.error(request, f'Error saving agreement: {str(e)}')
        else:
            print("=== DEBUG: FORM INVALID ===")
            print("Form errors:", form.errors.as_json())
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"  - {field}: {error}")
                    messages.error(request, f'{field}: {error}')
            
            # Show specific guidance for common errors
            if 'phone_number' in form.errors:
                messages.info(request, '📱 Phone number must be exactly 10 digits starting with 09 (e.g., 0912345678)')
            if 'mother_phone' in form.errors:
                messages.info(request, '📱 Mother\'s phone number must be exactly 10 digits starting with 09 (e.g., 0912345678)')
            if 'date_of_birth' in form.errors:
                messages.info(request, '🎂 Date of birth must be at least 10 years before current date')
            if 'year_of_entrance' in form.errors:
                current_year = timezone.now().year
                messages.info(request, f'📅 Year of entrance must be before {current_year}')
    else:
        # If editing a rejected agreement, prefill the form
        if rejected_agreement:
            print("=== DEBUG: Loading form with rejected agreement data ===")
            form = CostSharingForm(instance=rejected_agreement, user=request.user)
        else:
            form = CostSharingForm(user=request.user)
        
        # Debug initial form data
        print(f"=== DEBUG: Form initial data: {form.initial} ===")
    
    context = {
        'form': form,
        'cost_structures_exist': cost_structures_exist,
        'current_year': current_year,
        'is_resubmission': rejected_agreement is not None,
        'rejected_agreement': rejected_agreement,
        'student_department': student_department,
        'student_year_of_study': student_year_of_study
    }
    print(f"=== DEBUG: Context - is_resubmission: {context['is_resubmission']} ===")
    print(f"=== DEBUG: Context - student_department: {context['student_department']} ===")
    print(f"=== DEBUG: Context - student_year_of_study: {context['student_year_of_study']} ===")
    return render(request, 'fill_cost_sharing.html', context)

@login_required
@user_passes_test(is_student)
def view_cost_sharing(request):
    agreements = CostSharingAgreement.objects.filter(student=request.user)
    return render(request, 'view_cost_sharing.html', {'agreements': agreements})

@login_required
@user_passes_test(is_student)
def print_cost_sharing(request, pk):
    agreement = get_object_or_404(CostSharingAgreement, pk=pk, student=request.user)
    return render(request, 'print_cost_sharing.html', {'agreement': agreement})

@login_required
@user_passes_test(is_cost_sharing_officer)
def agreement_set_status(request, pk, status):
    """
    Allow cost sharing officer to accept or reject a CostSharingAgreement.
    Usage: /agreement/<pk>/set/<status>/ where status is 'accept'/'accepted' or 'reject'/'rejected'
    """
    ag = get_object_or_404(CostSharingAgreement, pk=pk)

    s = (status or '').lower()
    if s in ('accept', 'accepted'):
        ag.status = 'accepted'
        ag.save()
        create_notification(
            recipient=ag.student,
            title='Agreement accepted',
            message=f'Your cost sharing agreement (ID: {ag.id}) has been accepted.',
            notification_type='agreement',
            related_object_id=ag.id,
            related_object_type='CostSharingAgreement'
        )
        messages.success(request, 'Agreement accepted.')
    elif s in ('reject', 'rejected'):
        ag.status = 'rejected'
        ag.date_accepted = timezone.now()  # Set current date/time
        ag.save()
        create_notification(
            recipient=ag.student,
            title='Agreement rejected',
            message=f'Your cost sharing agreement (ID: {ag.id}) has been rejected.',
            notification_type='agreement',
            related_object_id=ag.id,
            related_object_type='CostSharingAgreement'
        )
        messages.success(request, 'Agreement rejected.')
    else:
        messages.error(request, 'Invalid status specified.')

    return redirect('dashboard')

def view_agreement(request, agreement_id):
    agreement = get_object_or_404(CostSharingAgreement, id=agreement_id)
    return render(request, 'view_agreement.html', {'agreement': agreement})

# =============================================================================
# COST STRUCTURE MANAGEMENT
# =============================================================================

@require_http_methods(["GET", "POST"])
@csrf_exempt
def cost_structure_api(request):
    """API endpoint to handle cost structure operations"""
    if request.method == 'GET':
        return get_cost_structure(request)
    elif request.method == 'POST':
        return create_or_update_cost_structure(request)

def get_cost_structure(request):
    """GET: Retrieve cost structure for specific department and year"""
    department = request.GET.get('department')
    year = request.GET.get('year')
    
    if not department or not year:
        return JsonResponse({'error': 'Department and year are required'}, status=400)
    
    try:
        cost_structure = CostStructure.objects.get(
            department=department,
            year=int(year)
        )
        
        return JsonResponse({
            'department': cost_structure.department,
            'year': cost_structure.year,
            'education_cost': float(cost_structure.education_cost),
            'food_cost': float(cost_structure.food_cost),
            'dormitory_cost': float(cost_structure.dormitory_cost),
            'total_cost': float(cost_structure.total_cost),  # This will be auto-calculated
        })
    except CostStructure.DoesNotExist:
        return JsonResponse({
            'education_cost': 0,
            'food_cost': 0,
            'dormitory_cost': 0,
            'total_cost': 0,
            'message': 'No cost structure found for this department and year'
        })

def create_or_update_cost_structure(request):
    """POST: Create or update cost structure"""
    try:
        data = json.loads(request.body)
        
        # Required fields validation
        required_fields = ['department', 'year', 'education_cost', 'food_cost', 'dormitory_cost']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Get or create cost structure
        cost_structure, created = CostStructure.objects.get_or_create(
            department=data['department'],
            year=int(data['year']),
            defaults={
                'education_cost': data['education_cost'],
                'food_cost': data['food_cost'],
                'dormitory_cost': data['dormitory_cost'],
                # total_cost will be automatically calculated in save() method
            }
        )
        
        if not created:
            # Update existing record
            cost_structure.education_cost = data['education_cost']
            cost_structure.food_cost = data['food_cost']
            cost_structure.dormitory_cost = data['dormitory_cost']
            cost_structure.save()  # This will auto-recalculate total_cost
        
        return JsonResponse({
            'message': 'Cost structure created successfully' if created else 'Cost structure updated successfully',
            'department': cost_structure.department,
            'year': cost_structure.year,
            'education_cost': float(cost_structure.education_cost),
            'food_cost': float(cost_structure.food_cost),
            'dormitory_cost': float(cost_structure.dormitory_cost),
            'total_cost': float(cost_structure.total_cost),  # Automatically calculated
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_available_departments(request):
    """Get available departments for cost structure"""
    departments = CostStructure.objects.values_list('department', flat=True).distinct()
    return JsonResponse({'departments': list(departments)})

def manage_cost_structure(request):
    """View to manage cost structures"""
    cost_structures = CostStructure.objects.all().order_by('department', 'year')
    
    if request.method == 'POST':
        form = CostStructureForm(request.POST)
        if form.is_valid():
            # The save() method in your model will auto-calculate total_cost
            form.save()
            messages.success(request, 'Cost structure saved successfully!')
            return redirect('manage_cost_structure')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CostStructureForm()
    
    return render(request, 'manage_cost_structure.html', {
        'form': form,
        'cost_structures': cost_structures
    })

@login_required
@user_passes_test(is_cost_sharing_officer)
def update_cost_structure(request, pk):
    cost_structure = get_object_or_404(CostStructure, pk=pk)
    
    if request.method == 'POST':
        form = CostStructureForm(request.POST, instance=cost_structure)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cost structure updated successfully')
            return redirect('manage_cost_structure')
    else:
        form = CostStructureForm(instance=cost_structure)
    
    return render(request, 'update_cost_structure.html', {'form': form})

def delete_cost_structure(request, pk):
    """Delete a cost structure"""
    cost_structure = get_object_or_404(CostStructure, pk=pk)
    if request.method == 'POST':
        department = cost_structure.department
        cost_structure.delete()
        messages.success(request, f'Cost structure for {department} deleted successfully!')
        return redirect('manage_cost_structure')
    
    # If not POST, show confirmation page
    return render(request, 'confirm_delete.html', {
        'object': cost_structure,
        'object_type': 'Cost Structure'
    })

@require_http_methods(["GET"])
@csrf_exempt
def get_cost_data(request):
    """API endpoint to get cost structure data"""
    department = request.GET.get('department')
    year = request.GET.get('year')
    
    if not department or not year:
        return JsonResponse({'error': 'Department and year are required'}, status=400)
    
    try:
        # Convert year to integer and get cost structure
        year_int = int(year)
        cost_structure = CostStructure.objects.filter(
            department=department,
            year=year_int
        ).first()
        
        if cost_structure:
            return JsonResponse({
                'education_cost': float(cost_structure.education_cost),
                'food_cost': float(cost_structure.food_cost),
                'dormitory_cost': float(cost_structure.dormitory_cost),
                'total_cost': float(cost_structure.total_cost),
                'department': cost_structure.department,
                'year': cost_structure.year
            })
        else:
            return JsonResponse({
                'error': 'No cost structure found for this department and year',
                'education_cost': 0,
                'food_cost': 0,
                'dormitory_cost': 0,
                'total_cost': 0
            })
            
    except ValueError:
        return JsonResponse({'error': 'Invalid year format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# =============================================================================
# PAYMENT MANAGEMENT
# =============================================================================
from decimal import Decimal
from django.db import transaction
@login_required
@user_passes_test(is_student)
def make_payment(request):
    """
    Virtual payment: only if the student's latest accepted cost sharing agreement
    has is_graduate=True. Uses StudentData.virtual_balance as the available balance.
    """
    print("🔍 DEBUG: Starting make_payment view")
    print(f"🔍 User: {request.user.username}, Role: {request.user.role}")
    
    # Get active agreement
    active_agreement = CostSharingAgreement.objects.filter(
        student=request.user,
        status__iexact='accepted'
    ).order_by('-date_filled', '-id').first()

    print(f"🔍 Active agreement found: {active_agreement}")
    
    if not active_agreement:
        messages.error(request, 'No accepted cost sharing agreement found.')
        return redirect('dashboard')
    
    if not getattr(active_agreement, 'is_graduate', False):
        messages.error(request, 'Payments allowed only if your accepted cost sharing agreement has "is_graduate" checked.')
        return redirect('dashboard')

    # Get student data
    student_data = getattr(request.user, 'studentdata', None)
    if not student_data:
        messages.error(request, 'Student profile not found. Contact registrar.')
        return redirect('dashboard')

    if not _model_has_field(StudentData, 'virtual_balance'):
        messages.error(request, 'Virtual balance field missing in database.')
        return redirect('dashboard')

    virtual_balance = Decimal(getattr(student_data, 'virtual_balance') or 0)
    print(f"🔍 Virtual balance: {virtual_balance}")

    # Calculate payment summary for active agreement
    total_paid = Payment.objects.filter(
        agreement=active_agreement,
        status__in=['partial', 'verified', 'completed']
    ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
    
    remaining_balance = Decimal(active_agreement.total_cost) - Decimal(total_paid)
    print(f"🔍 Agreement {active_agreement.id}: Total cost={active_agreement.total_cost}, Paid={total_paid}, Remaining={remaining_balance}")

    # Calculate ALL agreements summary
    all_agreements = CostSharingAgreement.objects.filter(student=request.user)
    
    total_cost_all = Decimal('0')
    total_paid_all = Decimal('0')
    
    for agreement in all_agreements:
        # Add agreement total
        if hasattr(agreement, 'total_cost') and agreement.total_cost:
            total_cost_all += Decimal(str(agreement.total_cost))
        
        # Add payments for this agreement
        agreement_payments = Payment.objects.filter(agreement=agreement)
        for payment in agreement_payments:
            if payment.status in ['partial', 'verified', 'completed']:
                total_paid_all += Decimal(str(payment.amount_paid or 0))
    
    remaining_all = total_cost_all - total_paid_all
    
    # Get counts
    all_agreements_count = all_agreements.count()
    total_payments_count = Payment.objects.filter(agreement__student=request.user).count()

    print(f"🔍 POST request: {request.method == 'POST'}")
    
    if request.method == 'POST':
        print(f"🔍 POST data: {dict(request.POST)}")
        
        # Get amount from form
        amount_raw = request.POST.get('amount_paid')
        agreement_id = request.POST.get('agreement')
        description = request.POST.get('description', '')
        
        print(f"🔍 Amount from form: {amount_raw}")
        print(f"🔍 Agreement ID from form: {agreement_id}")
        
        try:
            amount = Decimal(amount_raw or 0)
        except Exception as e:
            print(f"❌ Error converting amount: {e}")
            messages.error(request, f'Invalid payment amount: {amount_raw}')
            return redirect('make_payment')

        # Validation
        if amount < 500:
            messages.error(request, f'Minimum payment amount is ETB 500.00. You entered ETB {amount}.')
            return redirect('make_payment')
        
        if amount > virtual_balance:
            messages.error(request, f'Insufficient virtual balance. Available: ETB {virtual_balance}, Requested: ETB {amount}')
            return redirect('make_payment')
        
        if amount > remaining_balance:
            messages.error(request, f'Payment exceeds remaining agreement balance (ETB {remaining_balance}).')
            return redirect('make_payment')

        print(f"🔍 Validation passed. Processing payment of ETB {amount}")

        try:
            with transaction.atomic():
                print("🔍 Starting transaction...")
                
                # ✅ FIXED: Create Payment record with payer field
                payment = Payment.objects.create(
                    agreement=active_agreement,
                    payer=request.user,  # ✅ THIS IS CRITICAL - your model requires payer
                    amount_paid=amount,
                    status='completed',
                    payment_method='virtual',  # Add this field
                    date_paid=timezone.now(),
                )
                
                print(f"✅ Payment saved with ID: {payment.id}")

                # Deduct virtual balance
                print(f"🔍 Deducting from virtual balance: {virtual_balance} - {amount}")
                student_data.virtual_balance = virtual_balance - amount
                student_data.save()
                print(f"✅ Virtual balance updated: {student_data.virtual_balance}")

                # Create notification
                create_notification(
                    recipient=request.user,
                    title="Payment Successful",
                    message=f"Virtual payment of ETB {amount} has been recorded successfully.",
                    notification_type='payment',
                    related_object_id=payment.id,
                    related_object_type='payment'
                )
                print("✅ Notification created")
                
                messages.success(request, f'Payment of ETB {amount} recorded successfully!')
                print("✅ Success message set")
                
                return redirect('payment_history')
                
        except Exception as exc:
            print(f"❌ Error processing payment: {str(exc)}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            messages.error(request, f'Failed to process payment: {str(exc)}')
            return redirect('make_payment')

    # GET request - prepare context
    print("🔍 Preparing GET request context")
    
    context = {
        'active_agreement': active_agreement,
        'active_agreements': CostSharingAgreement.objects.filter(
            student=request.user,
            status__iexact='accepted'
        ).order_by('-date_filled'),
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
        'virtual_balance': virtual_balance,
        'virtual_mode': True,
        'payment_progress': {
            'percentage': (total_paid / active_agreement.total_cost * 100) if active_agreement.total_cost > 0 else 0,
            'paid': total_paid,
            'total': active_agreement.total_cost,
            'remaining': remaining_balance
        },
        'total_summary': {
            'all_cost': total_cost_all,
            'all_paid': total_paid_all,
            'all_remaining': remaining_all,
        },
        'all_agreements_count': all_agreements_count,
        'total_payments_count': total_payments_count,
    }
    
    print(f"🔍 Context prepared. Rendering template...")
    return render(request, 'make_payment.html', context)
@login_required
@user_passes_test(is_inland_revenue_officer)
def manage_payments(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment recorded successfully')
            return redirect('manage_payments')
    else:
        form = PaymentForm(user=request.user)
    
    payments = Payment.objects.all()
    
    return render(request, 'manage_payments.html', {
        'form': form,
        'payments': payments,
    })

@login_required
@user_passes_test(is_inland_revenue_officer)
def update_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully')
            return redirect('manage_payments')
    else:
        form = PaymentForm(instance=payment, user=request.user)
    
    return render(request, 'update_payment.html', {'form': form})

# ...existing code...
from django.db import transaction
from decimal import Decimal
# ...existing code...
@login_required
@user_passes_test(lambda u: getattr(u, 'role', '') in ('inland_revenue_officer','admin'))
def verify_payment(request, pk):
    """
    Verify/validate a payment. Automatically refund cancelled payments.
    """
    payment = get_object_or_404(Payment, pk=pk)

    if request.method == 'POST':
        form = PaymentVerificationForm(request.POST, instance=payment)
        if form.is_valid():
            prev_status = payment.status.lower() if getattr(payment, 'status', None) else ''
            payment = form.save(commit=False)
            new_status = (payment.status or '').lower()

            try:
                with transaction.atomic():
                    # Save payment verification info
                    payment.verified_by = request.user if hasattr(payment, 'verified_by') else None
                    payment.verified_at = timezone.now() if hasattr(payment, 'verified_at') else None
                    payment.save()

                    # ✅ CRITICAL: Automatically refund if payment is cancelled/failed/rejected
                    if new_status in ('failed', 'rejected', 'cancelled'):
                        amount = Decimal(getattr(payment, 'amount_paid', 0) or 0)
                        if amount > 0:
                            # Get the student
                            student = None
                            if hasattr(payment, 'agreement') and payment.agreement:
                                student = payment.agreement.student
                            elif hasattr(payment, 'payer'):
                                student = payment.payer
                            elif hasattr(payment, 'student'):
                                student = payment.student
                            elif hasattr(payment, 'user'):
                                student = payment.user
                            
                            if student:
                                # Find the student's StudentData record
                                student_data = None
                                try:
                                    # Try direct relationship first
                                    student_data = getattr(student, 'studentdata', None)
                                    if not student_data:
                                        # Try to find by student_id
                                        student_data = StudentData.objects.filter(
                                            student_id=getattr(student, 'student_id', None)
                                        ).first()
                                    
                                    if student_data and hasattr(student_data, 'virtual_balance'):
                                        # Get current balance
                                        current_balance = Decimal(getattr(student_data, 'virtual_balance') or 0)
                                        
                                        # Add refund amount back to balance
                                        new_balance = current_balance + amount
                                        student_data.virtual_balance = new_balance
                                        student_data.save()
                                        
                                        print(f"✅ REFUND PROCESSED: Student {student.username}")
                                        print(f"   - Amount refunded: ETB {amount}")
                                        print(f"   - Old balance: ETB {current_balance}")
                                        print(f"   - New balance: ETB {new_balance}")
                                        
                                        # Create notification for student
                                        create_notification(
                                            recipient=student,
                                            title="Payment Refunded",
                                            message=f"ETB {amount} has been refunded to your virtual balance due to payment cancellation/rejection.",
                                            notification_type='payment',
                                            related_object_id=payment.id,
                                            related_object_type='payment'
                                        )
                                        
                                        # Send email notification
                                        try:
                                            send_mail(
                                                subject=f'Payment Refund - ETB {amount}',
                                                message=f'Dear {student.get_full_name() or student.username},\n\n'
                                                        f'ETB {amount} has been refunded to your virtual balance.\n'
                                                        f'Reason: Payment was {new_status}.\n'
                                                        f'New Virtual Balance: ETB {new_balance}\n\n'
                                                        f'Thank you,\nOCSMS Team',
                                                from_email=settings.DEFAULT_FROM_EMAIL,
                                                recipient_list=[student.email],
                                                fail_silently=True,
                                            )
                                        except Exception as email_error:
                                            print(f"❌ Email notification failed: {email_error}")
                                    else:
                                        print(f"❌ Cannot find student_data or virtual_balance field for student {student.username}")
                                except Exception as refund_error:
                                    print(f"❌ Refund processing error: {refund_error}")
                                    messages.error(request, f'Payment status updated but refund failed: {refund_error}')
                            else:
                                print(f"❌ Cannot identify student for payment {payment.id}")
                    else:
                        print(f"✅ Payment {payment.id} status changed to {new_status}, no refund needed")

            except Exception as exc:
                print(f"❌ Error while verifying payment: {exc}")
                messages.error(request, f'Failed to update payment: {exc}')
                return redirect('manage_payments')

            messages.success(request, f'Payment status updated to {new_status}. '
                           f'Refund processed automatically where applicable.')
            return redirect('manage_payments')
    else:
        form = PaymentVerificationForm(instance=payment)

    return render(request, 'verify_payment.html', {'form': form, 'payment': payment})
from decimal import Decimal
def payment_history(request):
    """Show payment history for the logged-in student - CORRECTED VERSION"""
    
    # Get ALL payments for this student from ALL agreements
    payments = Payment.objects.filter(agreement__student=request.user).order_by('-date_paid')
    
    # Get ALL agreements for this student
    all_agreements = CostSharingAgreement.objects.filter(student=request.user)
    
    # DEBUG: Show all agreements
    print(f"🔍 DEBUG for student {request.user.username}:")
    print(f"   - Total agreements found: {all_agreements.count()}")
    
    # Calculate total cost from ALL agreements
    total_cost = Decimal('0')
    for agreement in all_agreements:
        if hasattr(agreement, 'total_cost') and agreement.total_cost:
            total_cost += Decimal(str(agreement.total_cost))
            print(f"   - Agreement {agreement.id}: total_cost = {agreement.total_cost}")
        elif hasattr(agreement, 'total') and agreement.total:
            total_cost += Decimal(str(agreement.total))
            print(f"   - Agreement {agreement.id}: total = {agreement.total}")
    
    print(f"   - SUM of all agreements: {total_cost}")
    
    # Calculate total paid from ALL agreements
    total_paid = Decimal('0')
    if payments.exists():
        # Method 1: Sum completed payments
        completed_payments = payments.filter(status='completed')
        completed_total = completed_payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        
        # Method 2: Sum verified payments
        verified_payments = payments.filter(status='verified')
        verified_total = verified_payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        
        # Method 3: Sum partial payments
        partial_payments = payments.filter(status='partial')
        partial_total = partial_payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        
        # Total = completed + verified + partial
        total_paid = completed_total + verified_total + partial_total
        
        print(f"   - Completed payments: {completed_total}")
        print(f"   - Verified payments: {verified_total}")
        print(f"   - Partial payments: {partial_total}")
        print(f"   - TOTAL PAID: {total_paid}")
    else:
        print("   - No payments found")
    
    # Calculate remaining balance
    remaining_balance = total_cost - total_paid
    
    # Create agreement summaries for template
    agreement_summaries = []
    for agreement in all_agreements:
        # Get agreement total
        ag_total = Decimal('0')
        if hasattr(agreement, 'total_cost') and agreement.total_cost:
            ag_total = Decimal(str(agreement.total_cost))
        elif hasattr(agreement, 'total') and agreement.total:
            ag_total = Decimal(str(agreement.total))
        
        # Get payments for this specific agreement
        ag_payments = payments.filter(agreement=agreement)
        ag_paid = Decimal('0')
        if ag_payments.exists():
            ag_paid = ag_payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0')
        
        ag_remaining = ag_total - ag_paid
        
        agreement_summaries.append({
            'agreement': agreement,
            'total': ag_total,
            'paid': ag_paid,
            'remaining': ag_remaining,
            'payment_progress_pct': (float(ag_paid) / float(ag_total) * 100) if ag_total > 0 else 0,
        })
    
    context = {
        'payments': payments,
        'total_cost': total_cost,
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
        'agreement_summaries': agreement_summaries,
        'all_agreements': all_agreements,  # For template to show count
    }
    
    return render(request, 'payment_history.html', context)

@login_required
@user_passes_test(is_student)
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk, agreement__student=request.user)
    
    # Generate PDF receipt
    response = generate_payment_receipt(payment)
    return response

def generate_payment_receipt(payment):
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Get the styles
    styles = getSampleStyleSheet()
    
    # Create a title style
    title_style = ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    # Create a normal style
    normal_style = styles['Normal']
    
    # Build the document
    elements = []
    
    # Add title
    elements.append(Paragraph("PAYMENT RECEIPT", title_style))
    
    # Add spacer
    elements.append(Spacer(1, 20))
    
    # Create data for the table
    data = [
        ['Transaction Code:', payment.transaction_code],
        ['Date:', payment.date_paid.strftime('%Y-%m-%d')],
        ['Student:', payment.agreement.student.get_full_name()],
        ['Student ID:', payment.agreement.student.student_id],
        ['Amount Paid:', f"ETB {payment.amount_paid}"],
        ['Payment Method:', payment.get_payment_method_display()],
        ['Status:', payment.get_status_display()],
    ]
    
    # Create the table
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
     ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 0), (0, -1), colors.grey),
    ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
]))
    
    elements.append(table)
    
    # Add spacer
    elements.append(Spacer(1, 20))
    
    # Add verification details if verified
    if payment.verified_by:
        elements.append(Paragraph("Verified by:", normal_style))
        elements.append(Paragraph(payment.verified_by.get_full_name(), normal_style))
        elements.append(Paragraph(f"Verified at: {payment.verified_at.strftime('%Y-%m-%d %H:%M')}", normal_style))
    
    # Add notes if any
    if payment.notes:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Notes:", normal_style))
        elements.append(Paragraph(payment.notes, normal_style))
    
    # Add footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Mekdela Amba University - Cost Sharing Management System", normal_style))
    
    # Build the document
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    
    # Create a response with the PDF data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_code}.pdf"'
    response.write(pdf)
    
    return response

@login_required
@user_passes_test(is_inland_revenue_officer)
def view_payment_status(request):
    """Show ONLY GRADUATE students with their TOTAL payment status"""
    # Get only graduate students from StudentData
    graduate_students = StudentData.objects.filter(is_graduate=True).order_by('student_id')
    
    # Calculate totals for each graduate student
    student_totals = []
    
    total_cost_all = 0
    total_paid_all = 0
    total_remaining_all = 0
    
    for student_data in graduate_students:
        # Find all agreements for this student
        agreements = CostSharingAgreement.objects.filter(
            Q(student__student_id=student_data.student_id) | 
            Q(full_name=student_data.full_name)
        )
        
        # Calculate totals across ALL agreements for this student
        total_cost_all_student = 0
        total_paid_all_student = 0
        
        for agreement in agreements:
            # Add agreement cost
            if hasattr(agreement, 'total_cost') and agreement.total_cost:
                total_cost_all_student += float(agreement.total_cost)
            
            # Add payments for this agreement
            payments = Payment.objects.filter(agreement=agreement)
            agreement_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
            total_paid_all_student += float(agreement_paid)
        
        # Calculate remaining balance
        remaining_balance_all_student = total_cost_all_student - total_paid_all_student
        
        # Add to overall totals
        total_cost_all += total_cost_all_student
        total_paid_all += total_paid_all_student
        total_remaining_all += remaining_balance_all_student
        
        # Determine payment status
        if total_cost_all_student > 0:
            if remaining_balance_all_student <= 0:
                payment_status = 'Paid'
                status_class = 'bg-success'
            elif total_paid_all_student > 0:
                payment_status = 'Partial'
                status_class = 'bg-warning'
            else:
                payment_status = 'Unpaid'
                status_class = 'bg-danger'
        else:
            payment_status = 'No Agreement'
            status_class = 'bg-secondary'
        
        student_totals.append({
            'student_id': student_data.student_id,
            'full_name': student_data.full_name,
            'department': student_data.department,
            'total_cost_all': total_cost_all_student,
            'total_paid_all': total_paid_all_student,
            'remaining_balance_all': remaining_balance_all_student,
            'payment_status': payment_status,
            'status_class': status_class,
            'agreement_count': agreements.count(),
            'has_agreement': agreements.exists(),
            'is_graduate': student_data.is_graduate,
        })
    
    # Get dashboard statistics
    total_payments = Payment.objects.count()
    total_collected = Payment.objects.aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    total_agreements = CostSharingAgreement.objects.count()
    total_bank_accounts = BankAccount.objects.count()
    
    context = {
        'student_totals': student_totals,
        'total_payments': total_payments,
        'total_collected': total_collected,
        'total_agreements': total_agreements,
        'total_bank_accounts': total_bank_accounts,
        'total_students': len(student_totals),
        'total_cost_all': total_cost_all,
        'total_paid_all': total_paid_all,
        'total_remaining_all': total_remaining_all,
        'show_only_graduates': True,  # Flag for template
    }
    
    return render(request, 'view_payment_status.html', context)
@login_required
@user_passes_test(lambda u: u.role in ['admin', 'cost_sharing_officer', 'inland_revenue_officer'])
def bank_account_transactions(request, account_id):
    """
    Show full transactions for a bank account.
    Visible to admin, cost_sharing_officer and inland_revenue_officer.
    """
    account = get_object_or_404(BankAccount, id=account_id)

    # Try to import BankTransaction model if present
    try:
        from .models import BankTransaction
    except Exception:
        BankTransaction = None

    if BankTransaction:
        transactions_qs = BankTransaction.objects.filter(bank_account=account).order_by('-timestamp')
    else:
        # Fallback: try common related names on BankAccount
        rel = getattr(account, 'banktransaction_set', None) or getattr(account, 'transactions', None)
        if rel is not None:
            try:
                transactions_qs = rel.all().order_by('-id')
            except Exception:
                transactions_qs = []
        else:
            transactions_qs = []

    paginator = Paginator(transactions_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'cost_sharing/bank_account_transactions.html', {
        'account': account,
        'transactions': page_obj,
    })

import csv
@login_required
@user_passes_test(is_cost_sharing_officer)
def cost_officer_assigned_list(request):
    """
    List StudentData items assigned to the logged-in cost-sharing officer.
    Paginated.
    """
    qs = StudentData.objects.filter(assigned_to=request.user).order_by('-created_at')
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'cost_officer_assigned_list.html', {'student_data_list': page_obj})

@login_required
@user_passes_test(is_cost_sharing_officer)
def cost_officer_forward_graduates(request, pk):
    """
    Cost-sharing officer forwards a graduate StudentData record to an inland revenue officer.
    GET: show confirmation page.
    POST: assign to first available inland officer, update status if present, notify recipient.
    """
    sd = get_object_or_404(StudentData, pk=pk)

    # ensure this item is assigned to this cost officer (if assigned_to exists)
    assigned_to = getattr(sd, 'assigned_to', None)
    if assigned_to and assigned_to != request.user:
        messages.error(request, "You don't have permission to forward this record.")
        return redirect('cost_officer_assigned_list')

    # only forward graduate records
    if not getattr(sd, 'is_graduate', False):
        messages.error(request, "Only graduate student data can be forwarded to Inland Revenue.")
        return redirect('cost_officer_assigned_list')

    if request.method == 'POST':
        inland_officer = User.objects.filter(role='inland_revenue_officer').first()
        if not inland_officer:
            messages.error(request, "No Inland Revenue Officer available to receive this record.")
            return redirect('cost_officer_assigned_list')

        sd.assigned_to = inland_officer
        # set status if model supports it
        if hasattr(sd, 'status'):
            try:
                sd.status = StudentData.STATUS_ASSIGNED_TO_INLAND
            except Exception:
                sd.status = 'assigned_to_inland'
        sd.save()

        # notify inland officer
        create_notification(
            recipient=inland_officer,
            title="Student Data Forwarded",
            message=f"Student data (ID: {sd.id}) has been forwarded by {request.user.get_full_name() or request.user.username}.",
            notification_type='student_data',
            related_object_id=sd.id,
            related_object_type='StudentData'
        )

        messages.success(request, f"Record forwarded to {inland_officer.get_full_name() or inland_officer.username}.")
        return redirect('cost_officer_assigned_list')

    return render(request, 'cost_forward_confirm.html', {'student_data': sd})
@login_required
@user_passes_test(is_cost_sharing_officer)
def cost_officer_dashboard(request):
    """
    Dedicated dashboard for cost sharing officers.
    Displays pending agreements, assigned students, and key statistics.
    """
    # Get pending agreements for review
    pending_agreements = CostSharingAgreement.objects.filter(
        status__iexact='pending'
    ).order_by('-date_filled' if _model_has_field(CostSharingAgreement, 'date_filled') else '-id')[:10]
    
    # Get accepted agreements
    accepted_agreements = CostSharingAgreement.objects.filter(
        status__iexact='accepted'
    ).order_by('-date_accepted' if _model_has_field(CostSharingAgreement, 'date_accepted') else '-id')[:10]
    
    # Get assigned student data
    assigned_students = StudentData.objects.filter(
        assigned_to=request.user
    ).order_by('-created_at')[:10]
    
    # Get cost structures
    cost_structures = CostStructure.objects.all()
    
    # Calculate statistics
    total_pending = CostSharingAgreement.objects.filter(status__iexact='pending').count()
    total_accepted = CostSharingAgreement.objects.filter(status__iexact='accepted').count()
    total_rejected = CostSharingAgreement.objects.filter(status__iexact='rejected').count()
    total_assigned_students = StudentData.objects.filter(assigned_to=request.user).count()
    
    # Get active notices for cost sharing officers
    role = 'cost_sharing_officer'
    active_notices = get_notices_for_role(role)
    
    # Get unread notifications
    unread_notifications = request.user.notifications.filter(is_read=False)[:5]
    
    context = {
        'pending_agreements': pending_agreements,
        'accepted_agreements': accepted_agreements,
        'assigned_students': assigned_students,
        'cost_structures': cost_structures,
        'total_pending': total_pending,
        'total_accepted': total_accepted,
        'total_rejected': total_rejected,
        'total_assigned_students': total_assigned_students,
        'active_notices': active_notices,
        'unread_notifications': unread_notifications,
    }
    
    return render(request, 'cost_officer_dashboard.html', context)


@login_required
@user_passes_test(is_inland_revenue_officer)
def inland_dashboard(request):
    """
    Inland revenue officer dashboard — show payments only for accepted agreements.
    """
    payments = Payment.objects.filter(agreement__status__iexact='accepted').select_related('agreement', getattr(Payment, 'payer', None))
    # optional: paginate
    paginator = Paginator(payments.order_by('-id'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cost_sharing/inland_dashboard.html', {
        'payments': page_obj,
    })

# =============================================================================
# BANK ACCOUNT MANAGEMENT
# =============================================================================

@login_required
@user_passes_test(is_admin)
def manage_bank_accounts(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank account added successfully')
            return redirect('manage_bank_accounts')
    else:
        form = BankAccountForm()
    
    bank_accounts = BankAccount.objects.all()
    
    return render(request, 'manage_bank_accounts.html', {
        'form': form,
        'bank_accounts': bank_accounts,
    })

@login_required
@user_passes_test(is_admin)
def edit_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    
    if request.method == 'POST':
        form = BankAccountForm(request.POST, instance=bank_account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bank account updated successfully')
            return redirect('manage_bank_accounts')
    else:
        form = BankAccountForm(instance=bank_account)
    return render(request, 'edit_bank_account.html', {'form': form, 'bank_account': bank_account})

@login_required
@user_passes_test(is_admin)
def delete_bank_account(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    
    if request.method == 'POST':
        bank_account.delete()
        messages.success(request, 'Bank account deleted successfully')
        return redirect('manage_bank_accounts')
    return render(request, 'delete_bank_account.html', {'bank_account': bank_account})

@login_required
@user_passes_test(is_inland_revenue_officer)
def view_bank_accounts(request):
    """View all bank accounts for inland revenue officers"""
    bank_accounts = BankAccount.objects.all()
    return render(request, 'view_bank_accounts.html', {'bank_accounts': bank_accounts})

# =============================================================================
# STUDENT DATA MANAGEMENT
# =============================================================================

@login_required
@user_passes_test(is_registrar_officer)
def upload_student_data(request):
    """Handle CSV student data upload - matching your actual model"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file.')
            return redirect('upload_student_data')
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            csv_reader = csv.DictReader(decoded_file)
            
            success_count = 0
            error_count = 0
            detailed_errors = []
            
            print("CSV Columns found:", csv_reader.fieldnames)
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Validate required fields
                    full_name = row.get('Full Name', '').strip()
                    student_id = row.get('Student ID', '').strip()
                    
                    if not full_name:
                        detailed_errors.append(f"Row {row_num}: Missing 'Full Name'")
                        error_count += 1
                        continue
                    
                    if not student_id:
                        detailed_errors.append(f"Row {row_num}: Missing 'Student ID'")
                        error_count += 1
                        continue
                    
                    # Check if student ID already exists
                    if StudentData.objects.filter(student_id=student_id).exists():
                        detailed_errors.append(f"Row {row_num}: Student ID '{student_id}' already exists")
                        error_count += 1
                        continue
                    
                    # Check if user already exists
                    if User.objects.filter(username=student_id).exists():
                        detailed_errors.append(f"Row {row_num}: Username '{student_id}' already exists")
                        error_count += 1
                        continue
                    
                    # Create user account
                    user = User.objects.create_user(
                        username=student_id,
                        email=f"{student_id}@university.edu",
                        first_name=full_name.split()[0] if full_name.split() else '',
                        last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else '',
                        password='default_password123'
                    )
                    user.is_active = True
                    user.save()
                    
                    # Create StudentData with EXACT field names from your model
                    student_data = StudentData(
                        user=user,
                        full_name=full_name,
                        student_id=student_id,  # This is a separate field in your model
                        sex=row.get('Sex', '').strip().upper()[:1],  # Just M or F
                        region=row.get('Region', '').strip(),
                        woreda=row.get('Woreda', '').strip(),
                        phone_number=row.get('Phone Number', '').strip(),
                        faculty=row.get('Faculty', '').strip(),
                        year_of_entrance=int(row.get('Year of Entrance', 2024)),  # Your model has year_of_entrance, not year
                        department=row.get('Department', '').strip(),
                        academic_year=int(row.get('Academic Year', 2024)),  # Your model has academic_year as IntegerField
                        mother_name=row.get('Mother Name', '').strip(),
                        mother_phone=row.get('Mother Phone', '').strip(),
                        uploaded_by=request.user,  # Set the user who uploaded
                        status=StudentData.STATUS_UPLOADED,
                    )
                    
                    student_data.save()
                    success_count += 1
                    print(f"✅ Successfully created: {full_name} ({student_id})")
                    
                except Exception as e:
                    error_count += 1
                    detailed_errors.append(f"Row {row_num}: {str(e)}")
                    print(f"❌ Error in row {row_num}: {e}")
                    
                    # Clean up user if created
                    if 'user' in locals():
                        user.delete()
                    continue
            
            # Show results
            if success_count > 0:
                messages.success(
                    request, 
                    f'✅ Successfully uploaded {success_count} student records!'
                )
            
            if error_count > 0:
                error_message = f'❌ {error_count} records failed to upload. '
                if detailed_errors:
                    # Show first 3 errors in the message
                    error_message += ' First errors: ' + '; '.join(detailed_errors[:3])
                
                messages.error(request, error_message)
                
                # Print all errors to console
                print("\n=== ALL UPLOAD ERRORS ===")
                for error in detailed_errors:
                    print(f"  - {error}")
            
            return redirect('upload_student_data')
            
        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
            print(f"CSV processing error: {e}")
            return redirect('upload_student_data')
    
    return render(request, 'upload_student_data.html')

@login_required
@user_passes_test(is_cost_sharing_officer)
def view_students(request):
    students = StudentData.objects.all()
    
    # Add payment status to each student
    for student in students:
        # Find if student has completed payment
        agreements = CostSharingAgreement.objects.filter(
            full_name=student.full_name,
            student__student_id=student.student_id
        )
        
        total_paid = 0
        for agreement in agreements:
            payments = Payment.objects.filter(
                agreement=agreement,
                status__in=['partial', 'completed']
            ).aggregate(total=Sum('amount_paid'))
            total_paid += payments['total'] or 0
        
        student.total_paid = total_paid
        student.has_paid = total_paid > 0
    
    return render(request, 'view_students.html', {'students': students})

# =============================================================================
# NOTICE MANAGEMENT
# =============================================================================

# views.py - Update post_notice function

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'cost_sharing_officer', 'registrar_officer', 'inland_revenue_officer'])
def post_notice(request):
    """Post a new notice with image support"""
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                # Save the notice
                notice = form.save()
                
                # Create notifications for target audience
                notification_count = 0
                audience_roles = form.cleaned_data.get('audience', [])
                
                # Get all users in the selected roles
                for role in audience_roles:
                    target_users = User.objects.filter(role=role, is_active=True)
                    for user in target_users:
                        try:
                            create_notification(
                                recipient=user,
                                title=f"New Notice: {notice.title}",
                                message=notice.content[:100] + '...' if notice.content and len(notice.content) > 100 else (notice.content or 'New notice posted'),
                                notification_type='notice',
                                related_object_id=notice.id,
                                related_object_type='notice'
                            )
                            notification_count += 1
                        except Exception as e:
                            print(f"❌ Failed to create notification for {user.username}: {e}")
                            continue
                
                # Format audience names for message
                role_names = {
                    'student': 'Students',
                    'admin': 'Administrators',
                    'cost_sharing_officer': 'Cost Sharing Officers',
                    'registrar_officer': 'Registrar Officers',
                    'inland_revenue_officer': 'Inland Revenue Officers',
                }
                audience_display = [role_names.get(role, role) for role in audience_roles]
                
                messages.success(request, 
                    f'✅ Notice "{notice.title}" posted successfully! '
                    f'Sent to {notification_count} users ({", ".join(audience_display)}).'
                )
                
                # Redirect to view notices
                return redirect('view_notices')
                
            except Exception as e:
                messages.error(request, f'❌ Error saving notice: {str(e)}')
                print(f"❌ Notice save error: {e}")
                print(f"❌ Traceback: {traceback.format_exc()}")
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = NoticeForm(user=request.user)
    
    return render(request, 'post_notice.html', {
        'form': form,
        'title': 'Post New Notice'
    })
def get_notices_for_role(role):
    """
    Get notices for a specific role - FIXED VERSION
    """
    try:
        from django.utils import timezone
        now = timezone.now()
        
        # Get all active notices that haven't expired
        notices = Notice.objects.filter(
            is_active=True
        ).filter(
            Q(expiry_date__isnull=True) | Q(expiry_date__gte=now)
        )
        
        # DEBUG: Print all notices and their audiences
        print(f"🔍 DEBUG: Checking notices for role: {role}")
        for notice in notices:
            print(f"  - Notice '{notice.title}': audience={notice.audience}")
        
        # Filter notices that include the user's role in their audience
        filtered_notices = []
        for notice in notices:
            # Check if the notice's audience list contains the user's role
            if role in notice.audience:
                filtered_notices.append(notice)
                print(f"  ✅ Notice '{notice.title}' is visible to {role}")
            else:
                print(f"  ❌ Notice '{notice.title}' is NOT visible to {role}")
        
        # Sort by creation date (newest first)
        filtered_notices.sort(key=lambda x: x.created_at, reverse=True)
        
        print(f"🔍 DEBUG: Found {len(filtered_notices)} notices for {role}")
        return filtered_notices
        
    except Exception as e:
        print(f"❌ Error in get_notices_for_role: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        # Fallback: return empty queryset
        return Notice.objects.none()
    
@login_required
def view_notices(request):
    role = getattr(request.user, 'role', None)
    notices = get_notices_for_role(role)
    
    # DEBUG: Print notice details
    print(f"🔔 User role: {role}")
    print(f"🔔 Notices count: {notices.count()}")
    
    for i, notice in enumerate(notices):
        print(f"🔔 Notice {i+1}:")
        print(f"   Title: {notice.title}")
        print(f"   Created by: {getattr(notice, 'created_by', 'No created_by')}")
        print(f"   Posted by: {getattr(notice, 'posted_by', 'No posted_by')}")
        print(f"   Audience: {getattr(notice, 'audience', 'No audience')}")
        print(f"   Target roles: {getattr(notice, 'target_roles', 'No target_roles')}")
        print(f"   Is active: {getattr(notice, 'is_active', 'No is_active')}")
    
    return render(request, 'view_notices.html', {'notices': notices})
@login_required
def view_notices(request):
    role = getattr(request.user, 'role', None)
    notices = get_notices_for_role(role)
    
    # Define allowed roles to post notices
    allowed_roles_to_post = [
        'admin', 
        'cost_sharing_officer', 
        'registrar_officer', 
        'inland_revenue_officer'
    ]
    
    context = {
        'notices': notices,
        'allowed_roles_to_post': allowed_roles_to_post,
    }
    return render(request, 'view_notices.html', context)
# views.py - Add edit_notice function

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'cost_sharing_officer'])
def edit_notice(request, pk):
    """Edit an existing notice"""
    notice = get_object_or_404(Notice, pk=pk)
    
    if request.method == 'POST':
        form = NoticeForm(request.POST, request.FILES, instance=notice, user=request.user)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f'✅ Notice "{notice.title}" updated successfully!')
            return redirect('view_notices')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {field}: {error}')
    else:
        form = NoticeForm(instance=notice, user=request.user)
    
    return render(request, 'post_notice.html', {
        'form': form,
        'title': 'Edit Notice',
        'notice': notice,
        'is_edit': True
    })


# =============================================================================
# FEEDBACK MANAGEMENT
# =============================================================================

@login_required
@user_passes_test(is_student)
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feedback submitted successfully')
            return redirect('dashboard')
    else:
        form = FeedbackForm(user=request.user)
    return render(request, 'submit_feedback.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'cost_sharing_officer'])
def view_feedback(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'view_feedback.html', {'feedbacks': feedbacks})

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'cost_sharing_officer'])
def respond_feedback(request, pk):
    feedback = get_object_or_404(Feedback, pk=pk)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        feedback.response = response
        feedback.date_responded = timezone.now()
        feedback.responded_by = request.user
        feedback.status = 'responded'
        feedback.save()
        
        # Create notification for the student
        create_notification(
            recipient=feedback.student,
            title="Feedback Response Received",
            message=f"Your feedback about '{feedback.subject}' has received a response.",
            notification_type='feedback',
            related_object_id=feedback.id,
            related_object_type='feedback'
        )
        
        messages.success(request, 'Feedback responded successfully')
        return redirect('view_feedback')
    
    return render(request, 'respond_feedback.html', {'feedback': feedback})

# =============================================================================
# NOTIFICATION MANAGEMENT
# =============================================================================

@login_required
def notifications(request):
    """View all notifications for the current user"""
    notifications = request.user.notifications.all()
    
    # Mark all as read when viewing
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    # If there's a related object, redirect to it (pass pk when required).
    if notification.related_object_type and notification.related_object_id:
        related_type = (notification.related_object_type or "").lower()
        related_id = notification.related_object_id
        try:
            if related_type == 'notice':
                return redirect('view_notices')
            elif related_type == 'payment':
                return redirect('payment_history')
            elif related_type in ('agreement', 'costsharingagreement', 'cost_sharing_agreement'):
                # view expecting an agreement pk
                return redirect('view_cost_sharing', pk=related_id)
            elif related_type == 'feedback':
                return redirect('submit_feedback')
        except Exception:
            # If reverse fails, fall back to dashboard
            pass

    return redirect('dashboard')

@login_required
def delete_notification(request, pk):
    """Delete a specific notification"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.delete()
    return redirect('notifications')

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications for the current user as read"""
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def check_new_notifications(request):
    """Check for new notifications for the current user"""
    unread_count = request.user.unread_notifications_count
    latest_notification = request.user.unread_notifications.first()
    
    return JsonResponse({
        'has_new': unread_count > 0,
        'count': unread_count,
        'message': latest_notification.title if latest_notification else None
    })

# =============================================================================
# REPORT GENERATION & DATA EXPORT
# =============================================================================

@login_required
@user_passes_test(is_inland_revenue_officer)
def download_payment_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payment_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Agreement ID', 'Amount Paid', 'Date Paid', 'Payment Method', 'Status', 'Transaction Code'])
    
    payments = Payment.objects.all()
    for payment in payments:
        writer.writerow([
            payment.agreement.student.student_id or '',
            payment.agreement.student.get_full_name() or payment.agreement.student.username,
            payment.agreement.id,
            payment.amount_paid,
            payment.date_paid.strftime('%Y-%m-%d') if payment.date_paid else '',
            payment.get_payment_method_display() or payment.payment_method,
            payment.status,
            payment.transaction_code or '',
        ])
    
    return response

@login_required
@user_passes_test(is_registrar_officer)
def download_student_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Full Name', 'Sex', 'Region', 'Woreda', 'Phone Number', 'Faculty', 'Department', 'Year of Entrance', 'Academic Year'])
    
    students = StudentData.objects.all()
    for student in students:
        writer.writerow([
            student.student_id or '',
            student.full_name,
            student.sex,
            student.region,
            student.woreda,
            student.phone_number,
            student.faculty,
            student.department,
            student.year_of_entrance,
            student.academic_year,
        ])
    
    return response

@login_required
@user_passes_test(is_cost_sharing_officer)
def generate_student_report(request):
    # Get all accepted agreements
    agreements = CostSharingAgreement.objects.filter(status='accepted')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_cost_sharing_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Department', 'Academic Year', 'Total Cost', 'Service Type', 'Date Accepted'])
    
    for agreement in agreements:
        writer.writerow([
            agreement.student.student_id or '',
            agreement.student.get_full_name() or agreement.student.username,
            agreement.department,
            agreement.academic_year,
            agreement.total_cost,
            agreement.get_service_type_display() or agreement.service_type,
            agreement.date_accepted.strftime('%Y-%m-%d') if agreement.date_accepted else '',
        ])
    
    return response

@login_required
@user_passes_test(is_cost_sharing_officer)
def download_student_data_after_payment(request):
    """
    New view: Allow cost officers to download student data after payment completion
    Only shows students who have completed cost sharing payments
    """
    # Get all agreements that are completed
    completed_agreements = CostSharingAgreement.objects.filter(
        status__iexact='completed'
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="completed_student_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Full Name', 'Sex', 'Region', 'Woreda', 'Phone Number',
        'Faculty', 'Department', 'Year of Entrance', 'Academic Year', 
        'Total Cost', 'Amount Paid', 'Status'
    ])
    
    for agreement in completed_agreements:
        student = agreement.student
        student_data = StudentData.objects.filter(student_id=student.student_id).first()
        
        if student_data:
            total_paid = Payment.objects.filter(
                agreement=agreement,
                status__in=['partial', 'completed']
            ).aggregate(total=Sum('amount_paid'))['total'] or 0
            
            writer.writerow([
                student.student_id or '',
                student_data.full_name,
                student_data.sex,
                student_data.region,
                student_data.woreda,
                student_data.phone_number,
                student_data.faculty,
                student_data.department,
                student_data.year_of_entrance,
                student_data.academic_year,
                agreement.total_cost,
                total_paid,
                agreement.status,
            ])
    
    return response

@login_required
@user_passes_test(is_inland_revenue_officer)
def download_student_information(request):
    # Create the HttpResponse object with CSV content-type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_information.csv"'
    writer = csv.writer(response)
    # Write the header
    writer.writerow(['Student ID', 'Full Name', 'Department', 'Academic Year', 'Total Cost', 'Service Type', 'Agreement Status'])
    # Get the student agreements
    agreements = CostSharingAgreement.objects.all()
    for agreement in agreements:
        writer.writerow([
            agreement.student.student_id if agreement.student.student_id else '',
            agreement.full_name,
            agreement.department,
            agreement.academic_year,
            agreement.total_cost,
            agreement.get_service_type_display(),
            agreement.status,
        ])
    return response

@login_required
def export_students_csv(request):
    """
    Export all students as CSV. Restricted to staff users.
    """
    if not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(['username', 'full_name', 'email', 'role'])
    UserModel = get_user_model()
    for u in UserModel.objects.filter(role='student'):
        writer.writerow([u.username, getattr(u, 'get_full_name', lambda: '')(), u.email, getattr(u, 'role', '')])
    return response

@login_required
def export_paid_students_csv(request):
    """
    Export students who made payments as CSV. Restricted to staff users.
    """
    if not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="paid_students.csv"'
    writer = csv.writer(response)
    writer.writerow(['username', 'full_name', 'email', 'amount', 'tin', 'paid_at'])
    qs = Payment.objects.select_related('payer').all()
    for p in qs:
        payer = getattr(p, 'payer', None) or getattr(p, 'student', None) or None
        username = getattr(payer, 'username', '') if payer else ''
        fullname = getattr(payer, 'get_full_name', lambda: '')() if payer else ''
        email = getattr(payer, 'email', '') if payer else ''
        writer.writerow([username, fullname, email, getattr(p, 'amount', ''), getattr(p, 'tin', ''), getattr(p, 'created_at', '')])
    return response

@login_required
@user_passes_test(lambda u: u.role in ['admin', 'cost_sharing_officer', 'inland_revenue_officer'])
def generate_report(request):
    report_type = request.GET.get('type', 'cost_sharing')
    
    if report_type == 'cost_sharing':
        agreements = CostSharingAgreement.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cost_sharing_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Department', 'Year', 'Total Cost', 'Status'])
        
        for agreement in agreements:
            writer.writerow([
                agreement.student.student_id,
                agreement.student.get_full_name(),
                agreement.student.department,
                agreement.academic_year,
                agreement.total_cost,
                agreement.status,
            ])
        
        return response
    
    elif report_type == 'payments':
        payments = Payment.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Name', 'Amount Paid', 'Date Paid', 'Status'])
        
        for payment in payments:
            writer.writerow([
                payment.agreement.student.student_id,
                payment.agreement.student.get_full_name(),
                payment.amount_paid,
                payment.date_paid,
                payment.status,
            ])
        
        return response
    
    return redirect('dashboard')
@login_required
@user_passes_test(is_inland_revenue_officer)
def payment_diagnostic(request):
    """
    Diagnostic view for payment system - helps troubleshoot payment issues
    """
    # Get all payments with related data
    payments = Payment.objects.select_related(
        'agreement', 
        'agreement__student',
        'verified_by'
    ).order_by('-date_paid')
    
    # Payment statistics
    total_payments = payments.count()
    pending_payments = payments.filter(status='pending').count()
    completed_payments = payments.filter(status='completed').count()
    partial_payments = payments.filter(status='partial').count()
    failed_payments = payments.filter(status='failed').count()
    
    # Amount statistics
    total_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    pending_amount = payments.filter(status='pending').aggregate(total=Sum('amount_paid'))['total'] or 0
    completed_amount = payments.filter(status='completed').aggregate(total=Sum('amount_paid'))['total'] or 0
    
    context = {
        'total_payments': total_payments,
        'pending_payments': pending_payments,
        'completed_payments': completed_payments,
        'partial_payments': partial_payments,
        'failed_payments': failed_payments,
        'total_amount': total_amount,
        'pending_amount': pending_amount,
        'completed_amount': completed_amount,
    }
    
    return render(request, 'payment_diagnostic.html', context)
@login_required
@user_passes_test(is_registrar_officer)
def students_without_agreements(request):
    """
    Show students who haven't filled cost sharing agreements for THEIR academic years
    """
    # Get all students from StudentData
    all_students = StudentData.objects.all()
    
    # Find students without agreements for their specific academic years
    students_without_agreements_list = []
    
    for student in all_students:
        has_agreement = CostSharingAgreement.objects.filter(
            student__student_id=student.student_id,
            academic_year=student.academic_year
        ).exists()
        
        if not has_agreement:
            students_without_agreements_list.append(student)
    
    # Convert back to queryset
    students_without_agreements = StudentData.objects.filter(
        id__in=[s.id for s in students_without_agreements_list]
    )
    
    # Apply filters
    department_filter = request.GET.get('department')
    faculty_filter = request.GET.get('faculty')
    year_filter = request.GET.get('year')
    
    if department_filter:
        students_without_agreements = students_without_agreements.filter(
            department__icontains=department_filter
        )
    
    if faculty_filter:
        students_without_agreements = students_without_agreements.filter(
            faculty__icontains=faculty_filter
        )
    
    if year_filter and year_filter.strip():
        try:
            year_int = int(year_filter)
            students_without_agreements = students_without_agreements.filter(
                academic_year=year_int
            )
        except (ValueError, TypeError):
            pass
    
    # Get unique values for filters
    departments = StudentData.objects.values_list('department', flat=True).distinct()
    faculties = StudentData.objects.values_list('faculty', flat=True).distinct()
    years = StudentData.objects.values_list('academic_year', flat=True).distinct()
    
    context = {
        'students': students_without_agreements,
        'current_year': get_current_academic_year(),
        'total_count': students_without_agreements.count(),
        'departments': departments,
        'faculties': faculties,
        'years': years,
        'selected_department': department_filter,
        'selected_faculty': faculty_filter,
        'selected_year': year_filter,
    }
    
    return render(request, 'students_without_agreements.html', context)
@user_passes_test(is_registrar_officer)
def download_students_without_agreements(request):
    """
    Download CSV of students without cost sharing agreements
    """
    current_year = get_current_academic_year()
    
    # Get students without agreements
    all_students = StudentData.objects.all()
    students_with_agreements = CostSharingAgreement.objects.filter(
        academic_year=current_year
    ).values_list('student__student_id', flat=True)
    
    students_without_agreements = all_students.exclude(
        student_id__in=students_with_agreements
    )
    
    # Apply same filters as in the view
    department_filter = request.GET.get('department')
    faculty_filter = request.GET.get('faculty')
    year_filter = request.GET.get('year')
    
    if department_filter:
        students_without_agreements = students_without_agreements.filter(
            department__icontains=department_filter
        )
    
    if faculty_filter:
        students_without_agreements = students_without_agreements.filter(
            faculty__icontains=faculty_filter
        )
    
    # FIX: Convert year_filter to integer if provided
    if year_filter and year_filter.strip():
        try:
            year_int = int(year_filter)
            students_without_agreements = students_without_agreements.filter(
                academic_year=year_int
            )
        except (ValueError, TypeError):
            # If conversion fails, ignore the year filter
            pass
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_without_agreements_{current_year}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Full Name', 'Department', 'Faculty', 
        'Academic Year', 'Phone Number', 'Region', 'Woreda'
    ])
    
    for student in students_without_agreements:
        writer.writerow([
            student.student_id,
            student.full_name,
            student.department,
            student.faculty,
            student.academic_year,
            student.phone_number,
            student.region,
            student.woreda,
        ])
    
    return response
@login_required
@user_passes_test(is_registrar_officer)
def send_reminder_notifications(request):
    """
    Send reminder notifications to students without cost sharing agreements
    """
    if request.method == 'POST':
        current_year = get_current_academic_year()
        
        print("🎯 DEBUG: send_reminder_notifications POST request received")
        print(f"🎯 DEBUG: Current academic year: {current_year}")
        
        # Get base queryset - we need to check for EACH student's academic year
        all_students = StudentData.objects.all()
        
        # We'll process students one by one to check their specific academic year
        students_to_notify = []
        
        for student in all_students:
            # Check if this specific student has an agreement for THEIR academic year
            has_agreement = CostSharingAgreement.objects.filter(
                student__student_id=student.student_id,
                academic_year=student.academic_year  # Use the student's academic year
            ).exists()
            
            if not has_agreement:
                students_to_notify.append(student)
                print(f"🎯 Student {student.student_id} ({student.academic_year}) needs agreement")
        
        students_without_agreements = StudentData.objects.filter(
            id__in=[s.id for s in students_to_notify]
        )
        
        print(f"🎯 DEBUG: Found {students_without_agreements.count()} students needing agreements")
        
        # Apply filters if not force_all
        force_all = request.POST.get('force_all') == 'true'
        
        if not force_all:
            department_filter = request.POST.get('department', '')
            faculty_filter = request.POST.get('faculty', '')
            year_filter = request.POST.get('year', '')
            
            if department_filter:
                students_without_agreements = students_without_agreements.filter(department__icontains=department_filter)
            if faculty_filter:
                students_without_agreements = students_without_agreements.filter(faculty__icontains=faculty_filter)
            if year_filter and year_filter.strip():
                try:
                    year_int = int(year_filter)
                    students_without_agreements = students_without_agreements.filter(academic_year=year_int)
                except (ValueError, TypeError):
                    pass
        
        print(f"🎯 DEBUG: After filters: {students_without_agreements.count()} students")
        
        # Send notifications
        notification_count = 0
        email_count = 0
        
        for student_data in students_without_agreements:
            try:
                student_year = student_data.academic_year
                print(f"🎯 Processing: {student_data.student_id} - {student_data.full_name} (Year: {student_year})")
                
                # Find or create user
                user = User.objects.filter(
                    Q(student_id=student_data.student_id) | 
                    Q(username=student_data.student_id)
                ).first()
                
                if not user:
                    try:
                        user = User.objects.create_user(
                            username=student_data.student_id,
                            password=f"Temp{student_data.student_id}123!",
                            email=f"{student_data.student_id}@student.mau.edu.et",
                            first_name=student_data.full_name.split()[0] if student_data.full_name.split() else student_data.full_name,
                            last_name=' '.join(student_data.full_name.split()[1:]) if len(student_data.full_name.split()) > 1 else '',
                            role='student',
                            student_id=student_data.student_id,
                            department=student_data.department,
                            is_active=True
                        )
                        print(f"🎯 Created user: {user.username}")
                    except Exception as e:
                        print(f"🎯 Error creating user: {e}")
                        continue
                
                # Create notification with correct academic year
                academic_year_display = f"{student_year}-{student_year + 1}"
                create_notification(
                    recipient=user,
                    title="Cost Sharing Agreement Reminder",
                    message=f"Dear {student_data.full_name}, please fill out your cost sharing agreement for academic year {academic_year_display}. The deadline is approaching.",
                    notification_type='reminder'
                )
                notification_count += 1
                
                # Send email with correct academic year
                if user.email:
                    try:
                        send_mail(
                            subject=f'Cost Sharing Agreement Reminder - {academic_year_display}',
                            message=f'Dear {student_data.full_name}, please complete your cost sharing agreement for academic year {academic_year_display} at {settings.SITE_URL}',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user.email],
                            fail_silently=True,
                        )
                        email_count += 1
                        print(f"✅ Email sent to {user.email} for year {academic_year_display}")
                    except Exception as e:
                        print(f"❌ Email failed for {user.email}: {e}")
                
            except Exception as e:
                print(f"❌ Error with student {student_data.student_id}: {e}")
                continue
        
        if notification_count > 0:
            if email_count > 0:
                messages.success(request, f"✅ Successfully sent {notification_count} notifications and {email_count} emails")
            else:
                messages.warning(request, f"⚠️ Sent {notification_count} in-app notifications but {email_count} emails")
        else:
            messages.error(request, "❌ No notifications sent.")
        
        return redirect('students_without_agreements')
    
    return redirect('students_without_agreements')

@login_required
@user_passes_test(is_registrar_officer)
def diagnostic_view(request):
    """
    Quick diagnostic to see what's in the database
    """
    current_year = get_current_academic_year()
    
    print("🔍 DIAGNOSTIC INFORMATION:")
    print(f"Current year: {current_year}")
    
    # Check StudentData
    all_students = StudentData.objects.all()
    print(f"Total StudentData records: {all_students.count()}")
    
    for student in all_students[:5]:
        print(f"StudentData: ID='{student.student_id}', Name='{student.full_name}', Dept='{student.department}'")
    
    # Check CostSharingAgreement
    agreements = CostSharingAgreement.objects.filter(academic_year=current_year)
    print(f"CostSharingAgreements for {current_year}: {agreements.count()}")
    
    # Check Users
    users = User.objects.filter(role='student')
    print(f"Student users: {users.count()}")
    for user in users[:3]:
        print(f"User: {user.username}, StudentID: {getattr(user, 'student_id', 'None')}")
    
    messages.info(request, "Check console for diagnostic information")
    return redirect('students_without_agreements')
    # ...existing code...
@login_required
@user_passes_test(is_student)
def student_feedback_list(request):
    feedbacks = Feedback.objects.filter(student=request.user).order_by('-date_submitted')
    return render(request, 'student_feedback_list.html', {'feedbacks': feedbacks})

@login_required
def student_feedback_detail(request, feedback_id):  # Make sure this parameter matches
    # Get the feedback object for the current student
    feedback = get_object_or_404(Feedback, id=feedback_id, student=request.user)
    
    context = {
        'feedback': feedback,
    }
    return render(request, 'student_feedback_detail.html', context)
@login_required
@user_passes_test(is_registrar_officer)
def edit_student(request, student_id):
    """
    Edit student information - Update BOTH StudentData and User year_of_study
    """
    student_data = get_object_or_404(StudentData, student_id=student_id)
    
    if request.method == 'POST':
        # Create a mutable copy of POST data
        post_data = request.POST.copy()
        
        # ✅ CRITICAL: Handle virtual_balance - if empty, set to 0
        if 'virtual_balance' in post_data and not post_data['virtual_balance'].strip():
            post_data['virtual_balance'] = '0.00'
        
        # Always include student_id and status
        post_data['student_id'] = student_data.student_id
        post_data['status'] = getattr(student_data, 'status', 'active')
        
        # ✅ FIX: Define the form variable here
        form = StudentDataForm(post_data, instance=student_data)
        
        if form.is_valid():
            try:
                # Save the StudentData form
                student_data = form.save(commit=False)
                
                # ✅ DOUBLE-CHECK: Ensure virtual_balance has a value
                if not student_data.virtual_balance:
                    student_data.virtual_balance = 0.00
                
                student_data.save()
                
                # ✅ CRITICAL: Update ALL relevant User fields (not just year_of_study)
                try:
                    # Get the associated user
                    user = student_data.user
                    
                    # Update user fields from StudentData
                    user.department = student_data.department  # Add this line
                    
                    # Get year_of_study from POST data
                    year_of_study = request.POST.get('year_of_study')
                    if year_of_study:
                        user.year_of_study = int(year_of_study)
                    
                    # Also update other fields that might be needed
                    if hasattr(user, 'faculty'):
                        user.faculty = student_data.faculty
                    
                    user.save()
                    
                    print(f"✅ Updated User {user.username}:")
                    print(f"   - Department: {user.department}")
                    print(f"   - Year of Study: {user.year_of_study}")
                    
                except Exception as e:
                    print(f"❌ Error updating user fields: {e}")
                    # Still continue even if user update fails
                
                messages.success(request, f'Student {student_data.full_name} updated successfully!')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'Error saving student: {str(e)}')
                print(f"❌ Save error: {e}")
        else:
            # Display form errors
            print(f"❌ Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # GET request - initialize form with student_data
        form = StudentDataForm(instance=student_data)
    
    # Make certain fields read-only
    if 'student_id' in form.fields:
        form.fields['student_id'].widget.attrs['readonly'] = True
        form.fields['student_id'].help_text = "Student ID cannot be modified"
    
    if 'status' in form.fields:
        form.fields['status'].widget.attrs['readonly'] = True
    
    return render(request, 'edit_student.html', {
        'form': form,
        'student': student_data,
        'title': f"Edit Student: {student_data.full_name}"
    })
@login_required
def print_agreement(request, pk):
    """Print cost sharing agreement"""
    agreement = get_object_or_404(CostSharingAgreement, pk=pk)
    
    # Check permissions
    if request.user.role == 'student' and agreement.student != request.user:
        messages.error(request, 'You can only view your own agreements.')
        return redirect('dashboard')
    
    # Calculate individual service costs if they're not set
    service_count = 0
    if agreement.education_service:
        service_count += 1
    if agreement.food_service:
        service_count += 1
    if agreement.dormitory_service:
        service_count += 1
    
    # Calculate cost per service
    cost_per_service = 0
    if service_count > 0 and agreement.total_cost:
        cost_per_service = agreement.total_cost / service_count
    
    # Create a context with calculated costs
    context = {
        'agreement': agreement,
        'calculated_education_cost': cost_per_service if agreement.education_service else 0,
        'calculated_food_cost': cost_per_service if agreement.food_service else 0,
        'calculated_dormitory_cost': cost_per_service if agreement.dormitory_service else 0,
    }
    
    return render(request, 'print_agreement.html', context)

@login_required
@user_passes_test(is_cost_sharing_officer)
def cost_officer_agreement_detail(request, pk):
    """Cost sharing officer view of agreement details with photo"""
    agreement = get_object_or_404(CostSharingAgreement, pk=pk)
    
    # Get payment information
    payments = Payment.objects.filter(agreement=agreement)
    total_paid = payments.filter(status__in=['completed', 'verified']).aggregate(
        total=Sum('amount_paid')
    )['total'] or 0
    remaining_balance = agreement.total_cost - total_paid
    
    context = {
        'agreement': agreement,
        'payments': payments,
        'total_paid': total_paid,
        'remaining_balance': remaining_balance,
        'payment_progress': (total_paid / agreement.total_cost * 100) if agreement.total_cost > 0 else 0,
    }
    
    return render(request, 'cost_officer_agreement_detail.html', context)
@login_required
@user_passes_test(is_registrar_officer)
def upload_students_to_cost_officer(request):
    """Upload/assign students to cost sharing officers"""
    if request.method == 'POST':
        cost_officer_id = request.POST.get('cost_officer_id')
        student_ids = request.POST.getlist('student_ids')
        send_notification = request.POST.get('send_notification') == 'on'
        only_without_agreements = request.POST.get('only_without_agreements') == 'on'
        
        print(f"🎯 DEBUG: cost_officer_id = {cost_officer_id}")
        print(f"🎯 DEBUG: student_ids = {student_ids}")
        print(f"🎯 DEBUG: send_notification = {send_notification}")
        print(f"🎯 DEBUG: only_without_agreements = {only_without_agreements}")
        
        try:
            cost_officer = User.objects.get(id=cost_officer_id, role='cost_sharing_officer')
            students = StudentData.objects.filter(id__in=student_ids)
            
            print(f"🎯 DEBUG: Found {students.count()} students")
            
            if only_without_agreements:
                # Filter out students who already have agreements
                students_with_agreements = CostSharingAgreement.objects.filter(
                    student__student_id__in=students.values_list('student_id', flat=True)
                ).values_list('student__student_id', flat=True)
                students = students.exclude(student_id__in=students_with_agreements)
                print(f"🎯 DEBUG: After filtering, {students.count()} students remain")
            
            updated_count = 0
            for student in students:
                student.assigned_to = cost_officer
                student.save()
                updated_count += 1
                print(f"🎯 DEBUG: Assigned {student.student_id} to {cost_officer.username}")
            
            # Send notification to cost officer
            if send_notification and updated_count > 0:
                create_notification(
                    recipient=cost_officer,
                    title="New Students Assigned",
                    message=f"{updated_count} students have been assigned to you for cost sharing agreement processing.",
                    notification_type='student_assignment',
                    related_object_id=cost_officer.id,
                    related_object_type='user'
                )
            
            messages.success(request, f'Successfully assigned {updated_count} students to {cost_officer.get_full_name()}.')
            
        except User.DoesNotExist:
            messages.error(request, 'Selected cost sharing officer not found.')
        except Exception as e:
            messages.error(request, f'Error assigning students: {str(e)}')
            print(f"❌ Error: {str(e)}")
    
    return redirect('dashboard')
@login_required
@user_passes_test(is_cost_sharing_officer)
def cost_officer_assigned_list(request):
    """
    List StudentData items assigned to the logged-in cost-sharing officer.
    Paginated.
    """
    # Get students assigned to this cost officer
    qs = StudentData.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        qs = qs.filter(
            Q(full_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    # Add agreement status to each student
    for student in qs:
        student.has_agreement = CostSharingAgreement.objects.filter(
            student__student_id=student.student_id,
            status__in=['accepted', 'completed']
        ).exists()
    
    # Calculate statistics
    total_students = qs.count()
    students_with_agreements_count = sum(1 for student in qs if student.has_agreement)
    students_without_agreements_count = total_students - students_with_agreements_count
    completion_rate = (students_with_agreements_count / total_students * 100) if total_students > 0 else 0
    
    # Pagination
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'student_data_list': page_obj,
        'students_with_agreements_count': students_with_agreements_count,
        'students_without_agreements_count': students_without_agreements_count,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'cost_officer_assigned_list.html', context)

@login_required
@require_http_methods(["GET"])
def get_student_details(request, student_id):
    try:
        student = StudentData.objects.get(id=student_id)
        
        # Get agreement status
        all_agreements = CostSharingAgreement.objects.all()
        students_with_agreements_from_relations = all_agreements.exclude(
            student__isnull=True
        ).values_list('student__student_id', flat=True).distinct()
        
        agreement_full_names = all_agreements.values_list('full_name', flat=True).distinct()
        students_with_matching_names = StudentData.objects.filter(
            full_name__in=agreement_full_names
        ).values_list('student_id', flat=True)
        
        students_with_agreements_ids = list(students_with_agreements_from_relations) + list(students_with_matching_names)
        students_with_agreements_ids = list(filter(None, students_with_agreements_ids))
        students_with_agreements_ids = list(set(students_with_agreements_ids))
        
        has_agreement = student.student_id in students_with_agreements_ids
        
        student_data = {
            'id': student.id,
            'student_id': student.student_id,
            'full_name': student.full_name,
            'department': student.department,
            'faculty': student.faculty,
            'academic_year': student.academic_year,
            'year_of_study': student.year_of_study,
            'year_of_entrance': student.year_of_entrance,
            'phone_number': student.phone_number,
            'email': getattr(student.user, 'email', '') if hasattr(student, 'user') and student.user else '',
            'sex': student.sex,
            'region': student.region,
            'woreda': student.woreda,
            'mother_name': student.mother_name,
            'mother_phone': student.mother_phone,
            'is_graduate': student.is_graduate,
            'created_at': student.created_at.isoformat() if student.created_at else None,
            'has_agreement': has_agreement,
        }
        
        return JsonResponse(student_data)
        
    except StudentData.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def send_student_reminder(request, student_id):
    try:
        student = StudentData.objects.get(id=student_id)
        
        # TODO: Implement actual reminder sending logic
        # This could be:
        # - Sending an email
        # - Sending an SMS
        # - Creating a notification
        # - Logging the reminder
        
        print(f"Reminder sent to student: {student.full_name} ({student.student_id})")
        
        return JsonResponse({'success': True, 'message': 'Reminder sent successfully'})
        
    except StudentData.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)