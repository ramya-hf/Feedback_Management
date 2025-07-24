# Feedback Management System

A comprehensive feedback management application built with Django REST Framework and designed for React frontend integration.

## Features

- **Role-based Access Control**: Admin, Moderator, and Contributor roles
- **JWT Authentication**: Secure token-based authentication
- **User Management**: Complete user profile and role management
- **RESTful API**: Clean and well-documented API endpoints
- **Admin Interface**: Comprehensive Django admin interface
- **Media Handling**: User avatar upload support
- **PostgreSQL Ready**: Configured for production PostgreSQL (currently using SQLite for development)

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Authentication**: JWT with djangorestframework-simplejwt
- **Database**: PostgreSQL (SQLite for development)
- **File Storage**: Local file system (can be extended to cloud storage)

## Project Structure

```
FeatureManagement/
├── accounts/                          # User authentication and management
│   ├── management/commands/           # Custom management commands
│   ├── migrations/                    # Database migrations
│   ├── admin.py                      # Django admin configuration
│   ├── models.py                     # User model with roles
│   ├── serializers.py                # API serializers
│   ├── views.py                      # API views
│   └── urls.py                       # URL patterns
├── feedback_management/              # Main project settings
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # Main URL configuration
│   └── wsgi.py                       # WSGI configuration
├── static/                           # Static files
├── media/                            # Media uploads
├── logs/                             # Application logs
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables
└── manage.py                         # Django management script
```

## Installation & Setup

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd FeatureManagement

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file or modify the existing one:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DB_NAME=feedback_management
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOW_ALL_ORIGINS=True

# Email (for production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create admin user
python manage.py create_admin --email admin@example.com --password admin123

# Or create superuser manually
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register/` | User registration | None |
| POST | `/api/auth/login/` | User login | None |
| POST | `/api/auth/logout/` | User logout | Required |
| POST | `/api/auth/refresh/` | Refresh JWT token | None |

### User Management Endpoints

| Method | Endpoint | Description | Authentication | Permission |
|--------|----------|-------------|----------------|------------|
| GET | `/api/auth/me/` | Current user info | Required | Own profile |
| GET/PUT/PATCH | `/api/auth/profile/` | User profile management | Required | Own profile |
| POST | `/api/auth/change-password/` | Change password | Required | Own account |
| GET | `/api/auth/users/` | List users | Required | Admin/Moderator |
| GET/PUT/PATCH | `/api/auth/users/{id}/` | User details | Required | Admin or own profile |
| PATCH | `/api/auth/users/{id}/role/` | Update user role | Required | Admin only |
| PATCH | `/api/auth/users/{id}/activate/` | Activate user | Required | Admin only |
| PATCH | `/api/auth/users/{id}/deactivate/` | Deactivate user | Required | Admin only |
| GET | `/api/auth/stats/` | User statistics | Required | Admin/Moderator |

## API Usage Examples

### User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "company": "Test Company",
    "job_title": "Developer"
  }'
```

### User Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@feedbackmanagement.com",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@feedbackmanagement.com",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin",
    "avatar": null,
    "is_email_verified": true
  }
}
```

### Get Current User Profile

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer your-access-token"
```

### Update User Profile

```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Updated bio",
    "phone_number": "+1234567890",
    "email_notifications": false
  }'
```

### List Users (Admin/Moderator only)

```bash
curl -X GET "http://localhost:8000/api/auth/users/?role=contributor&search=john" \
  -H "Authorization: Bearer your-access-token"
```

### Change User Role (Admin only)

```bash
curl -X PATCH http://localhost:8000/api/auth/users/2/role/ \
  -H "Authorization: Bearer your-access-token" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "moderator"
  }'
```

## User Roles & Permissions

### Admin
- Full system access
- Manage all users
- Change user roles
- Activate/deactivate users
- View all statistics
- Access Django admin interface

### Moderator
- Manage feedback content
- View user lists and details
- View user statistics
- Cannot change user roles
- Cannot activate/deactivate users

### Contributor
- Submit and manage own feedback
- Participate in discussions
- Update own profile
- View other contributors

## Model Schema

### User Model

```python
class User(AbstractUser):
    email = EmailField(unique=True)  # Primary login field
    role = CharField(choices=['admin', 'moderator', 'contributor'])
    avatar = ImageField(upload_to='avatars/')
    bio = TextField(max_length=500)
    phone_number = CharField(max_length=17)
    company = CharField(max_length=255)
    job_title = CharField(max_length=255)
    is_email_verified = BooleanField(default=False)
    email_notifications = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages:

```json
{
  "error": "Error message description",
  "detail": "Detailed error information",
  "field_errors": {
    "email": ["This field is required."]
  }
}
```

Common status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Testing

### Manual Testing

1. Start the development server:
```bash
python manage.py runserver
```

2. Test registration:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'
```

3. Test login and use the returned token for authenticated requests

### Django Admin

Access the admin interface at `http://localhost:8000/admin/` using the admin credentials created with the `create_admin` command.

## Production Deployment

### Database Configuration

For production, uncomment the PostgreSQL configuration in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

### Security Settings

Update production settings:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
]
```

### Static Files

Configure static file serving for production:

```bash
python manage.py collectstatic
```

## Next Steps

This foundation provides:

1. ✅ Complete user authentication system
2. ✅ Role-based access control
3. ✅ RESTful API endpoints
4. ✅ Admin interface
5. ✅ Database migrations
6. ✅ Comprehensive documentation

Ready for the next phase:
- Feedback model and API endpoints
- Board management system
- Comment and voting system
- Analytics and reporting
- Email notifications
- Frontend React application

## Support

For issues and questions, please refer to the API documentation or check the Django logs in the `logs/` directory. 