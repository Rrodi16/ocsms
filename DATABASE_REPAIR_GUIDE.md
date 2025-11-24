# OCSMS Database Repair Guide

## Problem: "database disk image is malformed"

This error occurs when the SQLite database file becomes corrupted. This can happen due to:
- Unexpected server shutdown
- Disk space issues
- File system errors
- Concurrent access issues

## Solution: Automatic Database Repair

### Step 1: Run the Repair Script

\`\`\`bash
python repair_database.py
\`\`\`

The script will:
1. ✓ Backup your corrupted database (with timestamp)
2. ✓ Delete the corrupted database file
3. ✓ Clean Python cache files
4. ✓ Remove old migration files
5. ✓ Create fresh migrations
6. ✓ Apply migrations to create new database
7. ✓ Verify the database was created correctly

### Step 2: Populate Sample Data (Optional)

If you want to populate the database with sample data for testing:

\`\`\`bash
python populate_db.py
\`\`\`

This creates:
- 1 Admin user (admin/admin123)
- 4 Officer users (cost officer, registrar, inland revenue)
- 5 Student users (student1-5)
- Sample cost structures, agreements, payments, and notices

### Step 3: Start the Server

\`\`\`bash
python manage.py runserver
\`\`\`

Then visit: http://localhost:8000

### Default Login Credentials

After running `populate_db.py`:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Cost Officer | csofficer | csofficer123 |
| Registrar | regofficer | regofficer123 |
| Inland Revenue | irofficer | irofficer123 |
| Student 1 | student1 | student1 |
| Student 2 | student2 | student2 |
| Student 3 | student3 | student3 |
| Student 4 | student4 | student4 |
| Student 5 | student5 | student5 |

## Troubleshooting

### If the repair script fails:

1. **Check Python version**: Ensure you're using Python 3.8+
   \`\`\`bash
   python --version
   \`\`\`

2. **Check Django installation**:
   \`\`\`bash
   pip install django
   \`\`\`

3. **Check database file permissions**:
   \`\`\`bash
   # On Linux/Mac
   ls -la db.sqlite3
   
   # On Windows
   dir db.sqlite3
   \`\`\`

4. **Manual repair** (if script fails):
   \`\`\`bash
   # Delete the corrupted database
   rm db.sqlite3  # Linux/Mac
   del db.sqlite3  # Windows
   
   # Create fresh migrations
   python manage.py makemigrations cost_sharing
   
   # Apply migrations
   python manage.py migrate
   \`\`\`

### If migrations fail:

1. Delete all migration files except `__init__.py`:
   \`\`\`bash
   rm cost_sharing/migrations/000*.py
   \`\`\`

2. Clear Python cache:
   \`\`\`bash
   find . -type d -name __pycache__ -exec rm -r {} +  # Linux/Mac
   \`\`\`

3. Recreate migrations:
   \`\`\`bash
   python manage.py makemigrations cost_sharing
   python manage.py migrate
   \`\`\`

## Backup Location

Your corrupted database is backed up as:
\`\`\`
db.sqlite3.backup.YYYYMMDD_HHMMSS
\`\`\`

Keep this file safe in case you need to recover any data.

## Prevention

To prevent database corruption:

1. **Always shut down properly**: Use Ctrl+C to stop the server
2. **Monitor disk space**: Ensure sufficient disk space
3. **Regular backups**: Backup your database regularly
4. **Use production database**: For production, use PostgreSQL instead of SQLite

## Need Help?

If you continue to experience issues:

1. Check the error message carefully
2. Review the troubleshooting section above
3. Ensure all dependencies are installed
4. Try the manual repair steps
5. Contact your system administrator

---

**Last Updated**: 2025-10-18
**Version**: 1.0
