# Credit Card Payment System

A full-stack Credit Card Payment System built using React, Django REST Framework, FastAPI, MySQL, and Docker.

The application supports secure user authentication, credit/debit card management, payment processing, transaction management, administrative operations, API documentation, automated testing, and Docker-based deployment.

---

## 1. Features

### User Authentication
- User registration
- JWT-based login
- JWT token authentication
- Logout with refresh-token blacklisting
- Protected user profile
- Encrypted password storage

### Card Management
- Add credit card
- Add debit card
- View saved cards
- Delete saved cards
- Card number masking
- Only masked card number and last four digits are stored
- CVV is not stored

### Payment Processing
- Payment processing through FastAPI
- Initial `PENDING` transaction status
- Simulated payment gateway processing
- `SUCCESS` payment status
- `FAILED` payment status
- Failure reason for declined payments

### Transaction Management
- View transaction history
- Filter by status
- Filter by minimum amount
- Filter by maximum amount
- Filter by date
- Transaction ownership protection
- Admin transaction management
- CSV export support

### Admin Panel
- Manage users
- Manage cards
- View transactions
- Daily payment summary
- Django administration interface

### Frontend
- Register
- Login
- Dashboard
- Add Card
- Make Payment
- Transaction History
- Admin Dashboard
- Responsive fintech-style UI

### API Documentation
- FastAPI Swagger UI
- OpenAPI documentation
- Protected API endpoints
- Postman testing support

### Testing
- Authentication tests
- Card management tests
- Transaction tests
- Payment API tests
- Payment service tests
- Django test coverage
- FastAPI test coverage

### Docker
- Dockerized Django backend
- Dockerized FastAPI backend
- Dockerized React frontend
- Dockerized MySQL database
- Docker Compose orchestration

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Tailwind CSS, Vite |
| Backend | Django, Django REST Framework |
| Payment Service | FastAPI |
| Database | MySQL |
| Authentication | JWT / Simple JWT |
| API Documentation | Swagger / OpenAPI |
| Testing | Django TestCase, unittest, coverage |
| Web Server | Nginx |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

---

## 3. Project Structure

```text
credit_card_payment_system/
│
├── database/
│   └── Dockerfile
│
├── django_backend/
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── config/
│   │   ├── asgi.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── transactions/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
│
├── fastapi_payment/
│   ├── routers/
│   │   ├── auth_router.py
│   │   ├── card_router.py
│   │   └── payment_router.py
│   │
│   ├── services/
│   │   └── payment_service.py
│   │
│   ├── tests/
│   │   ├── test_payment.py
│   │   └── test_payment_service.py
│   │
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── schemas.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml
├── .gitignore
└── README.md