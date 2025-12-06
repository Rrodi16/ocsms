# OCSMS - Quick Start Guide

## Prerequisites
- Python 3.8+
- Django 4.0+
- All dependencies installed

## Complete Setup (Recommended)

Run this single command to set up everything:

\`\`\`bash
python setup.py
\`\`\`

This will:
1. ✓ Run all database migrations
2. ✓ Create test users for each dashboard
3. ✓ Create sample data (cost structures, bank accounts)
4. ✓ Display login credentials

## Manual Setup (If needed)

If you prefer to run steps individually:

### Step 1: Run Migrations
\`\`\`bash
python manage.py migrate
\`\`\`

### Step 2: Create Test Users
\`\`\`bash
python create_test_users.py
\`\`\`

### Step 3: Create Sample Data
\`\`\`bash
python populate_db.py
\`\`\`

## Test User Credentials

After setup, login with these credentials:

| Dashboard | Username | Password |
|-----------|----------|----------|
| Admin | admin | admin123 |
| Cost Officer | costofficer | costofficer123 |
| Registrar | registrar | registrar123 |
| Inland Revenue Officer | inlandofficer | inlandofficer123 |
| Student | student1 | student123 |

## Start the Server

\`\`\`bash
python manage.py runserver
\`\`\`

Then open: http://localhost:8000

## Troubleshooting

### Error: "no such table: cost_sharing_user"
**Solution:** Run migrations first
\`\`\`bash
python manage.py migrate
\`\`\`

### Error: "database disk image is malformed"
**Solution:** Delete the corrupted database and run setup again
\`\`\`bash
rm db.sqlite3
python setup.py
\`\`\`

### Error: "ModuleNotFoundError"
**Solution:** Make sure you're in the correct directory and Django is installed
\`\`\`bash
cd ocsms
pip install -r requirements.txt
python setup.py
\`\`\`

## Next Steps

1. Login to each dashboard to verify everything works
2. Create cost structures in the Cost Officer dashboard
3. Upload student data through the Registrar dashboard
4. Create agreements and process payments

For more information, see the full documentation in the project root.
