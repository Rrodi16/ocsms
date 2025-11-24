# OCSMS - Online Cost Sharing Management System
## Organized Project Structure

\`\`\`
ocsms/
├── backend/                          # Django Backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3
│   │
│   ├── ocsms/                        # Main Django Project
│   │   ├── __init__.py
│   │   ├── settings.py               # Django settings
│   │   ├── urls.py                   # Main URL routing
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── cost_sharing/                 # Main App
│   │   ├── migrations/               # Database migrations
│   │   ├── management/
│   │   │   └── commands/
│   │   ├── models.py                 # Database models
│   │   ├── views.py                  # View logic
│   │   ├── forms.py                  # Form definitions
│   │   ├── urls.py                   # App URL routing
│   │   ├── admin.py                  # Admin configuration
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   └── static/
│   │       └── cost_sharing/
│   │           ├── css/
│   │           │   └── style.css
│   │           └── js/
│   │               └── main.js
│   │
│   ├── accounts/                     # User Management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── forms.py
│   │   └── urls.py
│   │
│   ├── templates/                    # Django Templates (Legacy)
│   │   ├── base.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── forgot_password.html
│   │   │   └── reset_password.html
│   │   ├── dashboards/
│   │   │   ├── dashboard_admin.html
│   │   │   ├── dashboard_cost_sharing_officer.html
│   │   │   ├── dashboard_inland_revenue_officer.html
│   │   │   ├── dashboard_registrar_officer.html
│   │   │   └── dashboard_student.html
│   │   ├── student/
│   │   │   ├── fill_cost_sharing.html
│   │   │   ├── view_cost_sharing.html
│   │   │   ├── make_payment.html
│   │   │   └── payment_history.html
│   │   ├── officer/
│   │   │   ├── manage_cost_structure.html
│   │   │   ├── view_students.html
│   │   │   ├── manage_payments.html
│   │   │   └── verify_payment.html
│   │   ├── inland/
│   │   │   ├── bank_accounts.html
│   │   │   ├── payments.html
│   │   │   └── post_notice.html
│   │   ├── registrar/
│   │   │   ├── upload_student_data.html
│   │   │   ├── view_students.html
│   │   │   └── reports.html
│   │   ├── notices/
│   │   │   ├── post_notice.html
│   │   │   └── view_notices.html
│   │   ├── feedback/
│   │   │   ├── submit_feedback.html
│   │   │   └── view_feedback.html
│   │   └── admin/
│   │       ├── manage_users.html
│   │       ├── manage_bank_accounts.html
│   │       └── cost_structure.html
│   │
│   └── media/                        # User Uploaded Files
│       └── receipts/                 # Payment receipts & photos
│
├── frontend/                         # Next.js Frontend (React)
│   ├── app/
│   │   ├── layout.tsx                # Root layout
│   │   ├── page.tsx                  # Home page
│   │   ├── globals.css               # Global styles
│   │   │
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── forgot-password/
│   │   │   │   └── page.tsx
│   │   │   └── reset-password/
│   │   │       └── page.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── page.tsx              # Main dashboard router
│   │   │   ├── admin/
│   │   │   │   └── page.tsx
│   │   │   ├── cost_sharing_officer/
│   │   │   │   └── page.tsx
│   │   │   ├── inland_revenue_officer/
│   │   │   │   └── page.tsx
│   │   │   ├── registrar_officer/
│   │   │   │   └── page.tsx
│   │   │   └── student/
│   │   │       └── page.tsx
│   │   │
│   │   ├── student/
│   │   │   ├── agreement/
│   │   │   │   ├── page.tsx          # View agreements
│   │   │   │   └── fill/
│   │   │   │       └── page.tsx      # Fill agreement form
│   │   │   ├── payment/
│   │   │   │   ├── make/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── history/
│   │   │   │       └── page.tsx
│   │   │   └── feedback/
│   │   │       └── page.tsx
│   │   │
│   │   ├── officer/
│   │   │   ├── agreements/
│   │   │   │   └── page.tsx          # Cost officer: view & manage agreements
│   │   │   ├── students/
│   │   │   │   └── page.tsx          # Cost officer: view students
│   │   │   ├── feedback/
│   │   │   │   └── page.tsx          # Cost officer: view feedback
│   │   │   ├── notices/
│   │   │   │   └── page.tsx          # Cost officer: post notices
│   │   │   └── reports/
│   │   │       └── page.tsx          # Cost officer: export reports
│   │   │
│   │   ├── inland/
│   │   │   ├── payments/
│   │   │   │   └── page.tsx          # Verify payments
│   │   │   ├── bank-accounts/
│   │   │   │   └── page.tsx          # View bank transactions
│   │   │   └── notices/
│   │   │       └── page.tsx          # Post notices
│   │   │
│   │   ├── registrar/
│   │   │   ├── upload/
│   │   │   │   └── page.tsx          # Upload student data
│   │   │   ├── students/
│   │   │   │   └── page.tsx          # View students
│   │   │   └── reports/
│   │   │       └── page.tsx          # Generate reports
│   │   │
│   │   ├── admin/
│   │   │   ├── users/
│   │   │   │   └── page.tsx
│   │   │   ├── bank-accounts/
│   │   │   │   └── page.tsx
│   │   │   ├── cost-structure/
│   │   │   │   └── page.tsx
│   │   │   ├── feedback/
│   │   │   │   └── page.tsx
│   │   │   └── notices/
│   │   │       └── page.tsx
│   │   │
│   │   └── notices/
│   │       └── page.tsx              # View all notices
│   │
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── select.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── checkbox.tsx
│   │   │   ├── radio-group.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── alert.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── pagination.tsx
│   │   │   └── ... (other UI components)
│   │   │
│   │   ├── layout/
│   │   │   ├── dashboard-layout.tsx  # Main dashboard wrapper
│   │   │   ├── sidebar.tsx           # Navigation sidebar
│   │   │   ├── header.tsx            # Top header
│   │   │   └── footer.tsx            # Footer
│   │   │
│   │   ├── forms/
│   │   │   ├── login-form.tsx
│   │   │   ├── cost-sharing-form.tsx
│   │   │   ├── payment-form.tsx
│   │   │   ├── feedback-form.tsx
│   │   │   ├── notice-form.tsx
│   │   │   ├── student-upload-form.tsx
│   │   │   └── bank-account-form.tsx
│   │   │
│   │   ├── tables/
│   │   │   ├── students-table.tsx
│   │   │   ├── payments-table.tsx
│   │   │   ├── agreements-table.tsx
│   │   │   ├── notices-table.tsx
│   │   │   └── feedback-table.tsx
│   │   │
│   │   ├── dialogs/
│   │   │   ├── confirm-dialog.tsx
│   │   │   ├── payment-details-dialog.tsx
│   │   │   └── agreement-details-dialog.tsx
│   │   │
│   │   ├── auth-provider.tsx
│   │   ├── theme-provider.tsx
│   │   └── dashboard-layout.tsx
│   │
│   ├── lib/
│   │   ├── utils.ts                  # Utility functions
│   │   ├── types.ts                  # TypeScript types
│   │   ├── storage.ts                # Local storage helpers
│   │   ├── api.ts                    # API client
│   │   └── utils/
│   │       └── export.tsx            # Export utilities (CSV, PDF)
│   │
│   ├── hooks/
│   │   ├── use-mobile.ts
│   │   ├── use-toast.ts
│   │   ├── use-auth.ts               # Authentication hook
│   │   ├── use-user.ts               # User data hook
│   │   └── use-api.ts                # API calls hook
│   │
│   ├── styles/
│   │   └── globals.css               # Global styles
│   │
│   ├── public/
│   │   ├── images/
│   │   ├── icons/
│   │   └── logo.png
│   │
│   ├── next.config.mjs
│   ├── tsconfig.json
│   ├── package.json
│   ├── postcss.config.mjs
│   └── components.json
│
├── docs/                             # Documentation
│   ├── API.md                        # API endpoints
│   ├── DATABASE.md                   # Database schema
│   ├── SETUP.md                      # Setup instructions
│   ├── FEATURES.md                   # Feature documentation
│   └── DEPLOYMENT.md                 # Deployment guide
│
├── scripts/                          # Utility scripts
│   ├── populate_db.py                # Populate database
│   ├── reset_db.py                   # Reset database
│   └── backup_db.py                  # Backup database
│
├── .env.example                      # Environment variables template
├── .gitignore
├── README.md
└── docker-compose.yml                # Docker configuration (optional)
\`\`\`

## Key Features by Role

### Student
- Fill cost sharing agreement (with photo upload)
- View agreement status
- Make payment (only if agreement accepted)
- View payment history
- Submit feedback
- View notices

### Cost Sharing Officer
- View feedback from students
- Post notices
- Export reports to inland revenue officer
- Manage cost structure
- View assigned students
- Accept/Reject agreements

### Inland Revenue Officer
- Verify payments
- View payment status
- View bank account transactions
- Post notices
- View all payments

### Registrar Officer
- Upload student data (CSV/Excel)
- View students
- Generate reports
- Export student lists

### Admin
- Manage users
- Manage bank accounts
- Manage cost structure
- View all data
- System configuration

## API Endpoints Structure

\`\`\`
/api/
├── auth/
│   ├── login
│   ├── logout
│   ├── register
│   └── forgot-password
├── student/
│   ├── agreements/
│   ├── payments/
│   └── feedback/
├── officer/
│   ├── agreements/
│   ├── feedback/
│   ├── notices/
│   └── reports/
├── inland/
│   ├── payments/
│   ├── bank-accounts/
│   └── notices/
├── registrar/
│   ├── students/
│   └── reports/
└── admin/
    ├── users/
    ├── bank-accounts/
    └── cost-structure/
\`\`\`

## Database Models

- **User** - Authentication & user management
- **CostSharingAgreement** - Student agreements (with photo_receipt field)
- **Payment** - Payment records (with TIN field)
- **BankAccount** - Bank account details
- **CostStructure** - Cost structure configuration
- **Notice** - System notices
- **Feedback** - Student feedback
- **StudentData** - Student information
- **Notification** - User notifications

## Environment Variables

\`\`\`
# Backend
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=OCSMS
