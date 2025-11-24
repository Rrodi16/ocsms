# OCSMS Database Schema

## User Model
\`\`\`
- id (PK)
- email (unique)
- password (hashed)
- first_name
- last_name
- role (admin, cost_officer, inland_officer, registrar, student)
- is_active
- is_staff
- created_at
- updated_at
\`\`\`

## CostSharingAgreement Model
\`\`\`
- id (PK)
- student (FK -> User)
- amount
- status (draft, submitted, accepted, rejected, completed)
- photo_receipt (ImageField) ← NEW
- bank_account (FK -> BankAccount)
- notes
- created_at
- updated_at
- accepted_at
- rejected_at
\`\`\`

## Payment Model
\`\`\`
- id (PK)
- agreement (FK -> CostSharingAgreement)
- student (FK -> User)
- amount
- tin (CharField) ← NEW
- bank_account (FK -> BankAccount)
- receipt (FileField)
- status (pending, verified, rejected, completed)
- date_paid
- verified_by (FK -> User)
- verified_at
- created_at
- updated_at
\`\`\`

## BankAccount Model
\`\`\`
- id (PK)
- bank_name
- account_number
- account_holder
- branch
- is_active
- created_at
- updated_at
\`\`\`

## CostStructure Model
\`\`\`
- id (PK)
- name
- amount
- description
- academic_year
- created_at
- updated_at
\`\`\`

## Notice Model
\`\`\`
- id (PK)
- title
- content
- posted_by (FK -> User)
- target_audience (all, students, officers)
- created_at
- updated_at
\`\`\`

## Feedback Model
\`\`\`
- id (PK)
- student (FK -> User)
- subject
- message
- category
- response
- responded_by (FK -> User)
- status (open, responded, closed)
- created_at
- updated_at
\`\`\`

## StudentData Model
\`\`\`
- id (PK)
- student_id
- first_name
- last_name
- email
- phone
- registration_number
- program
- assigned_to (FK -> User)
- is_graduate
- created_at
- updated_at
\`\`\`

## Notification Model
\`\`\`
- id (PK)
- user (FK -> User)
- title
- message
- type (agreement, payment, notice, feedback)
- is_read
- created_at
- read_at
\`\`\`

## Indexes
- User.email
- CostSharingAgreement.student
- CostSharingAgreement.status
- Payment.student
- Payment.status
- Payment.agreement
- StudentData.student_id
- Notification.user
- Notification.is_read
\`\`\`

\`\`\`plaintext file=".env.example"
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
# SQLite (default)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (uncomment to use)
# DATABASE_URL=postgresql://user:password@localhost:5432/ocsms_db

# MySQL (uncomment to use)
# DATABASE_URL=mysql://user:password@localhost:3306/ocsms_db

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Upload
MAX_UPLOAD_SIZE=5242880  # 5MB in bytes
MEDIA_ROOT=media
MEDIA_URL=/media/

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=OCSMS
NEXT_PUBLIC_APP_VERSION=1.0.0
