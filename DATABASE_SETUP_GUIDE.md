# ConsultEase Database Setup Guide

This document provides comprehensive instructions for setting up and configuring the database for the ConsultEase faculty consultation system.

## Table of Contents

1. [Overview](#overview)
2. [Database Options](#database-options)
3. [Firebase Setup](#firebase-setup)
4. [PostgreSQL Setup](#postgresql-setup)
5. [Database Configuration](#database-configuration)
6. [Default Data](#default-data)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

## Overview

ConsultEase supports two database options:
- **Firebase Firestore** - Default cloud-based option with real-time updates and offline capabilities
- **PostgreSQL** - Self-hosted option for universities that prefer to keep data on-premises

The system uses a database adapter pattern that allows switching between different database backends without changing application code.

## Database Options

### Firebase Firestore (Default)
- Cloud-based, serverless database
- Real-time updates and synchronization
- Built-in offline capabilities
- Scalable with minimal configuration
- Requires internet connection for initial setup

### PostgreSQL
- Self-hosted, traditional relational database
- Full control over data storage and security
- Can be deployed on university infrastructure
- Requires more setup and maintenance
- Good option for institutions with existing PostgreSQL infrastructure

## Firebase Setup

### Prerequisites
- Google Cloud Platform account
- Firebase project
- Billing account (Free tier available)

### Step 1: Create a Firebase Project
1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter a project name (e.g., "ConsultEase-Production")
4. Choose whether to enable Google Analytics (recommended)
5. Follow the prompts to complete project creation

### Step 2: Enable Firestore Database
1. From the Firebase project dashboard, select "Firestore Database" from the left menu
2. Click "Create database"
3. Choose starting mode:
   - **Production mode**: Recommended for deployment (restrictive security rules)
   - **Test mode**: For development (allows read/write access to all data)
4. Select a location (choose a region close to your users)
5. Click "Enable"

### Step 3: Create Service Account
1. Go to "Project settings" (gear icon in the top left)
2. Select the "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file as `firebase_key.json`
5. Place this file in the `central_system` directory

### Step 4: Configure Security Rules
1. Go to "Firestore Database" in the Firebase console
2. Select the "Rules" tab
3. **Important**: Firestore uses a different security rules format than Firebase Realtime Database
4. Use the following template for Firestore rules (do not use the JSON format from firebase_security_rules.json):

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Default deny access
    match /{document=**} {
      allow read: if false;
      allow write: if false;
    }
    
    // Faculty collection
    match /faculty/{facultyId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && (request.auth.token.admin == true || request.auth.uid == facultyId);
    }
    
    // Students collection
    match /students/{studentId} {
      allow read: if request.auth != null && (request.auth.token.admin == true || request.auth.uid == studentId);
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
    
    // Consultation requests collection
    match /consultation_requests/{requestId} {
      allow read: if request.auth != null && (
        request.auth.token.admin == true ||
        request.auth.uid == resource.data.faculty_id ||
        request.auth.uid == resource.data.student_id
      );
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && (
        request.auth.token.admin == true ||
        request.auth.uid == resource.data.faculty_id
      );
    }
    
    // Other collections with appropriate rules...
  }
}
```

5. **IMPORTANT NOTE**: Firestore security rules require the `if` keyword before each condition. Rules without the `if` keyword will fail silently. The following formats are NOT valid:
   ```
   // INVALID - missing "if" keyword
   allow read: request.auth != null;
   
   // CORRECT format
   allow read: if request.auth != null;
   ```

6. Customize the rules as needed for your security requirements
7. Click "Publish"

### Step 5: Update Configuration
1. Open `central_system/config.env`
2. Update the Firebase configuration section:
```
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
FIREBASE_REGION=your-selected-region
FIREBASE_SERVICE_ACCOUNT=firebase_key.json
```

## PostgreSQL Setup

### Prerequisites
- PostgreSQL server (version 12 or higher)
- psycopg2 Python package (`pip install psycopg2-binary`)

### Step 1: Install PostgreSQL
#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### On Windows:
1. Download the installer from [PostgreSQL website](https://www.postgresql.org/download/windows/)
2. Run the installer and follow the prompts
3. Remember the password you set for the 'postgres' user

#### On macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

### Step 2: Create Database and User
Connect to PostgreSQL and create the database and user:

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE consultease;

# Create user with password
CREATE USER consultease_user WITH ENCRYPTED PASSWORD 'strong_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE consultease TO consultease_user;

# Exit PostgreSQL shell
\q
```

### Step 3: Update Configuration
1. Open `central_system/config.env`
2. Add or modify the PostgreSQL configuration section:
```
# Database Configuration
DATABASE_TYPE=postgresql
POSTGRESQL_DBNAME=consultease
POSTGRESQL_USER=consultease_user
POSTGRESQL_PASSWORD=strong_password_here
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
```

### Step 4: Connection Pooling (Recommended for Production)
For better performance in production environments, enable connection pooling:

1. Install the psycopg2 connection pool package:
```bash
pip install psycopg2-pool
```

2. Add connection pooling settings to `config.env`:
```
# PostgreSQL connection pooling
POSTGRESQL_POOL_MIN=1
POSTGRESQL_POOL_MAX=10
POSTGRESQL_POOL_IDLE=60
```

3. The system will automatically use connection pooling when these settings are present.

### Step 5: Initialize Database
The system will automatically create the necessary tables when it connects to the database for the first time. This includes:
- Faculty table
- Students table
- Offices table
- Consultation requests table
- Consultations table
- Admin users table
- Audit log table

## Database Configuration

### Switching Database Type
To switch between database types, update the `DATABASE_TYPE` setting in `config.env`:

- For Firebase:
```
DATABASE_TYPE=firebase
```

- For PostgreSQL:
```
DATABASE_TYPE=postgresql
```

- For development/testing (simulation mode):
```
DATABASE_TYPE=simulation
```

### Configuration Properties
The database adapters support the following configuration properties:

#### Firebase Configuration
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_DATABASE_URL`: URL to your Firestore database
- `FIREBASE_REGION`: Selected region for your Firestore database
- `FIREBASE_SERVICE_ACCOUNT`: Path to your service account key file

#### PostgreSQL Configuration
- `POSTGRESQL_DBNAME`: Database name
- `POSTGRESQL_USER`: Username
- `POSTGRESQL_PASSWORD`: Password
- `POSTGRESQL_HOST`: Database host (default: localhost)
- `POSTGRESQL_PORT`: Database port (default: 5432)

## Default Data

### Default Administrator Account
The system automatically creates a default administrator account when initializing the database:

- **Username**: admin
- **Password**: admin123
- **Role**: superadmin

> **IMPORTANT**: Change the default administrator password after the first login for security reasons!

### Sample Data
In development and testing environments, the system can populate the database with sample data:

- Faculty members
- Students with RFID cards
- Office locations
- Sample consultation requests

To enable this feature, set the following in `config.env`:
```
INITIALIZE_SAMPLE_DATA=True
```

## Backup and Recovery

### Firebase Backup
Firebase automatically backs up your data. You can also:

1. Export data from the Firebase console:
   - Go to Project Settings > Usage and Billing > Export Project
   - Follow the prompts to export data

2. Use the Firebase Admin SDK to create automated backups:
   ```python
   import firebase_admin
   from firebase_admin import credentials, firestore
   import json
   
   # Initialize Firebase
   cred = credentials.Certificate('firebase_key.json')
   firebase_admin.initialize_app(cred)
   db = firestore.client()
   
   # Export data
   def export_collection(collection_name, output_file):
       docs = db.collection(collection_name).get()
       data = {doc.id: doc.to_dict() for doc in docs}
       with open(output_file, 'w') as f:
           json.dump(data, f)
   
   # Export main collections
   export_collection('faculty', 'faculty_backup.json')
   export_collection('students', 'students_backup.json')
   export_collection('consultation_requests', 'requests_backup.json')
   ```

### PostgreSQL Backup
Regular backups are recommended:

1. Using pg_dump (command line):
   ```bash
   pg_dump -U consultease_user -d consultease -F c -f consultease_backup.dump
   ```

2. Scheduled backups with cron job (Linux/macOS):
   ```bash
   # Add to crontab (run daily at 2 AM)
   0 2 * * * pg_dump -U consultease_user -d consultease -F c -f /path/to/backups/consultease_$(date +\%Y\%m\%d).dump
   ```

3. Restore from backup:
   ```bash
   pg_restore -U consultease_user -d consultease -c consultease_backup.dump
   ```

## Troubleshooting

### Common Issues

#### Firebase Connection Issues
- **Issue**: "Failed to initialize Firebase"
  - **Solution**: Check your internet connection and verify the service account key file exists
  - **Solution**: Ensure the Firebase project ID in config.env matches your project

- **Issue**: "Permission denied" errors
  - **Solution**: Check your Firebase security rules and service account permissions

#### PostgreSQL Connection Issues
- **Issue**: "Could not connect to PostgreSQL server"
  - **Solution**: Verify the PostgreSQL server is running
  - **Solution**: Check the connection parameters (host, port, username, password)

- **Issue**: "Password authentication failed"
  - **Solution**: Verify the password in config.env matches the database user's password

#### General Database Issues
- **Issue**: "Database adapter not available"
  - **Solution**: Install required Python packages (`pip install -r requirements.txt`)
  - **Solution**: Check if the selected database type is supported (firebase, postgresql, simulation)

### Getting Help
If you encounter persistent database issues:

1. Check the application logs (`logs/database.log`)
2. Verify your configuration settings
3. Ensure all required dependencies are installed
4. Try switching to simulation mode for testing (`DATABASE_TYPE=simulation`) 