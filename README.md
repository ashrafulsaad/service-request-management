# Government Service Request Management API

A Django REST Framework backend for managing citizen service requests in a government/public-service environment.

The system provides role-based access for **citizens, officers, and administrators**, with JWT authentication, request assignment, filtering, searching, pagination, attachments, comments, and administrative statistics.

---

## Features

- JWT-based authentication
- Role-based authorization
  - Citizen
  - Officer
  - Admin
- Citizen service-request creation and management
- Officer request assignment
- Request reassignment by administrators
- Request status and priority management
- Category management
- Comments
- File attachments
- File type and size validation
- Filtering
- Search
- Ordering
- Pagination
- Administrative statistics
- OpenAPI schema
- Interactive Swagger UI
- PostgreSQL database
- Docker Compose development environment
- Automated API test suite

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Django | Web framework |
| Django REST Framework | REST API |
| Simple JWT | JWT authentication |
| PostgreSQL | Database |
| django-filter | API filtering |
| drf-spectacular | OpenAPI / Swagger documentation |
| Docker | Development environment |
| Docker Compose | Multi-container environment |

---

## Architecture

```text
Client
  │
  │ HTTP / REST
  ▼
Django REST Framework
  │
  ├── JWT Authentication
  │
  ├── Role-Based Permissions
  │
  ├── Service Request API
  │
  ├── Category API
  │
  ├── Comment API
  │
  ├── Attachment API
  │
  ├── User API
  │
  └── Admin Statistics
  │
  ▼
PostgreSQL
```

---

## User Roles

### Citizen

Citizens can:

- Register and log in
- View their own service requests
- Create service requests
- Modify pending requests
- View related comments and attachments
- Upload attachments to their requests

### Officer

Officers can:

- Log in
- View requests assigned to them
- Update assigned requests
- Add comments
- Access attachments belonging to assigned requests

### Admin

Administrators can:

- View all service requests
- Manage categories
- Create officers
- Assign requests to officers
- Reassign requests
- Manage administrative data
- View system statistics
- View users

---

## Authentication

The API uses **JSON Web Tokens (JWT)**.

### Register

```http
POST /api/auth/register/
```

Example:

```json
{
  "username": "saad",
  "password": "your-password"
}
```

### Login

```http
POST /api/auth/login/
```

Example:

```json
{
  "username": "saad",
  "password": "your-password"
}
```

The login response contains:

```json
{
  "refresh": "YOUR_REFRESH_TOKEN",
  "access": "YOUR_ACCESS_TOKEN"
}
```

Use the access token for authenticated API requests:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## API Documentation

Interactive Swagger documentation:

```text
http://localhost:8000/api/docs/
```

OpenAPI schema:

```text
http://localhost:8000/api/schema/
```

Swagger supports JWT authentication through the **Authorize** button.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a citizen |
| POST | `/api/auth/login/` | Obtain JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current user |
| GET | `/api/auth/citizen-test/` | Citizen-only test endpoint |
| POST | `/api/auth/officers/` | Create officer |

---

### Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/categories/` | List categories |
| POST | `/api/categories/` | Create category |
| GET | `/api/categories/{id}/` | Retrieve category |
| PUT/PATCH | `/api/categories/{id}/` | Update category |
| DELETE | `/api/categories/{id}/` | Delete category |

Category listing and retrieval require authentication.

Category creation, modification, and deletion require admin privileges.

Categories currently cannot be deleted when they are referenced by existing service requests.

---

### Service Requests

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/requests/` | List requests visible to current user |
| POST | `/api/requests/` | Create request |
| GET | `/api/requests/{id}/` | Retrieve request |
| PUT/PATCH | `/api/requests/{id}/` | Update request |
| DELETE | `/api/requests/{id}/` | Delete request |
| POST | `/api/requests/{id}/assign/` | Assign officer |
| GET/POST | `/api/requests/{id}/attachments/` | List/upload attachments |
| GET/POST | `/api/requests/{id}/comments/` | List/create comments |

---

## Service Request Visibility

Requests are filtered according to the authenticated user's role.

```text
Citizen
   │
   └── Own requests

Officer
   │
   └── Assigned requests

Admin
   │
   └── All requests
