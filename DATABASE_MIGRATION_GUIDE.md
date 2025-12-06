# OCSMS Database Migration Guide

## Overview
This guide explains how to migrate your OCSMS database from SQLite to PostgreSQL or MySQL, or repair a corrupted SQLite database.

## Current Database Status
- **Current**: SQLite (db.sqlite3)
- **Issues**: Database corruption ("database disk image is malformed")
- **Solution**: Migrate to a more robust database or repair SQLite

---

## Option 1: Repair Corrupted SQLite Database (Quick Fix)

### Steps:
1. **Run the repair script**:
   \`\`\`bash
   python fix_database.py
   \`\`\`

2. **Populate sample data**:
   \`\`\`bash
   python populate_db.py
   \`\`\`

3. **Create test users**:
   \`\`\`bash
   python create_test_users.py
   \`\`\`

4. **Start the server**:
   \`\`\`bash
   python manage.py runserver
   \`\`\`

### Pros:
- Quick and easy
- No external dependencies
- Good for development

### Cons:
- SQLite has limitations with concurrent access
- Not suitable for production
- Can corrupt again under heavy load

---

## Option 2: Migrate to PostgreSQL (Recommended for Production)

### Prerequisites:
1. Install PostgreSQL:
   - **Windows**: Download from https://www.postgresql.org/download/windows/
   - **Mac**: `brew install postgresql`
   - **Linux**: `sudo apt-get install postgresql postgresql-contrib`

2. Install Python PostgreSQL adapter:
   \`\`\`bash
   pip install psycopg2-binary
   \`\`\`

### Migration Steps:

#### Step 1: Create PostgreSQL Database
\`\`\`bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE ocsms_db;
CREATE USER ocsms_user WITH PASSWORD 'your_secure_password';
ALTER ROLE ocsms_user SET client_encoding TO 'utf8';
ALTER ROLE ocsms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE ocsms_user SET default_transaction_deferrable TO on;
ALTER ROLE ocsms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE ocsms_db TO ocsms_user;
\q
\`\`\`

#### Step 2: Update Django Settings
Edit `ocsms/ocsms/settings.py`:

\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ocsms_db',
        'USER': 'ocsms_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
\`\`\`

#### Step 3: Run Migrations
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

#### Step 4: Create Test Users
\`\`\`bash
python create_test_users.py
\`\`\`

#### Step 5: Start Server
\`\`\`bash
python manage.py runserver
\`\`\`

### Pros:
- Production-ready
- Handles concurrent access well
- Better performance
- More reliable

### Cons:
- Requires PostgreSQL installation
- More complex setup
- Requires database administration

---

## Option 3: Migrate to MySQL

### Prerequisites:
1. Install MySQL:
   - **Windows**: Download from https://dev.mysql.com/downloads/mysql/
   - **Mac**: `brew install mysql`
   - **Linux**: `sudo apt-get install mysql-server`

2. Install Python MySQL adapter:
   \`\`\`bash
   pip install mysqlclient
   \`\`\`

### Migration Steps:

#### Step 1: Create MySQL Database
\`\`\`bash
# Connect to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE ocsms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ocsms_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ocsms_db.* TO 'ocsms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
\`\`\`

#### Step 2: Update Django Settings
Edit `ocsms/ocsms/settings.py`:

\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ocsms_db',
        'USER': 'ocsms_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}
\`\`\`

#### Step 3: Run Migrations
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

#### Step 4: Create Test Users
\`\`\`bash
python create_test_users.py
\`\`\`

#### Step 5: Start Server
\`\`\`bash
python manage.py runserver
\`\`\`

### Pros:
- Widely used and supported
- Good performance
- Easy to manage

### Cons:
- Requires MySQL installation
- Slightly less robust than PostgreSQL

---

## Migrating Existing Data

If you have existing data in SQLite that you want to preserve:

### Step 1: Export Data from SQLite
\`\`\`bash
python manage.py dumpdata > data.json
\`\`\`

### Step 2: Switch Database in settings.py
Update `DATABASES` configuration to your new database (PostgreSQL or MySQL)

### Step 3: Run Migrations
\`\`\`bash
python manage.py migrate
\`\`\`

### Step 4: Import Data
\`\`\`bash
python manage.py loaddata data.json
\`\`\`

---

## Test User Credentials

After setup, use these credentials to test:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Cost Officer | costofficer | costofficer123 |
| Registrar | registrar | registrar123 |
| Inland Revenue Officer | inlandofficer | inlandofficer123 |
| Student | student1 | student123 |

---

## Troubleshooting

### PostgreSQL Connection Error
\`\`\`
Error: could not translate host name "localhost" to address
\`\`\`
**Solution**: Ensure PostgreSQL service is running
- Windows: Check Services (postgresql-x64-XX)
- Mac: `brew services start postgresql`
- Linux: `sudo systemctl start postgresql`

### MySQL Connection Error
\`\`\`
Error: (2003, "Can't connect to MySQL server on 'localhost'")
\`\`\`
**Solution**: Ensure MySQL service is running
- Windows: Check Services (MySQL80)
- Mac: `brew services start mysql`
- Linux: `sudo systemctl start mysql`

### Migration Conflicts
\`\`\`
Error: Conflicting migrations detected
\`\`\`
**Solution**: Delete migration files and recreate
\`\`\`bash
rm cost_sharing/migrations/000*.py
python manage.py makemigrations
python manage.py migrate
\`\`\`

---

## Performance Recommendations

### For Development (SQLite):
- Use SQLite for quick testing
- Repair database if corrupted
- Not recommended for multiple concurrent users

### For Production (PostgreSQL/MySQL):
- Use PostgreSQL for best reliability
- Set up regular backups
- Monitor database performance
- Use connection pooling for high traffic

---

## Backup and Recovery

### Backup PostgreSQL
\`\`\`bash
pg_dump -U ocsms_user -h localhost ocsms_db > backup.sql
\`\`\`

### Restore PostgreSQL
\`\`\`bash
psql -U ocsms_user -h localhost ocsms_db < backup.sql
\`\`\`

### Backup MySQL
\`\`\`bash
mysqldump -u ocsms_user -p ocsms_db > backup.sql
\`\`\`

### Restore MySQL
\`\`\`bash
mysql -u ocsms_user -p ocsms_db < backup.sql
\`\`\`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Django documentation: https://docs.djangoproject.com/
3. Check database-specific documentation
