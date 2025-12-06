#!/usr/bin/env python
"""
Script to populate OCSMS database with initial sample data.
Run this after: python manage.py migrate
"""

import os
import sys
import django
import datetime
from django.utils import timezone

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')
django.setup()

from django.contrib.auth import get_user_model
from cost_sharing.models import (
    CostStructure, CostSharingAgreement, Payment, Notice, Feedback,
    StudentData, BankAccount, BankTransaction
)

User = get_user_model()

def populate_database():
    print("Starting database population...\n")

    # Create users
    print("Creating users...")
    admin_user = User.objects.create_superuser(
        username='rodas',
        email='rodas@mau.edu.et',
        password='rodas123',
        first_name='Rodas',
        last_name='Dilnesa',
        role='admin'
    )

    cost_sharing_officer = User.objects.create_user(
        username='muluken',
        email='muluken@mau.edu.et',
        password='muluken123',
        first_name='Muluken',
        last_name='Semagn',
        role='cost_sharing_officer'
    )

    registrar_officer = User.objects.create_user(
        username='habtamu',
        email='habtamu@mau.edu.et',
        password='habtamu123',
        first_name='Habtamu',
        last_name='Abebaw',
        role='registrar_officer'
    )

    inland_revenue_officer = User.objects.create_user(
        username='tigist',
        email='tigist@mau.edu.et',
        password='tigist123',
        first_name='Tigist',
        last_name='Alemayehu',
        role='inland_revenue_officer'
    )

    # Create students
    print("Creating students...")
    students = []
    for i in range(1, 2):  # only 1 sample student
        student = User.objects.create_user(
            username=f'student{i}',
            email=f'student{i}@mau.edu.et',
            password=f'student{i}',
            first_name=f'Student{i}',
            last_name='User',
            role='student',
            student_id=f'STU{i:03d}',
            department=f'Department {i}',
            year_of_study=i
        )
        students.append(student)

    # Create student data
    print("Creating student data...")
    for i, student in enumerate(students, 1):
        StudentData.objects.create(
            user=student,
            full_name=f'{student.first_name} {student.last_name}',
            student_id=student.student_id,
            sex='M' if i % 2 == 1 else 'F',
            region=f'Region {i}',
            woreda=f'Woreda {i}',
            phone_number=f'0911{i:06d}',
            faculty=f'Faculty {i}',
            year_of_entrance=2020 + i,
            department=student.department,
            academic_year=2023,
            mother_name=f'Mother {i}',
            mother_phone=f'0912{i:06d}'
        )

    # Create cost structures
    print("Creating cost structures...")
    CostStructure.objects.create(
        department='Computer Science',
        year=1,
        education_cost=10000,
        food_cost=5000,
        dormitory_cost=3000,
        total_cost=18000
    )

    # Create cost sharing agreement
    print("Creating cost sharing agreement...")
    student = students[0]
    agreement = CostSharingAgreement.objects.create(
        student=student,
        academic_year=2025,
        full_name=f'{student.first_name} {student.last_name}',
        sex='M',
        date_of_birth=timezone.now().date() - datetime.timedelta(days=365*20),
        place_of_birth='Addis Ababa',
        mother_name=f'Mother of {student.first_name}',
        mother_phone='0911000000',
        mother_address='Addis Ababa',
        preparatory_school='Addis Preparatory',
        high_school_completion_date=timezone.now().date() - datetime.timedelta(days=365*3),
        university_name='Mada Walabu University',
        faculty='Faculty 1',
        department=student.department,
        year=1,
        food_service=True,
        dormitory_service=True,
        education_service=True,
        service_type='in_cash',
        is_graduate=False,
        payment_type='income',
        duration=1,
        total_cost=18000,
        status='accepted'
    )

    # Create payment
    print("Creating payment...")
    Payment.objects.create(
        agreement=agreement,
        amount_paid=6000,
        date_paid=timezone.now().date(),
        payment_method='bank_transfer',
        transaction_code='TXN001',
        status='completed',
        payer=student,
        tin='TIN000001'
    )

    # Create bank account
    print("Creating bank account...")
    bank_account = BankAccount.objects.create(
        account_number='1000123456789',
        bank_name='CBE',
        account_holder='Mada Walabu University',
        branch='Main Branch',
        is_active=True
    )

    # Create bank transaction
    print("Creating bank transaction...")
    BankTransaction.objects.create(
        bank_account=bank_account,
        reference='REF001',
        amount=6000,
        details='Cost sharing payment transaction 1'
    )

    # Create notice
    print("Creating notice...")
    Notice.objects.create(
        title='Cost Sharing Payment Deadline',
        content='Please complete your payments on time.',
        posted_by=admin_user,
        target_roles=['student'],
        audience='specific',
        expiry_date=timezone.now() + datetime.timedelta(days=30)
    )

    # Create feedback
    print("Creating feedback...")
    feedback = Feedback.objects.create(
        student=student,
        subject='Feedback from Student',
        message='Everything works great so far!',
        status='pending'
    )

    feedback.response = 'Thank you for your feedback!'
    feedback.responded_by = admin_user
    feedback.date_responded = timezone.now()
    feedback.status = 'responded'
    feedback.save()

    print("\n✓ Database populated successfully!")
    print(f"  - 1 Admin, 3 Officers, 1 Student")
    print(f"  - 1 Cost structure, 1 Agreement, 1 Payment, 1 Notice, 1 Feedback\n")

if __name__ == '__main__':
    try:
        populate_database()
    except Exception as e:
        print(f"\n✗ Error populating database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
