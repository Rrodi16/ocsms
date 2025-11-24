# OCSMS Quick Start Guide

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git (optional)

### 2. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Fix Database (if corrupted)
\`\`\`bash
python fix_database.py
\`\`\`

### 4. Create Test Users
\`\`\`bash
python create_test_users.py
\`\`\`

### 5. Run Server
\`\`\`bash
python manage.py runserver
\`\`\`

Visit: http://127.0.0.1:8000/

---

## Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Cost Officer | costofficer | costofficer123 |
| Registrar | registrar | registrar123 |
| Inland Revenue Officer | inlandofficer | inlandofficer123 |
| Student | student1 | student123 |

---

## System Features

### Admin Dashboard
- Manage users and roles
- View system statistics
- Manage bank accounts
- View all agreements and payments

### Cost Officer Dashboard
- Review pending agreements
- Accept or reject agreements
- Manage cost structures
- View student data

### Registrar Dashboard
- Upload student data via CSV
- View uploaded students
- Download student lists

### Inland Revenue Officer Dashboard
- View payment status
- Verify payments
- Manage bank accounts
- Download payment reports

### Student Dashboard
- Submit cost sharing agreements
- Make payments with receipt upload
- View payment history
- Submit feedback

---

## Common Tasks

### Upload Student Data (Registrar)
1. Login as registrar
2. Go to Dashboard → Upload Student Data
3. Select CSV file with student information
4. Click Upload

### Accept Agreement (Cost Officer)
1. Login as cost officer
2. Go to Dashboard → Pending Agreements
3. Click Accept or Reject
4. Student receives notification

### Make Payment (Student)
1. Login as student
2. Go to Dashboard → Make Payment
3. Select agreement
4. Enter amount and TIN
5. Upload receipt
6. Submit for verification

### Verify Payment (Inland Revenue Officer)
1. Login as inland revenue officer
2. Go to Dashboard → Pending Payments
3. Review payment details
4. Click Verify or Reject
5. Student receives notification

---

## Troubleshooting

### Database Error
\`\`\`bash
python fix_database.py
\`\`\`

### Port Already in Use
\`\`\`bash
python manage.py runserver 8001
\`\`\`

### Missing Dependencies
\`\`\`bash
pip install -r requirements.txt --upgrade
\`\`\`

### Clear All Data
1. Login as admin
2. Go to Dashboard → Clear All Data
3. Confirm deletion

---

## Next Steps

1. **Customize Settings**: Edit `ocsms/ocsms/settings.py`
2. **Add More Users**: Use admin dashboard
3. **Configure Email**: Set up email notifications
4. **Deploy**: Follow deployment guide for production

---

## Support

For detailed information, see:
- DATABASE_MIGRATION_GUIDE.md - Database setup and migration
- SETUP_INSTRUCTIONS.md - Detailed setup instructions
