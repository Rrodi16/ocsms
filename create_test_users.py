#!/usr/bin/env python
"""
Quick script to create test users for each dashboard role.
Run this after running: python manage.py migrate
"""

import os
import sys
import django

# Django setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_users():
    print("Creating test users for each dashboard...\n")

    test_users = [
        {
            'username': 'rodas',
            'email': 'rodas@mau.edu.et',
            'password': 'rodas123',
            'first_name': 'Rodas',
            'last_name': 'Dilnesa',
            'role': 'admin',
            'is_superuser': True,
            'is_staff': True,
        },
        {
            'username': 'muluken',
            'email': 'muluken@mau.edu.et',
            'password': 'muluken123',
            'first_name': 'Muluken',
            'last_name': 'Semagn',
            'role': 'cost_sharing_officer',
            'is_superuser': False,
            'is_staff': False,
        },
        {
            'username': 'habtamu',
            'email': 'habtamu@mau.edu.et',
            'password': 'habtamu123',
            'first_name': 'Habtamu',
            'last_name': 'Abebaw',
            'role': 'registrar_officer',
            'is_superuser': False,
            'is_staff': False,
        },
        {
            'username': 'tigist',
            'email': 'tigist@mau.edu.et',
            'password': 'tigist123',
            'first_name': 'Tigist',
            'last_name': 'Alemayehu',
            'role': 'inland_revenue_officer',
            'is_superuser': False,
            'is_staff': False,
        },
        {
            'username': 'rodi',
            'email': 'rodi@mau.edu.et',
            'password': 'rodi123',
            'first_name': 'Rodi',
            'last_name': 'Arega',
            'role': 'student',
            'is_superuser': False,
            'is_staff': False,
            'student_id': 'STU001',
            'department': 'Computer Science',
            'year_of_study': 2,
        },
    ]

    created_count = 0
    for user_data in test_users:
        username = user_data['username']

        if User.objects.filter(username=username).exists():
            print(f"⚠ User '{username}' already exists, skipping...")
            continue

        password = user_data.pop('password')
        if user_data.get('is_superuser'):
            user = User.objects.create_superuser(**user_data)
        else:
            user = User.objects.create_user(**user_data, password=password)

        created_count += 1
        print(f"✓ Created {user_data['role']} user: {username}")
        print(f"  Email: {user_data['email']}")
        print(f"  Password: {password}\n")

    if created_count == 0:
        print("No new users created. All test users already exist.")
    else:
        print(f"\n✓ Successfully created {created_count} test user(s)!")

    print("\n" + "=" * 60)
    print("TEST USER CREDENTIALS")
    print("=" * 60)
    print("\n1. ADMIN DASHBOARD")
    print("   Username: rodas")
    print("   Password: rodas123")
    print("\n2. COST OFFICER DASHBOARD")
    print("   Username: muluken")
    print("   Password: muluken123")
    print("\n3. REGISTRAR DASHBOARD")
    print("   Username: habtamu")
    print("   Password: habtamu123")
    print("\n4. INLAND REVENUE OFFICER DASHBOARD")
    print("   Username: tigist")
    print("   Password: tigist123")
    print("\n5. STUDENT DASHBOARD")
    print("   Username: rodi")
    print("   Password: rodi123")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"\n✗ Error creating test users: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
