import os
from django import forms
import re
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

class AdminUserUpdateForm(forms.ModelForm):
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
        fields = ['username', 'email', 'first_name', 'last_name', 'phone',
                 'role', 'department', 'student_id', 'year_of_study',
                 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
# For regular users (no role field)
class UserUpdateForm(forms.ModelForm):
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
            'department', 'student_id', 'year_of_study'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_study': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user

# For admin users (with role field)
class AdminUserUpdateForm(UserChangeForm):
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
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user

class CostSharingForm(forms.ModelForm):
    # Add phone_number field if it's not in the model but needed in form
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '09XXXXXXXX'}),
        help_text="Must be 10 digits starting with 09"
    )
    
    # Add year_of_entrance field if needed
    year_of_entrance = forms.IntegerField(
        required=True,
        min_value=1900,
        max_value=timezone.now().year - 1,
        help_text=f"Must be before {timezone.now().year}"
    )

    class Meta:
        model = CostSharingAgreement
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
            'mother_phone': forms.TextInput(attrs={'placeholder': '09XXXXXXXX'}),
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
        
        # Auto-fill from user data if available
        if self.user:
            self.fields['full_name'].initial = self.user.get_full_name()
            self.fields['department'].initial = self.user.department
            self.fields['year'].initial = self.user.year_of_study
            
            # Make department and year read-only (from registrar)
            self.fields['department'].disabled = True
            self.fields['year'].disabled = True
            self.fields['department'].help_text = "Department is set by registrar and cannot be changed"
            self.fields['year'].help_text = "Year of study is set by registrar and cannot be changed"
            
            # Set initial values for phone and year of entrance if available
            if hasattr(self.user, 'phone') and self.user.phone:
                self.fields['phone_number'].initial = self.user.phone
            
            # Try to get year of entrance from student data
            try:
                from .models import StudentData
                student_data = StudentData.objects.filter(student_id=self.user.student_id).first()
                if student_data and hasattr(student_data, 'year_of_entrance'):
                    self.fields['year_of_entrance'].initial = student_data.year_of_entrance
            except:
                pass

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any spaces or special characters
            phone_number = ''.join(filter(str.isdigit, phone_number))
            
            # Validate Ethiopian phone number format
            pattern = r'^09[0-9]{8}$'
            if not re.match(pattern, phone_number):
                raise forms.ValidationError(
                    'Phone number must be exactly 10 digits and start with 09. Format: 09XXXXXXXX'
                )
        return phone_number

    def clean_mother_phone(self):
        mother_phone = self.cleaned_data.get('mother_phone')
        if mother_phone:
            # Remove any spaces or special characters
            mother_phone = ''.join(filter(str.isdigit, mother_phone))
            
            # Validate Ethiopian phone number format
            pattern = r'^09[0-9]{8}$'
            if not re.match(pattern, mother_phone):
                raise forms.ValidationError(
                    'Mother\'s phone number must be exactly 10 digits and start with 09. Format: 09XXXXXXXX'
                )
        return mother_phone

    def clean_year_of_entrance(self):
        year_of_entrance = self.cleaned_data.get('year_of_entrance')
        current_year = timezone.now().year
        
        if year_of_entrance:
            if year_of_entrance >= current_year:
                raise forms.ValidationError(
                    f'Year of entrance must be before the current year ({current_year})'
                )
        return year_of_entrance

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            current_date = timezone.now().date()
            # Calculate minimum birth date (10 years ago)
            min_birth_date = current_date - timezone.timedelta(days=365 * 10)
            
            if date_of_birth > min_birth_date:
                raise forms.ValidationError(
                    'Date of birth must be at least 10 years before the current date'
                )
        return date_of_birth

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            # Validate year of study is between 1 and 6 (typical undergraduate range)
            if not 1 <= year <= 6:
                raise forms.ValidationError('Year of study must be between 1 and 6')
        return year

    def clean(self):
        cleaned_data = super().clean()
        
        # Check if student is allowed to fill cost sharing based on year of study
        year = cleaned_data.get('year')
        if year and self.user:
            # Add any additional restrictions based on year of study
            # For example, restrict certain years from submitting
            if year < 1:
                raise forms.ValidationError('Invalid year of study')
            
            # You can add more specific restrictions here:
            # if year > 4 and not cleaned_data.get('is_graduate'):
            #     self.add_error('is_graduate', 'Graduate students must check this option')

        # Validate withdrawal fields if has_withdrawn is True
        if cleaned_data.get('has_withdrawn'):
            required_withdrawal_fields = ['withdrawal_date', 'withdrawal_year']
            for field in required_withdrawal_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required when "Has Withdrawn" is checked.')

        # Validate transfer fields if has_transferred is True
        if cleaned_data.get('has_transferred'):
            required_transfer_fields = ['previous_university', 'transfer_date']
            for field in required_transfer_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required when "Has Transferred" is checked.')

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
            
        # Set student for new submissions
        if not self.instance.pk and self.user:
            instance.student = self.user
            
        # Set phone number if the field exists in the model
        if hasattr(instance, 'phone_number') and 'phone_number' in self.cleaned_data:
            instance.phone_number = self.cleaned_data['phone_number']
            
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
    # Add image field
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload an image for this notice (optional)"
    )
    
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
        fields = ("title", "content", "image", "audience", "is_active", "expiry_date")
        widgets = {
            "expiry_date": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "form-control"
            }),
            "content": forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Enter notice content here...',
                'class': 'form-control'
            }),
            "title": forms.TextInput(attrs={'class': 'form-control'}),
            "is_active": forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'audience': "Select which user roles can see this notice",
            'expiry_date': "Optional - notice will automatically expire after this date",
            'is_active': "Uncheck to hide this notice without deleting it",
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set initial audience from JSON field
        if self.instance and self.instance.pk:
            self.initial['audience'] = self.instance.audience
        
        # For new notices, pre-select the user's own role for convenience
        if not self.instance.pk and self.user and self.user.role:
            self.initial['audience'] = [self.user.role]
        
        # Set default expiry date if new notice
        if not self.instance.pk:
            default_expiry = timezone.now() + timezone.timedelta(days=30)
            self.initial['expiry_date'] = default_expiry.strftime('%Y-%m-%dT%H:%M')
    
    def clean_audience(self):
        """Ensure audience is a list"""
        audience = self.cleaned_data.get('audience', [])
        return list(audience)  # Ensure it's a proper list
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image', False)
        if image:
            # Check file size (max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise ValidationError(f'Image file too large (max {max_size/1024/1024}MB)')
            
            # Check file extension
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError(f'Unsupported file format. Allowed: {", ".join(valid_extensions)}')
            
            # Check image dimensions (optional)
            try:
                from PIL import Image
                img = Image.open(image)
                width, height = img.size
                if width > 5000 or height > 5000:
                    raise ValidationError('Image dimensions too large (max 5000x5000 pixels)')
            except ImportError:
                pass  # PIL not installed, skip dimension check
        
        return image
    
    def save(self, commit=True):
        """Save notice with audience as JSON list"""
        notice = super().save(commit=False)
        
        # Set audience from choices field
        notice.audience = self.cleaned_data.get('audience', [])
        
        # Set posted_by if it's a new notice
        if not notice.pk and self.user:
            notice.posted_by = self.user
        
        if commit:
            notice.save()
        
        return notice
    
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
    # Add year_of_study as a form field (even if it's not in the model yet)
    year_of_study = forms.ChoiceField(
        choices=[
            (1, 'Year 1'),
            (2, 'Year 2'), 
            (3, 'Year 3'),
            (4, 'Year 4'),
            (5, 'Year 5'),
            (6, 'Year 6'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = StudentData
        exclude = ("user", "created_at", "assigned_to", "uploaded_by")
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'sex': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'woreda': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_entrance': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.HiddenInput(),
            'is_graduate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for year_of_study from the associated User
        if self.instance and self.instance.pk and hasattr(self.instance, 'user'):
            user_year = getattr(self.instance.user, 'year_of_study', 1)
            self.fields['year_of_study'].initial = user_year

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
        