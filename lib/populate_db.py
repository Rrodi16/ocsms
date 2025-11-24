import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')
django.setup()

from django.contrib.auth import get_user_model
from cost_sharing.models import (
    CostStructure, CostSharingAgreement, Payment, Notice, Feedback, 
    StudentData, BankAccount, BankTransaction, Notification
)
from django.utils import timezone
import datetime

User = get_user_model()

def populate_database():
    print("Starting database population...\n")
    
    # Create users
    print("Creating users...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@mau.edu.et',
        password='admin123',
        first_name='Admin',
        last_name='User',
        role='admin'
    )

    cost_sharing_officer = User.objects.create_user(
        username='csofficer',
        email='csofficer@mau.edu.et',
        password='csofficer123',
        first_name='Cost',
        last_name='Officer',
        role='cost_sharing_officer'
    )

    registrar_officer = User.objects.create_user(
        username='regofficer',
        email='regofficer@mau.edu.et',
        password='regofficer123',
        first_name='Registrar',
        last_name='Officer',
        role='registrar_officer'
    )

    inland_revenue_officer = User.objects.create_user(
        username='irofficer',
        email='irofficer@mau.edu.et',
        password='irofficer123',
        first_name='Inland',
        last_name='Officer',
        role='inland_revenue_officer'
    )

    # Create students
    print("Creating students...")
    students = []
    for i in range(1, 6):
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

    # Create student data for each student
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
    departments = ['Computer Science', 'Electrical Engineering', 'Civil Engineering', 'Mechanical Engineering', 'Chemical Engineering']
    for i, dept in enumerate(departments):
        CostStructure.objects.create(
            department=dept,
            year=i+1,
            education_cost=10000 + i*1000,
            food_cost=5000 + i*500,
            dormitory_cost=3000 + i*300,
            total_cost=18000 + i*1800
        )

    # Create cost sharing agreements for each student
    print("Creating cost sharing agreements...")
    for student in students:
        for year in range(1, 4):
            agreement = CostSharingAgreement.objects.create(
                student=student,
                academic_year=2020 + year,
                full_name=f'{student.first_name} {student.last_name}',
                sex='M' if student.year_of_study % 2 == 1 else 'F',
                date_of_birth=timezone.now().date() - datetime.timedelta(days=365*20),
                place_of_birth='Addis Ababa',
                mother_name=f'Mother of {student.first_name}',
                mother_phone=f'0911{student.year_of_study:06d}',
                mother_address='Addis Ababa',
                preparatory_school='Addis Ababa Preparatory School',
                high_school_completion_date=timezone.now().date() - datetime.timedelta(days=365*3),
                university_name='Mada Walabu University',
                faculty=f'Faculty {year}',
                department=student.department,
                year=year,
                food_service=True,
                dormitory_service=True,
                education_service=True,
                service_type='in_cash',
                is_graduate=(year == 3),
                payment_type='income',
                duration=1,
                total_cost=18000 + year*1800,
                status='accepted'  # Set to accepted so students can make payments
            )

            # Create payments for each agreement
            for j in range(1, 3):
                Payment.objects.create(
                    agreement=agreement,
                    amount_paid=5000 + j*1000,
                    date_paid=timezone.now().date() - datetime.timedelta(days=j*30),
                    payment_method='bank_transfer',
                    transaction_code=f'TXN{agreement.id}{j}',
                    status='completed',
                    payer=student,
                    tin=f'TIN{student.id:06d}'  # Added TIN for each payment
                )

    # Create bank accounts
    print("Creating bank accounts...")
    bank_accounts = []
    banks = [
        ('1000123456789', 'CBE', 'Mada Walabu University', 'Main Branch'),
        ('2000987654321', 'AWASH', 'Mada Walabu University', 'Finance Branch'),
        ('3000555666777', 'WEGAGEN', 'Mada Walabu University', 'Accounting Branch'),
    ]
    
    for account_num, bank_name, holder, branch in banks:
        bank_account = BankAccount.objects.create(
            account_number=account_num,
            bank_name=bank_name,
            account_holder=holder,
            branch=branch,
            is_active=True
        )
        bank_accounts.append(bank_account)

    # Create bank transactions
    print("Creating bank transactions...")
    for bank_account in bank_accounts:
        for i in range(1, 4):
            BankTransaction.objects.create(
                bank_account=bank_account,
                reference=f'REF{bank_account.id}{i}',
                amount=5000 + i*1000,
                details=f'Cost sharing payment transaction {i}'
            )

    # Create notices
    print("Creating notices...")
    notices = [
        {
            'title': 'Cost Sharing Payment Deadline',
            'content': 'Please be reminded that the cost sharing payment deadline is approaching. Make sure to complete your payments on time.',
            'target_roles': ['student'],
            'expiry_date': timezone.now() + datetime.timedelta(days=30)
        },
        {
            'title': 'System Maintenance',
            'content': 'The system will undergo maintenance this weekend. Please plan accordingly.',
            'target_roles': ['admin'],
            'expiry_date': timezone.now() + datetime.timedelta(days=7)
        },
        {
            'title': 'New Cost Structure',
            'content': 'A new cost structure has been approved for the upcoming academic year.',
            'target_roles': ['cost_sharing_officer'],
            'expiry_date': timezone.now() + datetime.timedelta(days=60)
        },
        {
            'title': 'Payment Verification Training',
            'content': 'Training session for payment verification process will be held next week.',
            'target_roles': ['inland_revenue_officer'],
            'expiry_date': timezone.now() + datetime.timedelta(days=14)
        },
        {
            'title': 'Student Data Upload',
            'content': 'Please upload the student data for the new academic year.',
            'target_roles': ['registrar_officer'],
            'expiry_date': timezone.now() + datetime.timedelta(days=21)
        },
        {
            'title': 'System-wide Announcement',
            'content': 'Important announcement for all users of the system.',
            'target_roles': ['admin', 'student', 'cost_sharing_officer', 'registrar_officer', 'inland_revenue_officer'],
            'expiry_date': timezone.now() + datetime.timedelta(days=90)
        }
    ]

    for notice_data in notices:
        Notice.objects.create(
            title=notice_data['title'],
            content=notice_data['content'],
            posted_by=admin_user,
            target_roles=notice_data['target_roles'],
            audience='all' if len(notice_data['target_roles']) > 1 else 'specific',
            expiry_date=notice_data['expiry_date']
        )

    # Create feedback
    print("Creating feedback...")
    for student in students:
        for i in range(1, 3):
            feedback = Feedback.objects.create(
                student=student,
                subject=f'Feedback {i} from {student.username}',
                message=f'This is feedback message {i} from {student.username}.',
                status='pending'
            )

            # Respond to some feedback
            if i == 1:
                feedback.response = f'Response to feedback {i} from admin.'
                feedback.date_responded = timezone.now()
                feedback.responded_by = admin_user
                feedback.status = 'responded'
                feedback.save()

    print("\n✓ Database populated successfully!")
    print("\nCreated:")
    print(f"  - 1 Admin user")
    print(f"  - 4 Officer users (Cost Sharing, Registrar, Inland Revenue)")
    print(f"  - 5 Student users")
    print(f"  - 5 Cost structures")
    print(f"  - 15 Cost sharing agreements")
    print(f"  - 30 Payments")
    print(f"  - 3 Bank accounts")
    print(f"  - 9 Bank transactions")
    print(f"  - 6 Notices")
    print(f"  - 10 Feedback entries")

if __name__ == '__main__':
    try:
        populate_database()
    except Exception as e:
        print(f"\n✗ Error populating database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