```

---

## Request Filtering

The service request API supports filtering by:

- Status
- Priority
- Category
- Assigned officer
- Creation date

Examples:

```http
GET /api/requests/?status=pending
```

```http
GET /api/requests/?priority=high
```

```http
GET /api/requests/?category=2
```

```http
GET /api/requests/?assigned_officer=3
```

Date range:

```http
GET /api/requests/?created_at_after=2026-09-01T00:00:00
```

```http
GET /api/requests/?created_at_before=2026-09-30T23:59:59
```

Filters can also be combined.

Example:

```http
GET /api/requests/?status=pending&priority=high
```

---

## Search

Service requests can be searched by title.

```http
GET /api/requests/?search=water
```

---

## Ordering

Supported ordering fields:

- `created_at`
- `priority`

Example:

```http
GET /api/requests/?ordering=created_at
```

Descending order:

```http
GET /api/requests/?ordering=-created_at
```

The default ordering is newest requests first.

---

## Pagination

The API uses page-number pagination.

The default page size is:

```text
10
```

Example:

```http
GET /api/requests/?page=2
```

A paginated response contains:

```json
{
  "count": 25,
  "next": "...",
  "previous": null,
  "results": []
}
```

---

## Attachments

Attachments can be uploaded to service requests.

Supported file extensions:

```text
.pdf
.jpg
.jpeg
.png
.doc
.docx
```

Maximum file size:

```text
5 MB
```

Example request:

```http
POST /api/requests/{id}/attachments/
Content-Type: multipart/form-data
```

The authenticated user is automatically recorded as the uploader.

---

## Comments

Comments are associated with service requests and record the user who created them.

Example:

```http
POST /api/requests/{id}/comments/
```

```json
{
  "text": "Additional information regarding this request."
}
```

---

## Administrative Statistics

Administrators can access:

```http
GET /api/admin/stats/
```

The endpoint provides statistics including:

- Total requests
- Requests by status
- Requests by priority
- Requests by category
- Requests per officer
- Number of unassigned requests

---

## Project Structure

```text
task/
│
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── requests_app/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── filters.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── media/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── README.md
```

---

## Running the Project

### 1. Clone the repository

```bash
git clone git@github.com:ashrafulsaad/service-request-management.git
cd service-request-management
```

### 2. Create the environment file

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=your-secret-key

POSTGRES_DB=your_database
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Do not commit the real `.env` file to Git.

---

### 3. Build and start the containers

```bash
docker compose up -d --build
```

Check the containers:

```bash
docker compose ps
```

---

### 4. Apply migrations

```bash
docker compose exec web python manage.py migrate
```

---

### 5. Create an admin/superuser

```bash
docker compose exec web python manage.py createsuperuser
```

If the application uses the custom `role` field, ensure the appropriate user role is configured for administrative API access.

---

### 6. Run tests

```bash
docker compose exec web python manage.py test
```

---

## Useful Development Commands

Check the Django project:

```bash
docker compose exec web python manage.py check
```

View migrations:

```bash
docker compose exec web python manage.py showmigrations
```

Create migrations after model changes:

```bash
docker compose exec web python manage.py makemigrations
```

Apply migrations:

```bash
docker compose exec web python manage.py migrate
```

View container logs:

```bash
docker compose logs web
```

Stop the project:

```bash
docker compose down
```

---

## Development URLs

| Service | URL |
|---|---|
| API | `http://localhost:8000/` |
| Swagger UI | `http://localhost:8000/api/docs/` |
| OpenAPI Schema | `http://localhost:8000/api/schema/` |
| Django Admin | `http://localhost:8000/admin/` |

---

## Environment

The project is designed to run locally using Docker Compose with:

```text
Django
    │
    ▼
Web Container
    │
    ▼
PostgreSQL Container
```

Environment-specific secrets such as database passwords and Django's `SECRET_KEY` should be stored in `.env` rather than committed to source control.

---

## Testing

The project includes automated tests covering the main API functionality, including:

- Authentication and authorization
- Category permissions
- Category deletion protection
- Officer management
- Service request creation
- Service request visibility
- Officer assignment and reassignment
- Filtering
- Searching
- Ordering
- Pagination
- Administrative statistics
- Attachment uploads

Run the test suite with:

```bash
docker compose exec web python manage.py test
```

---

## API Design

The API follows REST-style conventions and uses HTTP methods according to the operation being performed:

```text
GET       → Retrieve data
POST      → Create data
PUT/PATCH → Update data
DELETE    → Delete data
```

Authentication is handled using JWT tokens, while authorization is enforced according to the user's role and relationship to the requested resource.

---

## License

This project is intended as an educational/software engineering project.
