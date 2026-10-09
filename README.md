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



### User Dashboard

- Real-time dashboard summary
- Total transaction count
- Total successful amount spent
- Current month spending
- Available credit across saved credit cards
- Last 5 transactions
- Masked card numbers in dashboard results
- JWT-protected dashboard API
- Loading skeleton while dashboard data is fetched
- JWT error handling in the React dashboard

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
│   ├── Dockerfile
│   └── credit_card_payment_system.sql
│
├── django_backend/
│   ├── accounts/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── audit.py
│   │   ├── email_service.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── tests.py
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
│   │   ├── email_service.py
│   │   ├── fraud_service.py
│   │   ├── middleware.py
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
│   │   ├── dashboard_router.py
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
├── docs/
│   └── screenshots/
│       ├── Login.png
│       ├── Register.png
│       ├── Dashboard.png
│       ├── Add_card.png
│       ├── Make_Payment.png
│       ├── Transactions.png
│       ├── Admin_dashboard.png
│       ├── Django_admin_panel.png
│       ├── Docker_Desktop.png
│       ├── Fastapi_swagger.png
│       └── Postman_Testing.png
│
├── Postman_collection.json
├── docker-compose.yml
├── .gitignore
└── README.md
```



---



## 4. System Architecture



```text

                    ┌──────────────────────┐

                    │     React Frontend   │

                    │     + Tailwind CSS   │

                    └──────────┬───────────┘

                               │

              ┌────────────────┴────────────────┐

              │                                 │

              ▼                                 ▼

   ┌────────────────────┐             ┌────────────────────┐

   │ Django REST API    │             │ FastAPI Payment    │

   │ Authentication     │             │ Processing Service │

   │ Cards              │             │ Payment Simulation │

   │ Transactions       │             │ SUCCESS / FAILED   │

   │ Admin Operations   │             └─────────┬──────────┘

   └──────────┬─────────┘                       │

              │                                 │

              └────────────────┬────────────────┘

                               ▼

                    ┌──────────────────────┐

                    │       MySQL          │

                    │ Users                │

                    │ Cards                │

                    │ Transactions         │

                    │ Admin Operations     │

                    └──────────────────────┘

```



---



## 5. Database Schema



### Users



Stores application user information and authentication details.



| Field | Description |

|---|---|

| ID | Unique user identifier |

| Username | User login name |

| Email | Unique email address |

| Password | Encrypted password |

| Date Joined | Account creation date |



### Cards



Stores saved credit/debit card information without storing the actual card number.



| Field | Description |

|---|---|

| ID | Unique card identifier |

| User | Card owner |

| Card Type | Credit / Debit |

| Masked Card Number | Masked representation |

| Last Four Digits | Last four digits of card |

| Created At | Card creation timestamp |



### Transactions



Stores payment and transaction information.



| Field | Description |

|---|---|

| ID | Unique transaction identifier |

| User | Transaction owner |

| Card | Associated saved card |

| Amount | Payment amount |

| Status | PENDING / SUCCESS / FAILED |

| Failure Reason | Reason for failed transaction |

| Transaction Date | Transaction timestamp |



---



## 6. Authentication Flow



```text

Register

   ↓

User Account Created

   ↓

Login

   ↓

JWT Access Token + Refresh Token

   ↓

Protected API Requests

   ↓

Logout

   ↓

Refresh Token Blacklisted

```



Protected APIs require JWT authentication.



Example:



```http

Authorization: Bearer <access_token>

```



---



## 7. Payment Flow



```text

React Frontend

      ↓

FastAPI Payment API

      ↓

Create Transaction

      ↓

PENDING

      ↓

Payment Simulation

      ↓

 ┌───────────────┐

 │               │

 ▼               ▼

SUCCESS        FAILED

                 │

                 ▼

          Failure Reason

