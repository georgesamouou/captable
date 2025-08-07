# Cap Table Management System - Backend

## Overview

This is a robust FastAPI backend for managing a company's capitalization table (Cap Table) and share issuance workflow. The system provides secure authentication, comprehensive shareholder management, share issuance tracking, and PDF certificate generation.

## Technical Approach & Architectural Decisions

### Architecture
- **Framework**: FastAPI for high-performance async API development
- **Database**: PostgreSQL with SQLAlchemy ORM for robust data management
- **Authentication**: JWT-based authentication with role-based access control
- **PDF Generation**: WeasyPrint for dynamic PDF certificate generation
- **Testing**: Comprehensive test suite with pytest and factory-boy

### Key Design Decisions
1. **Layered Architecture**: Clear separation between API routes, business logic, and data access
2. **Security First**: JWT authentication, password hashing, and audit logging
3. **Data Integrity**: Foreign key constraints and validation at multiple levels
4. **Scalability**: Async operations and efficient database queries
5. **Maintainability**: Comprehensive documentation and type hints

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ (or SQLite for local development)
- pip (Python package manager)

## Setup Instructions

### 1. Clone and Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

You can use **PostgreSQL** (recommended for production) or **SQLite** (for quick local development/testing). To use SQLite, set the following in your `.env` file:

```
database_url=sqlite:///./cap_table.db
```

```bash
# Create PostgreSQL database
createdb cap_table_db

# Set environment variables (create .env file)
cp env.example .env
# Edit .env with your database credentials (or use SQLite as described above)
```

### 3. Database Migration

```bash
# Option 1: Use the setup script (recommended)
python setup_db.py

# Option 2: Manual setup
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### 4. Run the Application

```bash
# Using the startup script (recommended)
python start.py

# Or using uvicorn directly
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## AI Tools Used

- **Cursor's Chat**: Primary AI assistant for code generation and architectural decisions
- **GitHub Copilot**: Code completion and suggestions during development

## Key Prompts Used

### Architecture Design
```
"Design a FastAPI backend for a cap table management system with the following requirements:
- JWT authentication with admin and shareholder roles
- PostgreSQL database with SQLAlchemy ORM
- PDF certificate generation
- Comprehensive audit logging
- RESTful API endpoints for shareholder and issuance management
Please include proper error handling, validation, and security best practices."
```

### Database Models
```
"Create SQLAlchemy models for a cap table system with:
- User model with role-based authentication
- ShareholderProfile linked to User
- ShareIssuance for tracking share distributions
- AuditEvent for logging all critical actions
Include proper relationships, constraints, and validation."
```

### API Endpoints
```
"Implement FastAPI endpoints for:
- JWT authentication (/api/token/)
- Shareholder management (CRUD operations)
- Share issuance workflow
- PDF certificate generation
Include proper request/response models, validation, and error handling."
```

### PDF Generation
```
"Create a PDF certificate generator using WeasyPrint that:
- Generates professional share certificates
- Includes company branding and watermarking
- Contains all issuance details (shares, price, date)
- Is dynamically generated from database data
Include proper styling and layout."
```

## API Contract

### Authentication
- `POST /api/token/` - Login and get JWT token (form data)
- `POST /api/login/` - Login and get JWT token (JSON body)

### Shareholder Management (Admin)
- `GET /api/shareholders/` - List all shareholders with total shares
- `POST /api/shareholders/` - Create new shareholder
- `GET /api/shareholders/me` - Get current shareholder's profile

### Share Issuance
- `GET /api/issuances/` - List all issuances (admin only)
- `GET /api/issuances/my` - List current shareholder's issuances
- `POST /api/issuances/` - Create new share issuance (admin only)
- `GET /api/issuances/{id}/certificate/` - Generate PDF certificate (admin only)
- `GET /api/issuances/{id}/certificate/my/` - Generate PDF certificate (shareholder own)

### Dashboard (Admin)
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/ownership-distribution` - Get ownership distribution for pie chart

### Audit Logs (Admin)
- `GET /api/audit/` - View audit trail

## Default Users

The system creates default users on startup:

- **Admin**: admin@company.com / admin123
- **Shareholder**: shareholder@company.com / shareholder123

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run tests with verbose output
pytest -v

# Run tests and generate coverage report
pytest --cov=app --cov-report=html
```

## Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- Comprehensive audit logging
- SQL injection prevention through ORM

## Future Improvements

1. **Email Notifications**: Implement email service for share issuance notifications
2. **Advanced Analytics**: Add reporting and analytics endpoints
3. **File Upload**: Support for document attachments
4. **Real-time Updates**: WebSocket integration for live updates
5. **Caching**: Redis integration for performance optimization 