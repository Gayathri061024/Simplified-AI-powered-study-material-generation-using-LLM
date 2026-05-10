# Study Materials Management System

A comprehensive web-based platform for managing academic study materials, courses, and student uploads with role-based access control for administrators, faculty, and students.

## Project Overview

This system provides:
- **Admin Dashboard**: Manage faculty, students, and course uploads
- **Faculty Portal**: Upload and manage study materials, verify student submissions
- **Student Portal**: Access study materials, register, and submit assignments
- **Database Management**: Track materials by program (CSE, IT), year, and semester
- **Upload System**: Secure file upload and verification workflows

## Project Structure

```
├── app.py                          # Main Flask/Django application
├── generator.py                    # Material generation utilities
├── materials.py                    # Materials management
├── templates/                      # HTML templates
│   ├── admin_*.html               # Admin dashboards and pages
│   ├── faculty_*.html             # Faculty interfaces
│   ├── login.html                 # Authentication pages
│   └── dashboard.html             # User dashboards
├── static/                         # Static assets (CSS, JS)
├── uploads/                        # User-uploaded files
├── study_materials/                # Organized course materials
│   ├── CSE/                       # Computer Science Engineering
│   │   ├── 1st Year/
│   │   ├── 2nd Year/
│   │   ├── 3rd Year/
│   │   └── 4th Year/
│   └── IT/                        # Information Technology
│       ├── 1st Year/
│       ├── 2nd Year/
│       ├── 3rd Year/
│       └── 4th Year/
├── scratch/                        # Development and debugging scripts
├── ALGORITHM.md                    # Algorithm documentation
├── SYSTEM_ARCHITECTURE.md          # System design documentation
└── requirements.txt                # Python dependencies
```

## Key Features

### User Roles
- **Admin**: Full system control, user management, material oversight
- **Faculty**: Upload materials, verify submissions, manage courses
- **Student**: Access materials, upload assignments, track progress

### Core Functionality
- Multi-level course organization (Program → Year → Semester → Subject)
- User authentication with OTP verification
- File upload and verification workflows
- Material organization by semester and subject code
- Database inspection and migration tools

## Setup & Installation

### Prerequisites
- Python 3.x
- Flask/Django framework
- Database system (SQLite/PostgreSQL)

### Installation

1. **Clone/Extract the project**
   ```bash
   cd c:\proj
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000` (or configured port)

## Database

### Key Tables
- Users (Admin, Faculty, Students)
- Courses & Subjects
- Materials & Assignments
- Upload History & Verification Logs

### Database Scripts
- `inspect_db.py`: Inspect database structure and contents
- `query_db.py`: Run custom database queries
- `migrate_db.py`: Database migration utilities
- `verify_all.py`: Data verification tools

## Configuration

Update application settings in `app.py` or a dedicated config file:
- Database connection string
- Upload directory path
- Session timeout
- Email configuration (for OTP/notifications)

## Common Operations

### Admin Tasks
- Navigate to `/admin/login` for admin panel
- Manage faculty accounts in Faculty Management
- Monitor student uploads and verifications
- Generate reports

### Faculty Tasks
- Login at `/faculty/login`
- Upload study materials organized by semester/subject
- Verify student assignments
- Monitor class uploads

### Student Tasks
- Register at `/register`
- Login at `/login`
- Access materials from dashboard
- Upload assignments

## Development

### Debug Scripts
- `debug_gen.py`: Debug generation utilities
- `debug_mcq.js`: MCQ debugging
- `test_*.py`: Test various components
- `scratch/`: Various development utilities

### Documentation
- `SYSTEM_ARCHITECTURE.md`: Detailed system design
- `ALGORITHM.md`: Algorithm documentation
- `REFERENCES_PAPERS.md`: Academic references

## Logs

- `email_logs.txt`: Email/OTP notification logs
- `debug_out.txt`: Debug output
- Other log files in `scratch/test_output.txt`

## Troubleshooting

- Check `email_logs.txt` for authentication issues
- Use `inspect_db.py` to verify database integrity
- Review debug files for specific operation issues

## Contributing

1. Test changes locally using debug scripts
2. Verify database migrations
3. Update documentation for new features

## Support

For issues or questions, refer to:
- `SYSTEM_ARCHITECTURE.md` for system design
- Debug scripts in `scratch/` for testing
- Database inspection tools for data issues

---

