# DRF Library Practice

RESTful API for library management with book, user, and borrowing systems. Built with Django Rest Framework, JWT authentication, and automatic Swagger documentation.

---

## 📋 Description

The API allows you to:

- Manage the book collection (CRUD operations)
- Register users and manage authentication
- Create book borrowings with automatic inventory updates
- Track active and completed borrowings

---

## 🛠 Technologies

- Python 3.12
- Django 6.0.5
- Django Rest Framework 3.17.1
- Simple JWT 5.5.1 (authentication)
- drf-spectacular 0.29.0 (Swagger/OpenAPI documentation)
- SQLite (database)

---

## 📦 Installation

**1. Clone the repository:**

```bash
git clone https://github.com/Dmitriy527/DRF_Library_Practice.git
cd DRF_Library_Practice
```

**2. Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Create a `.env` file in the project root:**

```env
SECRET_KEY=your-secret-key-here
```

**5. Run migrations:**

```bash
python manage.py migrate
```

**6. Create a superuser:**

```bash
python manage.py createsuperuser
```

**7. Start the server:**

```bash
python manage.py runserver
```

---

## 🚀 API Endpoints

### 📚 Book Service

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/api/books/` | Add a new book | Staff only |
| `GET` | `/api/books/` | Get book list (with pagination) | Everyone (including unauthenticated) |
| `GET` | `/api/books/<id>/` | Get detailed book information | Everyone (including unauthenticated) |
| `PUT/PATCH` | `/api/books/<id>/` | Update a book (including inventory) | Staff only |
| `DELETE` | `/api/books/<id>/` | Delete a book | Staff only |

<details>
<summary>Example response for <code>GET /api/books/</code></summary>

```json
{
  "count": 15,
  "next": "http://localhost:8000/api/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "The Great Gatsby",
      "author": "F. Scott Fitzgerald",
      "cover": "HARD",
      "inventory": 5,
      "daily_fee": "2.50"
    },
    {
      "id": 2,
      "title": "To Kill a Mockingbird",
      "author": "Harper Lee",
      "cover": "SOFT",
      "inventory": 3,
      "daily_fee": "1.75"
    }
  ]
}
```

</details>

---

### 👤 User Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users/` | Register a new user |
| `POST` | `/api/users/token/` | Obtain JWT tokens |
| `POST` | `/api/users/token/refresh/` | Refresh JWT token |
| `GET` | `/api/users/me/` | Get profile |
| `PUT/PATCH` | `/api/users/me/` | Update profile |

<details>
<summary>Request examples</summary>

**Registration:**

```json
POST /api/users/
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123"
}
```

**Obtaining tokens:**

```json
POST /api/users/token/
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

</details>

---

### 📖 Borrowings Service

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `POST` | `/api/borrowings/` | Create a borrowing (inventory -= 1) | Authenticated users |
| `GET` | `/api/borrowings/` | Get borrowings with filtering (with pagination) | Authenticated users |
| `GET` | `/api/borrowings/<id>/` | Get a specific borrowing | Authenticated users |
| `POST` | `/api/borrowings/<id>/return/` | Return a book (inventory += 1) | Staff only |
| `PUT/PATCH` | `/api/borrowings/<id>/` | Update return date | Staff only |

**Filter parameters for `GET /api/borrowings/`:**

- `?user_id=<int>` — filter by user
- `?is_active=<bool>` — filter active/completed borrowings

<details>
<summary>Request and response examples</summary>

**Creating a borrowing:**

```json
POST /api/borrowings/
{
  "borrow_date": "2026-06-20",
  "expected_return": "2026-07-20",
  "book_id": 1,
  "user_id": 1
}
```

**Updating the return date (staff only):**

```json
PATCH /api/borrowings/1/
{
  "expected_return": "2026-08-01"
}
```

**Response for `GET /api/borrowings/`:**

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "borrow_date": "2026-06-19",
      "expected_return": "2026-06-19",
      "actual_return": null,
      "book_id": {
        "id": 1,
        "title": "Titanic",
        "author": "Jamse Kameron",
        "cover": "Hard",
        "inventory": 6,
        "daily_fee": "1.00"
      },
      "user_id": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe"
      }
    }
  ]
}
```

</details>

---

## 📚 API Documentation

- **Swagger UI:** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **OpenAPI Schema:** [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

## 🧪 Testing

```bash
# Run tests
python manage.py test

# With coverage
coverage run manage.py test
coverage report
```

---

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. For protected endpoints, add the token to the header:

```
Authorization: Bearer <your_access_token>
```

### User Roles

**Unauthenticated user:**
- Can view the book list and detailed book information

**Regular user:**
- Can borrow books, create borrowings, view their own borrowings

**Staff:**
- Full access to CRUD operations for books
- Can set the book return date (`actual_return`)
- Can change the expected return date (`expected_return`)
- Can edit borrowings
- Can view all borrowings from all users

---

## 📝 Pagination

The API uses pagination for book and borrowing lists:

- **Page size:** 7 items per page
- **Query parameter:** `?page=<page_number>`
- **Example:** `/api/books/?page=2`

---

## 📁 Project Structure

```
DRF_Library_Practice/
├── book/               # Book application
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── user/               # User application
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── borrowings/         # Borrowings application
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── DRF_Library_Practice/ # Main Django config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
└── .env.example
```

---

## 📞 Contacts

**Author:** [Dmitriy527](https://github.com/Dmitriy527)  
**Email:** dimkanividimka@gmail.com
