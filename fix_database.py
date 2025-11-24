#!/usr/bin/env python
"""
Database repair and reset script for OCSMS
Handles corrupted SQLite database and recreates it with proper schema
"""
import os
import sys
import django
import shutil
from pathlib import Path

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')

# Configure Django before importing models
django.setup()

from django.core.management import call_command
from django.db import connection

def backup_corrupted_db():
    """Create a backup of the corrupted database"""
    db_path = Path('db.sqlite3')
    if db_path.exists():
        backup_path = Path(f'db.sqlite3.backup.{os.urandom(4).hex()}')
        shutil.copy2(db_path, backup_path)
        print(f"✓ Corrupted database backed up to: {backup_path}")
        return True
    return False

def delete_database():
    """Delete the corrupted database file"""
    db_path = Path('db.sqlite3')
    if db_path.exists():
        try:
            db_path.unlink()
            print("✓ Corrupted database file deleted")
            return True
        except Exception as e:
            print(f"✗ Error deleting database: {e}")
            return False
    return True

def delete_migrations():
    """Delete migration files to start fresh"""
    migrations_dir = Path('cost_sharing/migrations')
    if migrations_dir.exists():
        # Keep __init__.py but delete other migration files
        for file in migrations_dir.glob('*.py'):
            if file.name != '__init__.py':
                try:
                    file.unlink()
                    print(f"✓ Deleted migration: {file.name}")
                except Exception as e:
                    print(f"✗ Error deleting {file.name}: {e}")

def reset_database():
    """Reset the database completely"""
    print("\n" + "="*60)
    print("OCSMS DATABASE REPAIR AND RESET")
    print("="*60 + "\n")
    
    # Step 1: Backup corrupted database
    print("Step 1: Backing up corrupted database...")
    backup_corrupted_db()
    
    # Step 2: Delete corrupted database
    print("\nStep 2: Deleting corrupted database...")
    if not delete_database():
        print("✗ Failed to delete database. Exiting.")
        return False
    
    # Step 3: Delete old migrations
    print("\nStep 3: Cleaning up old migrations...")
    delete_migrations()
    
    # Step 4: Create new migrations
    print("\nStep 4: Creating new migrations...")
    try:
        call_command('makemigrations', 'cost_sharing', verbosity=1)
        print("✓ Migrations created successfully")
    except Exception as e:
        print(f"✗ Error creating migrations: {e}")
        return False
    
    # Step 5: Apply migrations
    print("\nStep 5: Applying migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Migrations applied successfully")
    except Exception as e:
        print(f"✗ Error applying migrations: {e}")
        return False
    
    # Step 6: Verify database
    print("\nStep 6: Verifying database...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            print(f"✓ Database tables created: {', '.join(table_names)}")
    except Exception as e:
        print(f"✗ Error verifying database: {e}")
        return False
    
    print("\n" + "="*60)
    print("✓ DATABASE RESET SUCCESSFULLY!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python populate_db.py (to add sample data)")
    print("2. Run: python manage.py runserver (to start the server)")
    print("\n")
    
    return True

if __name__ == '__main__':
    try:
        success = reset_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
