# cost_sharing/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
import uuid
import random  # ADD THIS IMPORT
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError 
from django.db.models import Sum
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('cost_sharing_officer', 'Cost Sharing Officer'),
        ('registrar_officer', 'Registrar Officer'),
        ('inland_revenue_officer', 'Inland Revenue Officer'),
    )
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    year_of_study = models.IntegerField(blank=True, null=True)
    
    class Meta:
        permissions = [
            ("can_manage_students", "Can manage student data"),
            ("can_manage_costs", "Can manage cost structures"),
            ("can_manage_payments", "Can manage payments"),
            ("can_post_notices", "Can post notices"),
        ]
    
    @property
    def unread_notifications_count(self):
        """Return the count of unread notifications for this user"""
        return self.notifications.filter(is_read=False).count()
    
    @property
    def unread_notifications(self):
        """Return unread notifications for this user"""
        return self.notifications.filter(is_read=False)

class CostStructure(models.Model):
    department = models.CharField(max_length=100)
    year = models.IntegerField()
    education_cost = models.DecimalField(max_digits=10, decimal_places=2)
    food_cost = models.DecimalField(max_digits=10, decimal_places=2)
    dormitory_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate total cost before saving
        self.total_cost = self.education_cost + self.food_cost + self.dormitory_cost
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.department} - Year {self.year}"

class BankAccount(models.Model):
    BANK_CHOICES = [
        ('cbe', 'Commercial Bank of Ethiopia'),
        ('awash', 'Awash Bank'),
        ('dashen', 'Dashen Bank'),
        ('abyssinia', 'Bank of Abyssinia'),
        ('nib', 'Nib International Bank'),
        ('abay', 'Abay Bank'),
        ('berhan', 'Berhan Bank'),
        ('other', 'Other Bank'),
    ]
    
    bank_name = models.CharField(max_length=100, choices=BANK_CHOICES)
    account_number = models.CharField(max_length=50, unique=True)
    account_holder_name = models.CharField(max_length=200)
    branch = models.CharField(max_length=100)
    swift_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        ordering = ['bank_name', 'account_number']

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.account_holder_name})"

