# reset_db.py
import os
import sys
import django
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocsms.settings')
django.setup()

from django.core.management import execute_from_command_line
<<<<<<< HEAD
=======
#This imports Django’s database connection object
>>>>>>> 3d8e1befccba76e3fcdcd0446002701cbcd2422a
from django.db import connection

def reset_database():
    print("Resetting database...")
    
    # Delete the database file if it exists
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("Database file deleted.")
    
    # Create migrations
    print("Creating migrations...")
    execute_from_command_line(['manage.py', 'makemigrations', 'cost_sharing'])
    
    # Apply migrations
    print("Applying migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Check if tables were created
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
    
    print("Database reset successfully!")

if __name__ == '__main__':
    reset_database()
