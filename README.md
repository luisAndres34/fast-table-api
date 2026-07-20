# 🍔 FastTable - Restaurant Management API

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-00a393?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-316192?logo=postgresql&logoColor=white)
![WebSockets](https://img.shields.io/badge/WebSockets-Real%20Time-black)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)

A highly scalable, fully asynchronous REST API for managing restaurant operations. 

## ✨ Core Business Features

* 🍽️ **Menu Management:** Complete CRUD operations for Food Categories and Dishes.
* 🛒 **Order Processing (ACID Compliant):** Complex transactional logic to handle Orders and Order Items. If a single item fails to save, the entire transaction is rolled back to prevent corrupted data.
* 📅 **Table Reservations:** Booking system integrated with FastAPI `BackgroundTasks` for non-blocking email confirmations.
* 🔔 **Real-Time Kitchen Notifications:** Integrated **WebSockets** to broadcast new incoming orders to the kitchen or bar instantly.
* 🔐 **Strict RBAC & Data Integrity:**
  * Uses Python `Enums` strictly for states (`OrderStatus`, `ReservationStatus`) and roles (`Admin`, `Waiter`, `Client`).
  * Endpoints dynamically protected based on staff levels.

## 🛠️ Tech Stack & Architecture

* **Framework:** FastAPI
* **Database:** PostgreSQL (Production) / SQLite (In-Memory for Testing)
* **ORM:** SQLModel & SQLAlchemy 2.0 (Asyncpg)
* **Real-Time:** WebSockets
* **Security:** UUIDs to prevent IDOR attacks, JWT Authentication, and Argon2 password hashing.
* **Infrastructure:** Docker, Docker Compose, and managed entirely by `uv`.

## 🚀 Getting Started (Docker Flow)

### 1. Clone the repository
```bash
git clone https://github.com/luisAndres34/fast-table-api.git
cd fast-table-api
```

### 2. Environment Variables
Create your local environment file by copying the example:
```bash
cp .env.example .env
```
*(No need to change anything for local development, it defaults to the included Docker network).*

### 3. Spin up the Infrastructure
Start the API, PostgreSQL database, and Redis cache in detached mode:
```bash
docker compose up -d
```

### 4. Run Database Migrations
Generate the tables using Alembic (runs securely inside the container):
```bash
docker compose exec api uv run alembic upgrade head
```

### 5. Create the Initial Admin User
Bootstrap your database with the first manager/admin account:
```bash
docker compose exec api uv run python create_superuser.py
```

## 📚 API Documentation & Testing

Once the server is running, explore the interactive documentation:
* **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 🧪 Running the Test Suite
This project features a robust asynchronous test suite achieving high coverage of the business logic. It uses an isolated SQLite database and mocks external services (like SMTP and Redis) for fast CI/CD execution.

```bash
docker compose exec api uv run pytest
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```