class CostSharingAgreement(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('in_kind', 'In Kind'),
        ('in_cash', 'In Cash'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('service', 'To Provide Service'),
        ('income', 'To Be Paid by Income'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cost_sharing_agreements')
    academic_year = models.IntegerField()
    date_filled = models.DateField(auto_now_add=True)
    
    # Personal Information
    full_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    mother_phone = models.CharField(max_length=20)
    mother_address = models.TextField()
    
    # Educational Background
    preparatory_school = models.CharField(max_length=100)
    high_school_completion_date = models.DateField()
    university_name = models.CharField(max_length=100)
    faculty = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year = models.IntegerField()
    
    # Withdrawal Information - All optional with proper defaults
    has_withdrawn = models.BooleanField(default=False)
    withdrawal_date = models.DateField(blank=True, null=True)
    withdrawal_month = models.CharField(max_length=20, blank=True, null=True)
    withdrawal_year = models.IntegerField(blank=True, null=True)
    withdrawal_semester = models.CharField(max_length=20, blank=True, null=True)
    
    # Transfer Information - All optional with proper defaults
    has_transferred = models.BooleanField(default=False)
    previous_university = models.CharField(max_length=100, blank=True, null=True)
    previous_college = models.CharField(max_length=100, blank=True, null=True)
    previous_department = models.CharField(max_length=100, blank=True, null=True)
    transfer_date = models.DateField(blank=True, null=True)
    transfer_month = models.CharField(max_length=20, blank=True, null=True)
    transfer_year = models.IntegerField(blank=True, null=True)
    transfer_semester = models.CharField(max_length=20, blank=True, null=True)
    previous_total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Service Information
    food_service = models.BooleanField(default=False)
    dormitory_service = models.BooleanField(default=False)
    education_service = models.BooleanField(default=True)
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPE_CHOICES)
    is_graduate = models.BooleanField(default=False)
    payment_type = models.CharField(max_length=20, blank=True, null=True, choices=PAYMENT_TYPE_CHOICES)
    duration = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    
    receipt = models.FileField(
        upload_to='cost_sharing_receipts/',
        help_text="Photo/receipt is required"
    )
    
    @property
    def total_cost(self):
        """Calculate total cost automatically based on selected services and cost structure"""
        total = 0
        
        try:
            # Get the cost structure for this department and year
            cost_structure = CostStructure.objects.get(
                department=self.department,
                year=self.year
            )
            
            # Add costs for selected services
            if self.education_service:
                total += cost_structure.education_cost
            if self.food_service:
                total += cost_structure.food_cost
            if self.dormitory_service:
                total += cost_structure.dormitory_cost
                
        except CostStructure.DoesNotExist:
            # If no cost structure exists, return 0
            pass
            
        return total
    
    def get_total_paid(self):
        """Calculate total amount paid for this agreement - EXCLUDE cancelled/failed payments"""
        valid_statuses = ['verified', 'completed', 'partial']  # EXCLUDES 'cancelled', 'failed', 'pending'
        
        try:
            # Try using the reverse relationship from Payment model
            total = self.payments.filter(status__in=valid_statuses).aggregate(
                total=Sum('amount_paid')
            )['total'] or 0
            
        except AttributeError:
            # If payments relationship doesn't exist, try payment_set
            try:
                total = self.payment_set.filter(status__in=valid_statuses).aggregate(
                    total=Sum('amount_paid')
                )['total'] or 0
            except AttributeError:
                # If neither exists, check if there are any payments manually
                total = Payment.objects.filter(
                    agreement=self, 
                    status__in=valid_statuses
                ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        return total
    
    def get_remaining_balance(self):
        """Calculate remaining balance - EXCLUDE cancelled/failed payments"""
        return max(0, self.total_cost - self.get_total_paid())
    
    def __str__(self):
        return f"{self.student.username} - {self.academic_year}"
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('completed', 'Completed'),
        ('partial', 'Partial Payment'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_banking', 'Mobile Banking'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
    ]

    # Relationships
    agreement = models.ForeignKey(
        'CostSharingAgreement', 
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='payments'
    )
    bank_account = models.ForeignKey(
        BankAccount,  # Now BankAccount is defined above
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Bank Account Used"
    )
    tin = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name="Tax Identification Number"
    )
    # Payment details
    transaction_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    receipt = models.FileField(upload_to='payment_receipts/', blank=True, null=True)
    
    # Status and verification
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    date_paid = models.DateTimeField(default=timezone.now)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-date_paid', '-created_at']
        indexes = [
            models.Index(fields=['transaction_code']),
            models.Index(fields=['status']),
            models.Index(fields=['date_paid']),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.amount_paid} by {self.payer.username}"

    def save(self, *args, **kwargs):
        # Generate transaction code if not provided
        if not self.transaction_code:
            self.transaction_code = f"TXN{self.id or timezone.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)

    def get_remaining_balance(self):
        """Calculate remaining balance for the agreement"""
        total_paid = Payment.objects.filter(
            agreement=self.agreement,
            status__in=['verified', 'completed', 'partial']
        ).exclude(id=self.id).aggregate(total=Sum('amount_paid'))['total'] or 0
        total_paid += self.amount_paid
        return self.agreement.total_cost - total_paid

# models.py - Update your Notice model

class Notice(models.Model):
    AUDIENCE_CHOICES = [
        ('student', 'Students'),
        ('admin', 'Administrators'),
        ('cost_sharing_officer', 'Cost Sharing Officers'),
        ('registrar_officer', 'Registrar Officers'),
        ('inland_revenue_officer', 'Inland Revenue Officers'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='notices/%Y/%m/%d/',  # Organized by year/month/day
        blank=True,
        null=True,
        help_text="Upload an image for this notice (optional)"
    )
    audience = models.JSONField(default=list, help_text="List of roles that can see this notice")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    posted_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def audience_display(self):
        """Return human-readable audience names"""
        role_names = {
            'student': 'Students',
            'admin': 'Administrators', 
            'cost_sharing_officer': 'Cost Sharing Officers',
            'registrar_officer': 'Registrar Officers',
            'inland_revenue_officer': 'Inland Revenue Officers',
        }
        return [role_names.get(role, role) for role in self.audience]
    
    @property
    def has_image(self):
        """Check if notice has an image"""
        return bool(self.image)
    
    @property
    def image_url(self):
        """Return image URL or None"""
        if self.image:
            return self.image.url
        return None
    
    def is_expired(self):
        """Check if notice is expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False
    
    def save(self, *args, **kwargs):
        # If no expiry date set, default to 30 days from creation
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)

class Feedback(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True, null=True)
    date_responded = models.DateTimeField(blank=True, null=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='feedback_responses')
    status = models.CharField(max_length=20, default='pending')
    
    def __str__(self):
        return f"{self.student.username} - {self.subject}"

class StudentData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    sex = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    region = models.CharField(max_length=50)
    woreda = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    faculty = models.CharField(max_length=100)
    year_of_entrance = models.IntegerField()
    year_of_study = models.IntegerField(
        choices=[
            (1, 'Year 1'),
            (2, 'Year 2'), 
            (3, 'Year 3'),
            (4, 'Year 4'),
            (5, 'Year 5'),
            (6, 'Year 6'),
        ],
        default=1,
        blank=True,
        null=True,
        verbose_name='Year of Study'
    )
    department = models.CharField(max_length=100)
    academic_year = models.IntegerField()
    mother_name = models.CharField(max_length=100)
    mother_phone = models.CharField(max_length=20)
    uploaded_file = models.FileField(upload_to='student_uploads/', blank=True, null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploads')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_student_data')
    is_graduate = models.BooleanField(default=False)
    # virtual balance used for virtual payments
    virtual_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    STATUS_UPLOADED = 'uploaded'
    STATUS_ASSIGNED_TO_COST = 'assigned_to_cost_officer'
    STATUS_ASSIGNED_TO_INLAND = 'assigned_to_inland_officer'
    STATUS_CHOICES = [
        (STATUS_UPLOADED, 'Uploaded by Registrar'),
        (STATUS_ASSIGNED_TO_COST, 'Assigned to Cost Officer'),
        (STATUS_ASSIGNED_TO_INLAND, 'Assigned to Inland Officer'),
    ]
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default=STATUS_UPLOADED)
    created_at = models.DateTimeField(auto_now_add=True)

    def assign_to_cost_officer(self, user):
        self.assigned_to = user
        self.status = self.STATUS_ASSIGNED_TO_COST
        self.save()

    def assign_to_inland_officer(self, user):
        self.assigned_to = user
        self.status = self.STATUS_ASSIGNED_TO_INLAND
        self.save()

class Agreement(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

class BankTransaction(models.Model):
    bank_account = models.ForeignKey('BankAccount', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    reference = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('agreement', 'Agreement'),
        ('payment', 'Payment'),
        ('notice', 'Notice'),
        ('feedback', 'Feedback'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"