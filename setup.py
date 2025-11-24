#!/usr/bin/env python
"""
Complete setup script for OCSMS
Runs migrations, creates test users, and populates sample data
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')
sys.path.insert(0, str(Path(__file__).parent / 'ocsms'))

django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from cost_sharing.models import CostStructure, Agreement, Payment, BankAccount

User = get_user_model()

def run_migrations():
    """Run all pending migrations"""
    print("\n" + "="*60)
    print("STEP 1: Running Database Migrations")
    print("="*60)
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        return False

def create_test_users():
    """Create one test user for each dashboard"""
    print("\n" + "="*60)
    print("STEP 2: Creating Test Users")
    print("="*60)
    
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@ocsms.local',
            'password': 'admin123',
            'role': 'admin',
            'first_name': 'Admin',
            'last_name': 'User'
        },
        {
            'username': 'costofficer',
            'email': 'costofficer@ocsms.local',
            'password': 'costofficer123',
            'role': 'cost_sharing_officer',
            'first_name': 'Cost',
            'last_name': 'Officer'
        },
        {
            'username': 'registrar',
            'email': 'registrar@ocsms.local',
            'password': 'registrar123',
            'role': 'registrar_officer',
            'first_name': 'Registrar',
            'last_name': 'Officer'
        },
        {
            'username': 'inlandofficer',
            'email': 'inlandofficer@ocsms.local',
            'password': 'inlandofficer123',
            'role': 'inland_revenue_officer',
            'first_name': 'Inland',
            'last_name': 'Officer'
        },
        {
            'username': 'student1',
            'email': 'student1@ocsms.local',
            'password': 'student123',
            'role': 'student',
            'first_name': 'John',
            'last_name': 'Student'
        }
    ]
    
    created_count = 0
    for user_data in users_data:
        username = user_data['username']
        if User.objects.filter(username=username).exists():
            print(f"  ⊘ User '{username}' already exists")
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                print(f"  ✓ Created user: {username} ({user_data['role']})")
                created_count += 1
            except Exception as e:
                print(f"  ✗ Failed to create {username}: {str(e)}")
    
    print(f"\n✓ Test users setup complete ({created_count} new users created)")
    return True

def create_sample_data():
    """Create sample cost structures and agreements"""
    print("\n" + "="*60)
    print("STEP 3: Creating Sample Data")
    print("="*60)
    
    try:
        # Create cost structure if it doesn't exist
        if not CostStructure.objects.exists():
            cost_structure = CostStructure.objects.create(
                name='2024/2025 Cost Sharing',
                description='Cost sharing structure for academic year 2024/2025',
                total_cost=50000,
                student_contribution=25000,
                government_contribution=25000,
                status='active'
            )
            print(f"  ✓ Created cost structure: {cost_structure.name}")
        else:
            print("  ⊘ Cost structure already exists")
        
        # Create sample bank account
        if not BankAccount.objects.exists():
            bank_account = BankAccount.objects.create(
                bank_name='National Bank',
                account_number='1234567890',
                account_holder='OCSMS',
                balance=0
            )
            print(f"  ✓ Created bank account: {bank_account.bank_name}")
        else:
            print("  ⊘ Bank account already exists")
        
        print("\n✓ Sample data created successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to create sample data: {str(e)}")
        return False

def print_credentials():
    """Print test user credentials"""
    print("\n" + "="*60)
    print("TEST USER CREDENTIALS")
    print("="*60)
    print("\nYou can now login with these credentials:\n")
    
    credentials = [
        ("Admin Dashboard", "admin", "admin123"),
        ("Cost Officer Dashboard", "costofficer", "costofficer123"),
        ("Registrar Dashboard", "registrar", "registrar123"),
        ("Inland Revenue Officer Dashboard", "inlandofficer", "inlandofficer123"),
        ("Student Dashboard", "student1", "student123"),
    ]
    
    for dashboard, username, password in credentials:
        print(f"  {dashboard}")
        print(f"    Username: {username}")
        print(f"    Password: {password}\n")

def main():
    """Run complete setup"""
    print("\n" + "="*60)
    print("OCSMS - Complete Setup Script")
    print("="*60)
    
    # Step 1: Run migrations
    if not run_migrations():
        print("\n✗ Setup failed at migration step")
        sys.exit(1)
    
    # Step 2: Create test users
    if not create_test_users():
        print("\n✗ Setup failed at user creation step")
        sys.exit(1)
    
    # Step 3: Create sample data
    if not create_sample_data():
        print("\n✗ Setup failed at sample data creation step")
        sys.exit(1)
    
    # Print credentials
    print_credentials()
    
    print("="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Run: python manage.py runserver")
    print("  2. Open: http://localhost:8000")
    print("  3. Login with any of the credentials above")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