```



Payments start with a `PENDING` status and are finally updated to either `SUCCESS` or `FAILED`.



---



## 8. API Documentation

### FastAPI Swagger

FastAPI provides interactive Swagger/OpenAPI documentation:

```text
http://localhost:8001/docs
```

### Django REST API

The Django backend provides authentication, card management, role-based access control (RBAC), transaction management, filtering, CSV/PDF export, fraud detection, and system health monitoring APIs:

```text
http://localhost:8000/api/
```

Django and FastAPI API endpoints are fully tested through the automated test suites and the Postman collection.

---

## 9. Main API Operations

### 1. Authentication & Profile
```text
POST /api/register/       - Register new user
POST /api/login/          - JWT login (returns access, refresh, role)
POST /api/logout/         - JWT logout (blacklists refresh token)
GET  /api/profile/        - Protected user profile
```

### 2. Card Management & RBAC Operations
```text
POST   /api/cards/              - Add credit or debit card
GET    /api/cards/list/         - View saved cards (masked card numbers)
DELETE /api/cards/<id>/         - Delete saved card
POST   /api/cards/<id>/block/   - Block card (Admin / Support)
POST   /api/cards/<id>/unblock/ - Unblock card (Admin / Support)
PATCH  /api/cards/<id>/limit/   - Update credit limit (Admin only)
```

### 3. Role-Based Access Control (RBAC) & Audit Logs
```text
GET   /api/users/               - List users with roles (Admin / Support)
PATCH /api/users/<id>/role/     - Assign user role (Admin only)
GET   /api/audit-logs/          - View system audit log trail (filter by action, actor)
```

### 4. Transactions & History
```text
POST  /api/transactions/create/            - Create pending transaction (fraud & limit check)
PATCH /api/transactions/<id>/status/       - Update transaction status (SUCCESS / FAILED)
GET   /api/transactions/                   - Transaction history (with search, sort, filter, pagination)
GET   /api/transactions/dashboard/summary/ - Real-time dashboard transaction summary
```

### 5. Rule-Based Fraud Detection & Review
```text
GET   /api/transactions/fraud-logs/             - List detected fraud risk logs (Admin / Support)
PATCH /api/transactions/fraud-logs/<id>/review/ - Review fraud log (CONFIRMED / FALSE_POSITIVE / RESOLVED)
```

### 6. Analytics & Statement Exports
```text
GET /api/transactions/analytics/card-usage/  - Monthly spending, category expenses, credit utilization
GET /api/transactions/analytics/export/csv/  - Export card usage analytics summary to CSV
GET /api/transactions/analytics/export/pdf/  - Export card usage analytics summary to PDF
GET /api/transactions/export/csv/            - Export filtered transactions to CSV
GET /api/transactions/monthly-statement/     - Export user monthly statement to PDF
```

### 7. System Health & Performance Monitoring
```text
GET /api/system/health/   - Real-time DB latency, error rates, slow requests, HTTP status metrics
```

### 8. FastAPI Payment Processing Gateway
```text
POST /payments/           - Process payment simulation via FastAPI
POST /auth/register       - FastAPI Gateway user registration
POST /auth/login          - FastAPI Gateway JWT login
GET  /auth/profile        - FastAPI Gateway user profile
POST /cards/              - FastAPI Gateway card creation
GET  /cards/              - FastAPI Gateway card listing
DELETE /cards/<id>        - FastAPI Gateway card deletion
GET  /dashboard/summary   - FastAPI Gateway dashboard summary
```

---

## 10. Postman Collection

The comprehensive Postman collection is available in the project root:

[Postman Collection](Postman_collection.json)

The collection is organized into 8 modular folders containing **44 total requests** with automated test scripts and collection variables:

1. **FastAPI Gateway (Port 8001)**: Registration, JWT login, profile, card management, payments (success & simulation failure), dashboard summary, Swagger docs.
2. **Django REST API - Authentication (Port 8000)**: Registration, JWT login, protected profile, token blacklist logout.
3. **Django REST API - Card Management**: Add credit card, add debit card, list saved cards, delete card.
4. **Django REST API - RBAC & Admin Ops**: List users & roles, update user roles, block card, unblock card, update credit limit, inspect audit logs, filter audit logs by action.
5. **Django REST API - Transactions & History**: Create pending transaction, update status, complete history, filter by status, amount range, date range, category, search by card digits, server pagination & sorting, dashboard summary.
6. **Django REST API - Fraud Detection**: List flagged fraud logs, review fraud status (`CONFIRMED`, `FALSE_POSITIVE`, `RESOLVED`).
7. **Django REST API - Analytics & Exports**: Card usage analytics API, analytics CSV export, analytics PDF export, filtered transactions CSV export, monthly statement PDF generation.
8. **Django REST API - System Health & Metrics**: Database latency, uptime status, API metric logs, error rates.

**Collection Variables Included:**
- `django_base_url`: `http://localhost:8000`
- `fastapi_base_url`: `http://localhost:8001`
- `access_token` & `refresh_token`: Automatically captured and refreshed upon running any Login request.
- `card_id`, `transaction_id`, `user_id`, `fraud_log_id`: Auto-captured or configured for chaining requests.



---



## 11. Running the Project with Docker



Make sure Docker Desktop is running.



From the project root:



```bash

docker compose up --build

```



To run the containers in detached mode:



