# 🍔 FastTable - Restaurant Management API

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128%2B-00a393?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-316192?logo=postgresql&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Payments-635BFF?logo=stripe&logoColor=white)
![WebSockets](https://img.shields.io/badge/WebSockets-Real%20Time-black)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Coverage](https://img.shields.io/badge/Coverage-80%25-brightgreen)

A highly scalable, production-ready, fully asynchronous REST API for managing modern restaurant operations, featuring automated Stripe checkout, real-time WebSocket notifications, SQL-driven analytics, and automated digital receipts.

🌐 **Live Production API Documentation:** [https://fast-table-api.onrender.com/docs](https://fast-table-api.onrender.com/docs)

---

## ✨ Core Business Features

* 🍽️ **Menu Management:** Complete CRUD operations for Food Categories and Dishes.
* 🛒 **Order Processing (ACID Compliant):** Complex transactional logic to handle Orders and Order Items with strict database rollbacks on failures.
* 💳 **Stripe Payment Gateway:**
  * Hosted Stripe Checkout Session generation (`POST /payments/checkout-session`).
  * Public, secure Webhook endpoint (`POST /payments/webhook`) with cryptographic signature verification (`stripe-signature`).
  * Idempotency and race condition prevention using PostgreSQL row-level locks (`SELECT ... FOR UPDATE`).
  * Automatic state transition to `paid`.
* 🔔 **Real-Time Kitchen Notifications:** Integrated **WebSockets** to broadcast new incoming orders and instant payment notifications to kitchen/cashier displays.
* 📊 **Admin Analytics Dashboard:** High-performance native SQL aggregation queries (`SUM`, `COUNT`, `AVG`, `GROUP BY`) for sales summaries, top 5 selling dishes, and reservation metrics.
* 🧾 **Digital Email Receipts:** Non-blocking async HTML receipt delivery using `aiosmtplib` and FastAPI `BackgroundTasks`.
* 📅 **Table Reservations:** Booking system integrated with background email confirmations.
* 🔐 **Strict RBAC & Security:**
  * Role-Based Access Control (`Admin`, `Waiter`, `Client`) via custom FastAPI dependency injection.
  * Primary keys powered by `UUIDv4` to prevent IDOR attacks.
  * Argon2 password hashing (`pwdlib`) and JWT authentication.

---

## 🛠️ Tech Stack & Architecture

* **Framework:** FastAPI
* **Package Manager:** `uv` (Astral)
* **Database:** PostgreSQL (Production on Render) / SQLite In-Memory (Testing)
* **ORM:** SQLModel & SQLAlchemy 2.0 (`asyncpg`)
* **Payments:** Stripe SDK (`stripe`)
* **Async Emailing:** `aiosmtplib`
* **Real-Time:** WebSockets
* **Testing:** Pytest & HTTPX (80% Total Coverage, 18/18 passing)
* **Infrastructure:** Docker, Docker Compose, Render Cloud, GitHub Actions (CI/CD)

---

## 🚀 Getting Started (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/luisAndres34/fast-table-api.git
cd fast-table-api
```

### 2. Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

### 3. Spin up Infrastructure with Docker
```bash
docker compose up -d
```

### 4. Run Database Migrations
```bash
docker compose exec api uv run alembic upgrade head
```

### 5. Create Default Superuser (Admin)
```bash
docker compose exec api uv run python create_superuser.py
```

---

## 🧪 Running Tests & Coverage

Execute the automated test suite with in-memory SQLite and Stripe mocks:

```bash
docker compose exec api uv run pytest --cov=app --cov-report=term-missing
```

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.