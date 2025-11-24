from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    CostSharingAgreement,
    CostStructure,
    Payment,
    Notice,
    Feedback,
    StudentData,
    BankAccount,
    Notification,
)
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "role", "phone", "student_id", "department", "year_of_study")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "role", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

admin.site.register(User, UserAdmin)

# Register other models with basic admins
@admin.register(CostSharingAgreement)
class CostSharingAgreementAdmin(admin.ModelAdmin):
    list_display = ("student", "academic_year", "total_cost", "status", "date_filled")
    search_fields = ("student__username", "student__student_id")


@admin.register(CostStructure)
class CostStructureAdmin(admin.ModelAdmin):
    list_display = ("department", "year", "total_cost")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("agreement", "amount_paid", "date_paid", "status")
    search_fields = ("agreement__student__username", "transaction_code")


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "is_active", "created_at")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "date_submitted", "status")


@admin.register(StudentData)
class StudentDataAdmin(admin.ModelAdmin):
    list_display = ("full_name", "student_id", "department", "academic_year")


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("account_number", "bank_name", "account_holder_name", "is_active")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "created_at")
