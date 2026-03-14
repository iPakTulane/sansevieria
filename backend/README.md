# Sansevieria Backend API

This is the backend foundation for the Sansevieria web application, built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**.

## Tech Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Migrations:** Alembic

---

## 🚀 Setup Instructions

### 1. Prerequisites
Ensure you have **Python 3.10+** and **PostgreSQL** installed.

### 2. Database Configuration
1. Start your local PostgreSQL server.
2. Create a new database named `sansevieria`:
   ```bash
   psql -U postgres -c "CREATE DATABASE sansevieria;"
   ```
3. Update the connection string in the `.env` file if your PostgreSQL user/password differs from the default (`postgres:postgres`).

### 3. Install Dependencies
It's recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Database Migrations (Alembic)
To initialize and apply the database schema, run:
```bash
# Optional: Initialize alembic if the migrations folder is empty
# alembic init migrations

# The application is currently set to auto-create tables via SQLAlchemy Base.metadata.create_all
# To handle schema cleanly with alembic over time:
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```
*(Note: SQLAlchemy in `main.py` is currently configured to automatically generate the tables on startup for ease of initial development).*

### 5. Running the API
Start the FastAPI development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The server will be available at: http://localhost:8000

---

## 📚 API Documentation & Testing
FastAPI automatically generates interactive OpenAPI documentation. You can test all endpoints directly from your browser!

1. Start the API server as described above.
2. Navigate to: **[http://localhost:8000/docs](http://localhost:8000/docs)**
3. Use the **Authorize** button at the top right to log in (after registering a user) to access protected Cart and Order endpoints.

**Available Endpoints:**
- `POST /api/auth/register` - Create a new user
- `POST /api/auth/login` - Authenticate and receive a JWT token
- `GET /api/products` - List products
- `GET /api/products/{id}` - Get product details
- `GET/POST/DELETE /api/cart` - Manage shopping cart items (Protected)
- `POST /api/checkout` - Convert the current cart into an Order (Protected)
- `GET /api/orders` - View order history (Protected)

---

## 🌐 Frontend Integration
The existing static frontend HTML pages can now be augmented to use `fetch()` or `Axios` calls against `http://localhost:8000/api/...`. No static routing changes are required.

---

## 🐇 Messaging Integration (RabbitMQ)

This project uses **RabbitMQ** to handle computationally heavy event tasks asynchronously via persistent durable queues (`order_processing_queue`, `email_notification_queue`).

### 1. Running RabbitMQ (Docker)
The easiest way to stand up the message broker is via Docker:
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
*(The UI becomes available at `http://localhost:15672` with credentials `guest/guest`)*

### 2. Running the Worker Process
In a fresh terminal (with the virtual environment activated), start the decoupled consumer service:
```bash
cd backend
export PYTHONPATH=.
python app/messaging/worker.py
```
This worker listens continuously and handles order status updates and mock-email notifications.

### 3. Demonstrating Asynchronous & Offline Processing
1. **Live Processing**: Submit a `POST /api/checkout` request with your server and worker running. Notice the immediate HTTP response, while the terminal running the worker prints subsequent "Processing" and "Email sending" tasks asynchronously.
2. **Offline Resilience**: Kill the python `worker.py` script. Submit another checkout request. The API remains responsive and returns immediately! 
3. **Recovery**: Navigate to `http://localhost:15672` and see the message waiting in the `order_processing_queue`. Restart the `worker.py` script, and it will immediately pull and process the backed-up message correctly proving offline resiliency.
