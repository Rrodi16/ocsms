# OCSMS Setup Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Git

## Backend Setup (Django)

### 1. Clone Repository
\`\`\`bash
git clone <repository-url>
cd ocsms/backend
\`\`\`

### 2. Create Virtual Environment
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 3. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Configure Environment
\`\`\`bash
cp .env.example .env
# Edit .env with your settings
\`\`\`

### 5. Run Migrations
\`\`\`bash
python manage.py migrate
\`\`\`

### 6. Create Superuser
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 7. Run Development Server
\`\`\`bash
python manage.py runserver
\`\`\`

Backend will be available at: http://localhost:8000

## Frontend Setup (Next.js)

### 1. Navigate to Frontend
\`\`\`bash
cd ../frontend
\`\`\`

### 2. Install Dependencies
\`\`\`bash
npm install
\`\`\`

### 3. Configure Environment
\`\`\`bash
cp .env.example .env.local
# Edit .env.local with your settings
\`\`\`

### 4. Run Development Server
\`\`\`bash
npm run dev
\`\`\`

Frontend will be available at: http://localhost:3000

## Database Setup

### Using SQLite (Development)
Already configured in settings.py

### Using PostgreSQL (Production)
1. Install PostgreSQL
2. Create database: `createdb ocsms_db`
3. Update settings.py with PostgreSQL config
4. Run migrations

### Using MySQL (Production)
1. Install MySQL
2. Create database: `CREATE DATABASE ocsms_db;`
3. Update settings.py with MySQL config
4. Run migrations

## Initial Data Population

\`\`\`bash
python manage.py populate_db  # Populate with sample data
\`\`\`

## Testing

### Backend Tests
\`\`\`bash
python manage.py test
\`\`\`

### Frontend Tests
\`\`\`bash
npm run test
\`\`\`

## Deployment

See DEPLOYMENT.md for production deployment instructions.
