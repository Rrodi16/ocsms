# OCSMS Features Documentation

## 1. Authentication & Authorization

### Login
- Email/Username and password authentication
- Role-based access control (RBAC)
- Session management
- Forgot password functionality

### User Roles
- **Admin** - Full system access
- **Cost Sharing Officer** - Manage agreements, feedback, notices
- **Inland Revenue Officer** - Verify payments, manage bank accounts
- **Registrar Officer** - Upload student data, generate reports
- **Student** - Fill agreements, make payments

## 2. Cost Sharing Agreement

### Student Features
- Fill cost sharing agreement form
- **Upload photo receipt** (NEW)
- View agreement status
- Print agreement
- Submit feedback

### Cost Officer Features
- View all agreements
- Accept/Reject agreements
- View student feedback
- Post notices
- Export reports

### Agreement Status Flow
1. **Draft** - Student filling form
2. **Submitted** - Waiting for officer review
3. **Accepted** - Student can make payment
4. **Rejected** - Student notified, can resubmit
5. **Completed** - Payment verified

## 3. Payment Management

### Student Payment Process
1. Agreement must be **ACCEPTED** by cost officer
2. Student fills payment form with:
   - Amount
   - Bank account
   - **TIN (Tax Identification Number)** (REQUIRED)
   - Receipt/Proof of payment
3. Payment submitted for verification

### Payment Verification
- Only students with accepted agreements can make payments
- TIN is required for cost sharing repayment tracking
- Receipt must be attached and valid
- Inland revenue officer verifies payment

### Payment Status
- **Pending** - Awaiting verification
- **Verified** - Payment confirmed
- **Rejected** - Invalid receipt/proof
- **Completed** - Fully processed

## 4. Bank Account Management

### Admin Features
- Create bank accounts
- Edit bank account details
- Delete bank accounts
- View all transactions

### Transaction Details Display
- Account number
- Bank name
- Transaction date
- Amount
- Transaction type (Debit/Credit)
- Reference number
- Status

## 5. Notice Management

### Cost Officer & Inland Officer
- Post notices to students
- View all notices
- Edit notices
- Delete notices

### Student
- View all notices
- Filter by date
- Search notices

## 6. Feedback System

### Student
- Submit feedback
- View feedback status
- Track responses

### Cost Officer
- View all feedback
- Respond to feedback
- Mark as resolved

## 7. Student Data Management

### Registrar Officer
- Upload student data (CSV/Excel)
- View uploaded students
- Assign to cost officers
- Generate reports

### Admin
- View all student data
- Edit student information
- Delete students
- Export student lists

## 8. Reporting & Export

### Available Reports
- **Student List** - All students (CSV)
- **Paid Students** - Students who made payments (CSV)
- **Payment Report** - All payments with details (CSV/PDF)
- **Cost Sharing Report** - Agreement statistics (PDF)
- **Bank Transactions** - All bank transactions (CSV)

### Export Formats
- CSV - For spreadsheet analysis
- PDF - For printing/archiving

## 9. Notifications

### Types
- Agreement status changes
- Payment verification results
- New notices
- Feedback responses
- System announcements

### Features
- Real-time notifications
- Mark as read
- Delete notifications
- Notification history

## 10. Dashboard Features

### Student Dashboard
- Agreement status
- Payment history
- Pending actions
- Recent notices
- Feedback status

### Cost Officer Dashboard
- Pending agreements
- Student feedback
- Posted notices
- Export options
- Assigned students

### Inland Officer Dashboard
- Pending payments
- Verified payments
- Bank transactions
- Posted notices
- Payment statistics

### Registrar Dashboard
- Upload student data
- View students
- Generate reports
- Export student lists

### Admin Dashboard
- System statistics
- User management
- Bank account management
- Cost structure management
- System logs

## 11. Photo Upload Feature

### Cost Sharing Agreement
- Upload photo of receipt/proof
- Supported formats: JPG, PNG, PDF
- Maximum file size: 5MB
- Stored in: `/media/receipts/`

### Payment Form
- Upload payment receipt
- Proof of payment required
- Photo validation
- Secure storage

## 12. TIN (Tax Identification Number)

### Purpose
- Cost sharing repayment tracking
- Tax compliance
- Payment verification

### Usage
- Required for all payments
- Validated during payment submission
- Stored with payment record
- Used for reporting

## 13. Data Security

### Features
- Password hashing (bcrypt)
- CSRF protection
- SQL injection prevention
- XSS protection
- File upload validation
- Role-based access control

### Backup
- Regular database backups
- Media file backups
- Version control

## 14. Performance

### Optimization
- Database indexing
- Query optimization
- Pagination (25 items per page)
- Caching
- Lazy loading

### Scalability
- Horizontal scaling ready
- Load balancing support
- Database replication ready
