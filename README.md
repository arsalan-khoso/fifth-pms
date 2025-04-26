# FIFTH Property Management System

A comprehensive property management solution for managing properties, tenants, landlords, and leases.

## Overview

The FIFTH Property Management System is a Django-based API that provides functionality for managing:
- Contacts (landlords and tenants)
- Property units
- Lease agreements
- Dashboard analytics

## Entity Relationship Diagram (ERD)

```
+-------------+       +-------------+       +-------------+
|   Contact   |       |    Unit     |       |    Lease    |
+-------------+       +-------------+       +-------------+
| id          |       | id          |       | id          |
| name        |       | unit_number |       | unit        | ----+
| contact_type| <--+  | type        |       | tenant      | -+  |
| email       |    |  | location    |       | landlord    | -+  |
| phone       |    |  | value       |       | start_date  |     |
| address     |    |  | status      |       | duration    |     |
| created_at  |    |  | owner       | --+   | rent_amount |     |
| updated_at  |    |  | created_at  |   |   | payment_freq|     |
+-------------+    |  | updated_at  |   |   | created_at  |     |
                   |  +-------------+   |   | updated_at  |     |
                   +--------------------+   +-------------+     |
                                            |                   |
                                            +-------------------+
```

### Relationships:
- A Contact can be either a Landlord or a Tenant
- A Landlord can own multiple Units
- A Tenant can lease multiple Units (through Lease agreements)
- A Unit can only have one owner (Landlord)
- A Unit can be vacant or occupied (status)
- A Lease connects a Unit, a Tenant, and a Landlord

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip (Python package manager)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/fifth-pms.git
cd fifth-pms
```

2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory with the following content:
```
# Database Configuration
DB_NAME=fifth_pms
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1
```

5. Set up the database
```bash
python manage.py makemigrations core
python manage.py migrate
```

6. Create a superuser
```bash
python manage.py createsuperuser
```

7. Create API Key (Optional - For testing purposes)
```bash
# Access the admin panel and create an API key, or use the built-in command
python manage.py runserver
# Then go to http://localhost:8000/admin/ and create an API key
```

8. Load test data
```bash
python manage.py load_test_data
```

9. Run the development server
```bash
python manage.py runserver
```

## Test Data

The system comes with a management command to load test data:

```bash
python manage.py load_test_data
```

This creates:
- A test landlord (John Doe)
- A test tenant (Jane Smith)
- A test unit (Unit A1, owned by John Doe)
- A test lease connecting the tenant, landlord, and unit

## API Documentation

API documentation is available via Swagger UI at:
```
http://localhost:8000/swagger/
```

And ReDoc at:
```
http://localhost:8000/redoc/
```

## Authentication

The API supports two authentication methods:

1. **JWT Authentication**
   - Obtain a token: `POST /api/token/`
   - Refresh a token: `POST /api/token/refresh/`
   - Include in header: `Authorization: Bearer <token>`

2. **API Key Authentication** (for testing)
   - Create an API key in the admin panel
   - Include in header: `X-API-Key: <api-key>`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/contacts/` | GET, POST | List/Create contacts |
| `/api/v1/contacts/{id}/` | GET, PUT, DELETE | Retrieve/Update/Delete a contact |
| `/api/v1/units/` | GET, POST | List/Create units |
| `/api/v1/units/{id}/` | GET, PUT, DELETE | Retrieve/Update/Delete a unit |
| `/api/v1/leases/` | GET, POST | List/Create leases |
| `/api/v1/leases/{id}/` | GET, PUT, DELETE | Retrieve/Update/Delete a lease |
| `/api/v1/summary/` | GET | Get summary of test data |
| `/api/v1/dashboard/` | GET | Get dashboard statistics |

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT, API Key
- **Documentation**: Swagger/ReDoc

## Frontend Integration

The backend is designed to be integrated with a React.js or Next.js frontend. The API provides all necessary endpoints for the frontend to display:
- Contact profiles (landlords and tenants)
- Unit details and status
- Lease agreements
- Dashboard statistics