```bash

docker compose up -d --build

```



To check running containers:



```bash

docker compose ps

```



To stop the project:



```bash

docker compose down

```



> Do not use `docker compose down -v` unless you intentionally want to remove Docker volumes and database data.



---



## 12. Application Services



The project consists of:



```text

Frontend

Django Backend

FastAPI Payment Service

MySQL Database

```



The service configuration and ports are defined in:



```text

docker-compose.yml

```



---



## 13. Local Development



### Django Backend



```bash

cd django_backend

python manage.py migrate

python manage.py runserver

```



### FastAPI Backend



```bash

cd fastapi_payment

uvicorn main:app --reload

```



### Frontend



```bash

cd frontend

npm install

npm run dev

```



---



## 14. Testing



### Django Tests



```bash

cd django_backend

python manage.py test

```



### FastAPI Tests

```bash
cd fastapi_payment
python -m unittest discover tests
```

To run with coverage:

```bash
cd fastapi_payment
coverage run -m unittest discover tests
coverage report
```

The project contains tests covering authentication, card management, transactions, payment API behaviour, and payment service functionality.

---

## 15. Security

The application follows the required security rules:

- CVV is not stored
- Actual card numbers are not stored
- Passwords are encrypted
- JWT authentication is used
- Protected routes require authentication
- Input validation is implemented
- Django ORM is used for database access
- Transaction ownership is validated
- Refresh-token blacklisting is implemented during logout

---

## 16. Admin Panel

The Django administration interface provides:

- User management
- Card management
- Transaction management
- Payment summary
- Administrative operations

Admin URL:

```text
http://localhost:8000/admin/
```

---

## 17. Screenshots

### Login

![Login](docs/screenshots/Login.png)

### Register

![Register](docs/screenshots/Register.png)

### Dashboard

![Dashboard](docs/screenshots/Dashboard.png)

### Add Card

![Add Card](docs/screenshots/Add_card.png)

### Make Payment

![Make Payment](docs/screenshots/Make_Payment.png)

### Transactions

![Transactions](docs/screenshots/Transactions.png)

### Admin Dashboard

![Admin Dashboard](docs/screenshots/Admin_dashboard.png)

### Django Admin Panel

![Django Admin Panel](docs/screenshots/Django_admin_panel.png)

### Docker Desktop

![Docker Desktop](docs/screenshots/Docker_Desktop.png)

### FastAPI Swagger

![FastAPI Swagger](docs/screenshots/Fastapi_swagger.png)

### Postman Testing

![Postman Testing](docs/screenshots/Postman_Testing.png)

---

## Task 1 – User Dashboard With Transaction Summary

The dashboard implementation provides the required real-time transaction summary through FastAPI and Django.

### Backend

```text
GET /dashboard/summary
```

The endpoint is JWT protected and returns transaction count, successful spending totals, current-month spending, available credit, and the latest five transactions.

Database access uses `SUM(amount)` for spending aggregation and a limited query for the latest five transactions.

### Frontend

The React dashboard includes:

- Four statistic cards
- Last 5 transactions list
- Saved card information and credit limits
- Loading skeleton during API fetch
- JWT error handling

### Verification

The dashboard endpoint was tested through Postman and returned HTTP 200 with all required fields. The Postman dashboard test collection reports 3/3 passing tests.

---

## 18. GitHub Repository

GitHub Repository:

https://github.com/arunaru1515-glitch/credit-card-payment-system



---



## 19. Project Requirements Coverage



| Module | Status |

|---|---|

| User Authentication | Completed |

| Card Management | Completed |

| Payment Processing | Completed |

| Transaction Management | Completed |

| Admin Panel | Completed |

| React Frontend | Completed |

| MySQL Database | Completed |

| Security Requirements | Completed |

| API Documentation | Completed |

| Docker Deployment | Completed |

| Testing | Completed |

| Git & Documentation | Completed |



---



## 20. Final Submission



The project includes:



- GitHub repository

- Docker configuration

- Postman collection

- UI screenshots

- Django Admin screenshot

- FastAPI Swagger screenshot

- Docker running screenshot

- Project documentation

---

## 21. Assessment Deliverables (EOD Release)

### 1. Role-Based Access Control (RBAC) & Audit Logs
- **Roles Implemented**:
  - `ADMIN`: Full access to user role management, credit limits, card deletion, fraud alert reviews, audit logs, system monitoring.
  - `SUPPORT`: Card block/unblock, view transactions, inspect audit logs, review fraud alerts. Cannot alter credit limits or delete cards.
  - `READ_ONLY`: Full read/inspection rights for transactions, cards, analytics, and audit logs. All write/mutating operations are denied (`403 Forbidden`).
  - `CUSTOMER`: Standard customer operations restricted to own cards and transactions.
