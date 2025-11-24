#!/usr/bin/env python
"""
OCSMS Database Repair Script
Fixes corrupted SQLite database and recreates schema
Run this script when you encounter: "database disk image is malformed"
"""
import os
import sys
import django
import shutil
from pathlib import Path
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(step_num, text):
    """Print formatted step"""
    print(f"[Step {step_num}] {text}")

def print_success(text):
    """Print success message"""
    print(f"  ✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"  ✗ {text}")

def backup_corrupted_db():
    """Create a backup of the corrupted database"""
    db_path = Path('db.sqlite3')
    if db_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = Path(f'db.sqlite3.backup.{timestamp}')
        try:
            shutil.copy2(db_path, backup_path)
            print_success(f"Corrupted database backed up to: {backup_path}")
            return True
        except Exception as e:
            print_error(f"Failed to backup database: {e}")
            return False
    return True

def delete_database():
    """Delete the corrupted database file"""
    db_path = Path('db.sqlite3')
    if db_path.exists():
        try:
            db_path.unlink()
            print_success("Corrupted database file deleted")
            return True
        except Exception as e:
            print_error(f"Failed to delete database: {e}")
            return False
    return True

def delete_pycache():
    """Delete __pycache__ directories to avoid stale bytecode"""
    pycache_dirs = list(Path('.').rglob('__pycache__'))
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print_success(f"Deleted cache: {pycache_dir}")
        except Exception as e:
            print_error(f"Failed to delete {pycache_dir}: {e}")

def delete_migrations():
    """Delete migration files to start fresh"""
    migrations_dir = Path('cost_sharing/migrations')
    if migrations_dir.exists():
        for file in migrations_dir.glob('*.py'):
            if file.name != '__init__.py':
                try:
                    file.unlink()
                    print_success(f"Deleted migration: {file.name}")
                except Exception as e:
                    print_error(f"Failed to delete {file.name}: {e}")

def setup_django():
    """Setup Django"""
    try:
        django.setup()
        print_success("Django setup completed")
        return True
    except Exception as e:
        print_error(f"Failed to setup Django: {e}")
        return False

def create_migrations():
    """Create new migrations"""
    try:
        from django.core.management import call_command
        call_command('makemigrations', 'cost_sharing', verbosity=1)
        print_success("Migrations created successfully")
        return True
    except Exception as e:
        print_error(f"Failed to create migrations: {e}")
        import traceback
        traceback.print_exc()
        return False

def apply_migrations():
    """Apply migrations"""
    try:
        from django.core.management import call_command
        call_command('migrate', verbosity=1)
        print_success("Migrations applied successfully")
        return True
    except Exception as e:
        print_error(f"Failed to apply migrations: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_database():
    """Verify database was created correctly"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            expected_tables = [
                'cost_sharing_user',
                'cost_sharing_coststructure',
                'cost_sharing_costsharingagreement',
                'cost_sharing_payment',
                'cost_sharing_notice',
                'cost_sharing_feedback',
                'cost_sharing_studentdata',
                'cost_sharing_bankaccount',
                'cost_sharing_notification',
                'cost_sharing_agreement',
                'cost_sharing_banktransaction',
            ]
            
            print_success(f"Database tables created: {len(table_names)} tables")
            for table in table_names:
                print(f"    - {table}")
            
            missing = set(expected_tables) - set(table_names)
            if missing:
                print_error(f"Missing tables: {missing}")
                return False
            
            return True
    except Exception as e:
        print_error(f"Failed to verify database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main repair process"""
    print_header("OCSMS DATABASE REPAIR TOOL")
    print("This script will fix your corrupted SQLite database.")
    print("A backup of the corrupted database will be created.\n")
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("\nRepair cancelled.")
        return False
    
    print_header("Starting Database Repair")
    
    # Step 1: Backup
    print_step(1, "Backing up corrupted database...")
    if not backup_corrupted_db():
        print_error("Backup failed. Aborting.")
        return False
    
    # Step 2: Delete corrupted database
    print_step(2, "Deleting corrupted database...")
    if not delete_database():
        print_error("Failed to delete database. Aborting.")
        return False
    
    # Step 3: Clean cache
    print_step(3, "Cleaning Python cache...")
    delete_pycache()
    
    # Step 4: Delete old migrations
    print_step(4, "Cleaning old migrations...")
    delete_migrations()
    
    # Step 5: Setup Django
    print_step(5, "Setting up Django...")
    if not setup_django():
        print_error("Django setup failed. Aborting.")
        return False
    
    # Step 6: Create migrations
    print_step(6, "Creating new migrations...")
    if not create_migrations():
        print_error("Migration creation failed. Aborting.")
        return False
    
    # Step 7: Apply migrations
    print_step(7, "Applying migrations...")
    if not apply_migrations():
        print_error("Migration application failed. Aborting.")
        return False
    
    # Step 8: Verify database
    print_step(8, "Verifying database...")
    if not verify_database():
        print_error("Database verification failed.")
        return False
    
    print_header("✓ DATABASE REPAIR COMPLETED SUCCESSFULLY!")
    print("Next steps:")
    print("  1. Run: python populate_db.py")
    print("     (to populate the database with sample data)")
    print("  2. Run: python manage.py runserver")
    print("     (to start the development server)")
    print("  3. Login with credentials:")
    print("     - Username: admin")
    print("     - Password: admin123")
    print("\n")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nRepair cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_header("✗ FATAL ERROR")
        print_error(str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
