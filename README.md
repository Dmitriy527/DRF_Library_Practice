# DRF Library Practice

RESTful API для управління бібліотекою з системами книг, користувачів та позик. Побудовано на Django Rest Framework з JWT аутентифікацією та автоматичною документацією Swagger.

---

## 📋 Опис

API дозволяє:

- Керувати книжковим фондом (CRUD операції)
- Реєструвати користувачів та керувати аутентифікацією
- Оформлювати позики книг з автоматичним оновленням інвентаря
- Відстежувати активні та завершені позики

---

## 🛠 Технології

- Python 3.12
- Django 6.0.5
- Django Rest Framework 3.17.1
- Simple JWT 5.5.1 (аутентифікація)
- drf-spectacular 0.29.0 (Swagger/OpenAPI документація)
- SQLite (база даних)

---

## 📦 Встановлення

**1. Клонуйте репозиторій:**

```bash
git clone https://github.com/Dmitriy527/DRF_Library_Practice.git
cd DRF_Library_Practice
```

**2. Створіть та активуйте віртуальне середовище:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows
```

**3. Встановіть залежності:**

```bash
pip install -r requirements.txt
```

**4. Створіть файл `.env` в корені проекту:**

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**5. Виконайте міграції:**

```bash
python manage.py migrate
```

**6. Створіть суперкористувача:**

```bash
python manage.py createsuperuser
```

**7. Запустіть сервер:**

```bash
python manage.py runserver
```

---

## 🚀 API Ендпоінти

### 📚 Book Service

| Метод | Ендпоінт | Опис | Доступ |
|-------|----------|------|--------|
| `POST` | `/api/books/` | Додати нову книгу | Тільки персонал |
| `GET` | `/api/books/` | Отримати список книг (з пагінацією) | Всі (включаючи неавторизованих) |
| `GET` | `/api/books/<id>/` | Отримати детальну інформацію про книгу | Всі (включаючи неавторизованих) |
| `PUT/PATCH` | `/api/books/<id>/` | Оновити книгу (включаючи інвентар) | Тільки персонал |
| `DELETE` | `/api/books/<id>/` | Видалити книгу | Тільки персонал |

<details>
<summary>Приклад відповіді <code>GET /api/books/</code></summary>

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

| Метод | Ендпоінт | Опис |
|-------|----------|------|
| `POST` | `/api/users/` | Реєстрація нового користувача |
| `POST` | `/api/users/token/` | Отримати JWT токени |
| `POST` | `/api/users/token/refresh/` | Оновити JWT токен |
| `GET` | `/api/users/me/` | Отримати профіль |
| `PUT/PATCH` | `/api/users/me/` | Оновити профіль |

<details>
<summary>Приклади запитів</summary>

**Реєстрація:**

```json
POST /api/users/
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword123"
}
```

**Отримання токенів:**

```json
POST /api/users/token/
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Відповідь:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

</details>

---

### 📖 Borrowings Service

| Метод | Ендпоінт | Опис | Доступ |
|-------|----------|------|--------|
| `POST` | `/api/borrowings/` | Оформити позику (інвентар -= 1) | Авторизовані користувачі |
| `GET` | `/api/borrowings/` | Отримати позики з фільтрацією (з пагінацією) | Авторизовані користувачі |
| `GET` | `/api/borrowings/<id>/` | Отримати конкретну позику | Авторизовані користувачі |
| `POST` | `/api/borrowings/<id>/return/` | Повернути книгу (інвентар += 1) | Тільки персонал |
| `PUT/PATCH` | `/api/borrowings/<id>/` | Оновити дату повернення | Тільки персонал |

**Параметри фільтрації для `GET /api/borrowings/`:**

- `?user_id=<int>` — фільтр по користувачу
- `?is_active=<bool>` — фільтр активних/завершених позик

<details>
<summary>Приклади запитів та відповідей</summary>

**Створення позики:**

```json
POST /api/borrowings/
{
  "borrow_date": "2026-06-20",
  "expected_return": "2026-07-20",
  "book_id": 1,
  "user_id": 1
}
```

**Оновлення дати повернення (тільки для персоналу):**

```json
PATCH /api/borrowings/1/
{
  "expected_return": "2026-08-01"
}
```

**Відповідь `GET /api/borrowings/`:**

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

## 📚 Документація API

- **Swagger UI:** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **OpenAPI Schema:** [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)

---

## 🧪 Тестування

```bash
# Запуск тестів
python manage.py test

# З покриттям
coverage run manage.py test
coverage report
```

---

## 🔐 Аутентифікація

API використовує JWT (JSON Web Tokens). Для захищених ендпоінтів додайте токен в заголовок:

```
Authorization: Bearer <your_access_token>
```

### Ролі користувачів

| Роль | Можливості |
|------|-----------|
| **Неавторизований** | Перегляд списку книг та детальної інформації |
| **Звичайний користувач** | Оформлення позик, перегляд своїх позик |
| **Staff (персонал)** | Повний CRUD для книг, управління всіма позиками, внесення дати повернення, перегляд позик всіх користувачів |

---

## 📝 Пагінація

API використовує пагінацію для списків книг та позик:

- **Page size:** 7 елементів на сторінку
- **Параметр запиту:** `?page=<номер_сторінки>`
- **Приклад:** `/api/books/?page=2`

---

## 📁 Структура проекту

```
DRF_Library_Practice/
├── book/               # Додаток книг
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── user/               # Додаток користувачів
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── borrowings/         # Додаток позик
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── DRF_Library_Practice/ # Основний конфіг Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
└── .env.example
```

---

## 📞 Контакти

**Автор:** [Dmitriy527](https://github.com/Dmitriy527)  
**Email:** dimkanividimka@gmail.com