- **Role Permission Checks**:
  - `POST /api/cards/` (Customer, Admin; blocked for Read-Only)
  - `DELETE /api/cards/<id>/` (Admin for any, Customer for own; blocked for Support & Read-Only)
  - `POST /api/cards/<id>/block/` & `/unblock/` (Admin & Support only)
  - `PATCH /api/cards/<id>/limit/` (Admin only)
  - `GET /api/audit-logs/` (Admin, Support, Read-Only)
- **Audit Logging Structure**:
  - Tracks `actor`, `action` (`CARD_BLOCK`, `CARD_UNBLOCK`, `CREDIT_LIMIT_UPDATE`, `ROLE_UPDATE`, `CARD_DELETE`), `target_type`, `target_id`, `description`, `old_value`, `new_value`, `ip_address`, and timestamp.

### 2. Rule-Based Fraud Detection & Alerting
- **Engine Rules**:
  1. **Multiple High-Value Transactions in Short Time**: Detects burst spending where multiple transactions exceed ₹10,000 within a 10-minute window or cumulative spending exceeds ₹25,000 (`HIGH` risk).
  2. **Rapid Transactions from Different Locations / Devices**: Flags rapid subsequent transactions initiated within 15 minutes with mismatched geographical locations or devices (`HIGH`/`MEDIUM` risk).
  3. **Velocity Surge Detection**: Flags high frequency (>3 transactions within 2 minutes).
- **Fraud Status & Audit**:
  - Transaction field `fraud_status`: `CLEAN`, `SUSPICIOUS`, `FLAGGED`, `BLOCKED`.
  - Database model `FraudLog`: Stores attempt details, risk level, rules triggered, IP address, and location.
  - Asynchronous background email alerting (`send_fraud_alert_email`).
  - Staff management endpoints:
    - `GET /api/transactions/fraud-logs/`
    - `PATCH /api/transactions/fraud-logs/<id>/review/` (Status: `CONFIRMED`, `FALSE_POSITIVE`, `RESOLVED`)

### 3. Analytics & Search Optimization
- **Card Usage Analytics API** (`/api/transactions/analytics/card-usage/`):
  - **Monthly Spending Summary**: Complete 12-month spending trend and transaction volumes.
  - **Category-Wise Expense Data**: Category distribution across `Groceries`, `Dining`, `Shopping`, `Utilities`, `Travel`, `Entertainment`, `Healthcare`, `General`, with percentage share.
  - **Credit Utilization Percentage**: Overall utilization % across credit lines and per-card breakdown.
- **Advanced Transaction Search & Filtering**:
  - Date Range (`start_date`, `end_date`)
  - Amount Range (`min_amount`, `max_amount`)
  - Status Filter (`status`)
  - Category Filter (`category`)
  - Masked Card / Last 4 Digits Search (`search`)
  - Server-Side Sorting (`sort_by`: `transaction_date`, `-transaction_date`, `amount`, `-amount`)
  - Server-Side Pagination (`page`, `page_size`)
- **Query Optimization**:
  - Composite indexes on `[user, -transaction_date]`, `[status, -transaction_date]`, `[category, -transaction_date]`, and `[fraud_status]`.
  - Efficient queries using `select_related('card', 'user')` and database aggregations.

### 4. System Health Monitoring & Data Export
- **Monitoring Middleware & Database Auditing**:
  - `SystemMonitoringMiddleware` logs response times, status codes, endpoints, and client IPs into `APIMetricLog`.
  - Unhandled errors and failure logs tracked.
- **System Health API** (`/api/system/health/`):
  - Database connectivity test & latency (ms).
  - Average API response time and failure rate percentage.
  - Status code breakdown (2xx, 4xx, 5xx) and slow request count (>500ms).
- **Export Options**:
  - Analytics Summary to PDF: `GET /api/transactions/analytics/export/pdf/`
  - Analytics Summary to CSV: `GET /api/transactions/analytics/export/csv/`
  - Filtered Transactions to CSV: `GET /api/transactions/export/csv/`
  - Monthly Statement to PDF: `GET /api/transactions/monthly-statement/`
- **Frontend Enhancements**:
  - Interactive charts (monthly bar chart, category distribution, credit utilization gauge) in user dashboard.
  - Live system health monitor, fraud alert review actions, and export buttons in admin dashboard.
  - Advanced search filters, pagination controls, and CSV export in transaction history.