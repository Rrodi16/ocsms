# OCSMS API Documentation

## Base URL
\`\`\`
http://localhost:8000
\`\`\`

## Authentication
All endpoints require authentication except login/register.

### Login
\`\`\`
POST /login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "token": "auth_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "student"
  }
}
\`\`\`

## Student Endpoints

### Cost Sharing Agreement

#### Fill Agreement
\`\`\`
POST /fill-cost-sharing/
Content-Type: multipart/form-data

{
  "student_id": 1,
  "amount": 50000,
  "photo_receipt": <file>,
  "bank_account": 1,
  "notes": "..."
}
\`\`\`

#### View Agreement
\`\`\`
GET /view-cost-sharing/<id>/
\`\`\`

#### View All Agreements
\`\`\`
GET /agreement/
\`\`\`

### Payment

#### Make Payment
\`\`\`
POST /make-payment/
Content-Type: multipart/form-data

{
  "agreement_id": 1,
  "amount": 50000,
  "tin": "1234567890",
  "bank_account": 1,
  "receipt": <file>
}

Response:
{
  "id": 1,
  "status": "pending",
  "amount": 50000,
  "date_paid": "2025-01-15"
}
\`\`\`

#### Payment History
\`\`\`
GET /payment-history/
\`\`\`

#### Payment Receipt
\`\`\`
GET /payment-receipt/<id>/
\`\`\`

### Feedback

#### Submit Feedback
\`\`\`
POST /submit-feedback/
Content-Type: application/json

{
  "subject": "...",
  "message": "...",
  "category": "general"
}
\`\`\`

## Cost Officer Endpoints

### Agreements

#### View Agreements
\`\`\`
GET /officer/agreements/
\`\`\`

#### Accept Agreement
\`\`\`
POST /agreement/<id>/set/accepted/
\`\`\`

#### Reject Agreement
\`\`\`
POST /agreement/<id>/set/rejected/
\`\`\`

### Feedback

#### View Feedback
\`\`\`
GET /view-feedback/
\`\`\`

#### Respond to Feedback
\`\`\`
POST /respond-feedback/<id>/
Content-Type: application/json

{
  "response": "..."
}
\`\`\`

### Notices

#### Post Notice
\`\`\`
POST /post-notice/
Content-Type: application/json

{
  "title": "...",
  "content": "...",
  "target_audience": "all"
}
\`\`\`

### Reports

#### Export Students
\`\`\`
GET /export/students.csv
\`\`\`

#### Export Paid Students
\`\`\`
GET /export/paid_students.csv
\`\`\`

#### Generate Report
\`\`\`
GET /generate-report/
\`\`\`

## Inland Revenue Officer Endpoints

### Payments

#### View Payments
\`\`\`
GET /manage-payments/
\`\`\`

#### Verify Payment
\`\`\`
POST /verify-payment/<id>/
Content-Type: application/json

{
  "status": "verified"
}
\`\`\`

#### Payment Status
\`\`\`
GET /view-payment-status/
\`\`\`

### Bank Accounts

#### View Bank Transactions
\`\`\`
GET /bank-account/<id>/transactions/
\`\`\`

### Notices

#### Post Notice
\`\`\`
POST /post-notice/
Content-Type: application/json

{
  "title": "...",
  "content": "..."
}
\`\`\`

## Registrar Officer Endpoints

### Student Data

#### Upload Students
\`\`\`
POST /upload-student-data/
Content-Type: multipart/form-data

{
  "file": <csv_or_excel_file>
}
\`\`\`

#### View Students
\`\`\`
GET /registrar/students/
\`\`\`

#### Generate Report
\`\`\`
GET /registrar/reports/
\`\`\`

## Admin Endpoints

### Users

#### Create User
\`\`\`
POST /create-user/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "role": "student",
  "first_name": "John",
  "last_name": "Doe"
}
\`\`\`

#### Manage Users
\`\`\`
GET /manage-users/
\`\`\`

#### Edit User
\`\`\`
PUT /edit-user/<id>/
\`\`\`

#### Delete User
\`\`\`
DELETE /delete-user/<id>/
\`\`\`

### Bank Accounts

#### Create Bank Account
\`\`\`
POST /manage-bank-accounts/
Content-Type: application/json

{
  "bank_name": "...",
  "account_number": "...",
  "account_holder": "..."
}
\`\`\`

#### View Bank Accounts
\`\`\`
GET /view-bank-accounts/
\`\`\`

#### Edit Bank Account
\`\`\`
PUT /edit-bank-account/<id>/
\`\`\`

#### Delete Bank Account
\`\`\`
DELETE /delete-bank-account/<id>/
\`\`\`

## Error Responses

### 400 Bad Request
\`\`\`json
{
  "error": "Invalid request data",
  "details": {...}
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "error": "Authentication required"
}
\`\`\`

### 403 Forbidden
\`\`\`json
{
  "error": "Permission denied"
}
\`\`\`

### 404 Not Found
\`\`\`json
{
  "error": "Resource not found"
}
\`\`\`

### 500 Server Error
\`\`\`json
{
  "error": "Internal server error"
}
