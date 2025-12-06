# OCSMS Setup Instructions

## Quick Start Guide

Follow these steps to set up and run the OCSMS system:

### 1. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Run Database Migrations
\`\`\`bash
python manage.py migrate
\`\`\`

### 3. Create Test Users
\`\`\`bash
python create_test_users.py
\`\`\`

This will create 5 test users - one for each dashboard:

| Dashboard | Username | Password | Role |
|-----------|----------|----------|------|
| Admin | admin | admin123 | Admin |
| Cost Officer | costofficer | costofficer123 | Cost Sharing Officer |
| Registrar | registrar | registrar123 | Registrar Officer |
| Inland Revenue Officer | inlandofficer | inlandofficer123 | Inland Revenue Officer |
| Student | student1 | student123 | Student |

### 4. (Optional) Populate Sample Data
\`\`\`bash
python populate_db.py
\`\`\`

This will create sample data including:
- 5 students with agreements
- Cost structures
- Payments
- Bank accounts
- Notices
- Feedback

### 5. Run the Development Server
\`\`\`bash
python manage.py runserver
\`\`\`

The application will be available at: `http://localhost:8000`

### 6. Login and Test Each Dashboard

1. **Admin Dashboard**: Login with `admin` / `admin123`
2. **Cost Officer Dashboard**: Login with `costofficer` / `costofficer123`
3. **Registrar Dashboard**: Login with `registrar` / `registrar123`
4. **Inland Revenue Officer Dashboard**: Login with `inlandofficer` / `inlandofficer123`
5. **Student Dashboard**: Login with `student1` / `student123`

## Troubleshooting

### "Template does not exist" Error
- Make sure all migrations have been run: `python manage.py migrate`
- Verify that the templates directory exists in the project root
- Check that `TEMPLATES` is properly configured in `settings.py`

### Database Errors
- Delete the `db.sqlite3` file and run migrations again
- Run `python manage.py migrate --run-syncdb` if needed

### User Creation Issues
- Make sure the User model has the `role` field
- Run migrations if you get "column does not exist" errors
- Check that `create_test_users.py` is in the project root directory

## System Architecture

### User Roles

1. **Admin** - System administrator with full access
2. **Cost Officer** - Manages cost structures and approves agreements
3. **Registrar Officer** - Uploads and manages student data
4. **Inland Revenue Officer** - Verifies and tracks payments
5. **Student** - Views agreements and makes payments

### Key Features

- **Cost Sharing Agreements** - Students fill out agreements with personal and educational information
- **Payment Management** - Students make payments with receipt uploads and TIN validation
- **Cost Structures** - Cost officers manage education, food, and dormitory costs
- **Student Data** - Registrar uploads student information
- **Payment Verification** - Inland revenue officers verify and track payments
- **Notices** - System-wide announcements for specific roles or all users

## Database Schema

The system uses Django ORM with the following main models:
- `User` - Extended Django user with role field
- `CostSharingAgreement` - Student agreements with cost details
- `Payment` - Payment records with verification status
- `CostStructure` - Cost breakdown by department and year
- `StudentData` - Student information uploaded by registrar
- `BankAccount` - Bank account information for payments
- `Notice` - System announcements
- `Notification` - User notifications

## Support

For issues or questions, check the error logs and ensure all migrations have been applied.
