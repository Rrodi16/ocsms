import os
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import (
    CostSharingAgreement,
    CostStructure,
    Payment,
    Notice,
    Feedback,
    StudentData,
    BankAccount,
)

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "phone",
            "student_id",
            "department",
            "year_of_study",
            "is_staff",
            "is_superuser",
        )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "role",
            "first_name",
            "last_name",
            "phone",
            "student_id",
            "department",
            "year_of_study",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


# Alias used in some views/templates
SiteUserCreationForm = CustomUserCreationForm


class UserUpdateForm(UserChangeForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password to change it'
        }),
        help_text="Leave blank to keep current password"
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'role', 'department', 'student_id', 'year_of_study',
            'is_active', 'is_staff'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
        
        # Make role field read-only for non-admin users
        if not (self.instance.is_superuser or self.instance.role == 'admin'):
            self.fields['role'].disabled = True
            self.fields['is_active'].disabled = True
            self.fields['is_staff'].disabled = True
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user

class CostSharingForm(forms.ModelForm):
    class Meta:
        model = CostSharingAgreement
        # Explicitly list all fields instead of using __all__ + exclude
        fields = [
            'academic_year', 'full_name', 'sex', 'date_of_birth', 'place_of_birth',
            'mother_name', 'mother_phone', 'mother_address', 'preparatory_school',
            'high_school_completion_date', 'university_name', 'faculty', 'department',
            'year', 'has_withdrawn', 'withdrawal_date', 'withdrawal_month', 
            'withdrawal_year', 'withdrawal_semester', 'has_transferred', 
            'previous_university', 'previous_college', 'previous_department',
            'transfer_date', 'transfer_month', 'transfer_year', 'transfer_semester', 
            'previous_total_cost', 'food_service', 'dormitory_service', 
            'education_service', 'service_type', 'is_graduate', 'payment_type', 
            'duration', 'receipt'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'high_school_completion_date': forms.DateInput(attrs={'type': 'date'}),
            'withdrawal_date': forms.DateInput(attrs={'type': 'date'}),
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'academic_year': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set academic year to current year for new submissions
        if not self.instance.pk:
            current_year = timezone.now().year
            self.initial['academic_year'] = current_year
        
        # If this is an existing instance (resubmission), make file field optional
        if self.instance and self.instance.pk:
            self.fields['receipt'].required = False
            self.fields['receipt'].help_text = "Optional - keep existing photo or upload new one"
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate withdrawal fields if has_withdrawn is True
        if cleaned_data.get('has_withdrawn'):
            if not cleaned_data.get('withdrawal_date'):
                self.add_error('withdrawal_date', 'Withdrawal date is required when "Has Withdrawn" is checked.')
        
        # Validate transfer fields if has_transferred is True
        if cleaned_data.get('has_transferred'):
            if not cleaned_data.get('previous_university'):
                self.add_error('previous_university', 'Previous university is required when "Has Transferred" is checked.')
        
        return cleaned_data
    
    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        
        # If this is a resubmission and no new file is provided, keep the existing one
        if self.instance and self.instance.pk and not receipt:
            return self.instance.receipt
        
        if receipt:
            # Validate file size (5MB limit)
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be no more than 5MB.')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            import os
            ext = os.path.splitext(receipt.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Unsupported file type. Please upload JPG, PNG, or PDF files only.')
        
        # For new submissions, receipt is required
        if not self.instance.pk and not receipt:
            raise forms.ValidationError('Photo/Receipt is required for new submissions.')
        
        return receipt
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Ensure academic year is set
        if not instance.academic_year:
            instance.academic_year = timezone.now().year
            
        if commit:
            instance.save()
        return instance

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            "agreement",
            "payer",
            "amount_paid",
            "date_paid",
            "payment_method",
            "transaction_code",
            "notes",
            "receipt",
            "tin",
            "status",
            "verified_at",
            "verified_by",
        )
        widgets = {
            "date_paid": forms.DateInput(attrs={"type": "date"}),
            "verified_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        # If payer should default to current user, and field exists
        if user is not None and "payer" in self.fields:
            self.fields["payer"].initial = user


class StudentPaymentForm(forms.ModelForm):
    bank_account = forms.ModelChoiceField(
        queryset=BankAccount.objects.filter(is_active=True),
        empty_label="Select Bank Account",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': 'required'
        })
    )
    
    class Meta:
        model = Payment
        fields = ['agreement', 'amount_paid', 'payment_method', 'receipt', 'bank_account']
        widgets = {
            'agreement': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00',
                'required': 'required'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required' 
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'accept': 'image/*,.pdf'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        print(f"=== DEBUG: Initializing form for user: {self.user.username if self.user else 'None'}")
        
        if self.user:
            # Get accepted agreements for this user
            accepted_agreements = CostSharingAgreement.objects.filter(
                student=self.user,
                status='accepted'
            )
            print(f"=== DEBUG: Found {accepted_agreements.count()} accepted agreements")
            
            self.fields['agreement'].queryset = accepted_agreements
            
            # If no accepted agreements, disable the form
            if not accepted_agreements.exists():
                for field_name, field in self.fields.items():
                    field.disabled = True
                    field.required = False
    
    def clean(self):
        cleaned_data = super().clean()
        print("=== DEBUG: Form clean method called")
        
        # Check if user has accepted agreements
        if self.user:
            accepted_agreements = CostSharingAgreement.objects.filter(
                student=self.user, 
                status='accepted'
            )
            if not accepted_agreements.exists():
                raise forms.ValidationError(
                    "You don't have any accepted cost sharing agreements. "
                    "Please submit an agreement and wait for approval."
                )
        
        return cleaned_data
    
    def clean_amount_paid(self):
        amount = self.cleaned_data.get('amount_paid')
        if amount and amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than 0.")
        return amount
    
    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt:
            # Check file size (5MB limit)
            if receipt.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be no more than 5MB.")
            
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
            import os
            ext = os.path.splitext(receipt.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file type. Please upload JPG, PNG, or PDF.")
        
        return receipt
    
class PaymentVerificationForm(forms.ModelForm):
    """Form for inland revenue officers to verify payments"""
    class Meta:
        model = Payment
        fields = ['status', 'notes', 'verified_by', 'verified_at']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'verified_at': forms.DateTimeInput(attrs={
                'class': 'form-control', 
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove verified_by field from form - it will be set automatically
        if 'verified_by' in self.fields:
            del self.fields['verified_by']

class NoticeForm(forms.ModelForm):
    # Make audience a MultipleChoiceField with checkboxes for ALL roles
    audience = forms.MultipleChoiceField(
        choices=[
            ('student', 'Students'),
            ('cost_sharing_officer', 'Cost Sharing Officers'),
            ('registrar_officer', 'Registrar Officers'),
            ('inland_revenue_officer', 'Inland Revenue Officers'),
            ('admin', 'Administrators'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Visible To"
    )
    
    class Meta:
        model = Notice
        fields = ("title", "content", "audience", "is_active", "expiry_date")
        widgets = {
            "expiry_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "content": forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter notice content here...'}),
        }
        help_texts = {
            'audience': "Select which user roles can see this notice",
            'expiry_date': "Optional - notice will automatically expire after this date",
            'is_active': "Uncheck to hide this notice without deleting it",
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # For new notices, pre-select the user's own role for convenience
        if not self.instance.pk and self.user and self.user.role:
            self.initial['audience'] = [self.user.role]
    
    def clean_audience(self):
        """Ensure audience is a list"""
        audience = self.cleaned_data.get('audience', [])
        return list(audience)  # Ensure it's a proper list
    
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("student", "subject", "message", "status", "response", "date_responded", "responded_by")
        widgets = {"date_responded": forms.DateTimeInput(attrs={"type": "datetime-local"})}

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        if user is not None and "student" in self.fields:
            self.fields["student"].initial = user

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self._user and not getattr(obj, "student", None):
            obj.student = self._user
        if commit:
            obj.save()
            try:
                self.save_m2m()
            except Exception:
                pass
        return obj


class StudentDataForm(forms.ModelForm):
    class Meta:
        model = StudentData
        exclude = ("user", "created_at", "assigned_to", "uploaded_by")


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ("account_number", "bank_name", "account_holder_name", "branch", "is_active")
        widgets = {
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account number'
            }),
            'bank_name': forms.Select(attrs={'class': 'form-control'}),
            'account_holder_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter account holder name'
            }),
            'branch': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch name'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_account_number(self):
        acc = self.cleaned_data.get("account_number")
        if BankAccount.objects.exclude(pk=getattr(self.instance, "pk", None)).filter(account_number=acc).exists():
            raise forms.ValidationError("Account number already exists.")
        return acc
    
class CostStructureForm(forms.ModelForm):
    class Meta:
        model = CostStructure
        fields = ['department', 'year', 'education_cost', 'food_cost', 'dormitory_cost']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'education_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'food_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'dormitory_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'education_cost': 'Education Cost ($)',
            'food_cost': 'Food Cost ($)',
            'dormitory_cost': 'Dormitory Cost ($)',
        }