# Sansevieria Developer Runbook

Welcome to the complete local setup guide for the **Sansevieria** application. This document provides step-by-step instructions to start the entire distributed system locally, ensuring that the backend infrastructure, messaging, orchestration, caching, and fault handling features all function smoothly.

---

## SECTION 1 — SYSTEM REQUIREMENTS

To run the Sansevieria system locally, ensure you have the following installed:

- **Python**: 3.10+
- **Docker** & **Docker Compose**
- **PostgreSQL**: (Can be run locally or via Docker)
- **Git**
- *(Optional)* **Node.js**: (If you plan to use modern frontend tooling later)

---

## SECTION 2 — PROJECT STRUCTURE OVERVIEW

The codebase is organized to separate frontend static assets from the complex microservice-style backend architecture:

- `frontend/` - Static HTML, CSS, Javascript files forming the UI.
- `backend/` - The FastAPI Python backend application.
  - `backend/app/messaging/` - RabbitMQ producer and consumer logic.
  - `backend/app/workflow/` - Camunda BPMN workflow configurations and workers.
  - `backend/app/cache/` - Redis data and output caching mechanisms.
  - `backend/app/utils/` - Shared utilities like structured logging, fault handlers, and decorators.

---

## SECTION 3 — ENVIRONMENT SETUP

Navigate to the `backend/` directory and set up your environment variables. 
Create or modify the `.env` file to include all essential external connections and logic flags:

```dotenv
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sansevieria

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Camunda Configuration
CAMUNDA_REST_URL=http://localhost:8080/engine-rest

# Fault Simulation (True to simulate a payment crash)
SIMULATE_PAYMENT_FAILURE=false
```

---

## SECTION 4 — START INFRASTRUCTURE

Use Docker to spin up the distributed architectural components. Run these commands from any terminal equipped with Docker:

**1. RabbitMQ (AMQP Message Broker)**
```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
*(Management UI available at `http://localhost:15672` | Login: `guest`/`guest`)*

**2. Redis (Enterprise Cache Layer)**
```bash
docker run -d --name cache-redis -p 6379:6379 redis:alpine
```

**3. Camunda Platform 7 (BPMN Engine)**
```bash
docker run -d --name camunda -p 8080:8080 camunda/camunda-bpm-platform:run-latest
```
*(Wait ~60 seconds for initialization. UI available at `http://localhost:8080/camunda` | Login: `demo`/`demo`)*

**4. PostgreSQL** *(If missing a local native installation)*
```bash
docker run -d --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=sansevieria -p 5432:5432 postgres:15-alpine
```

---

## SECTION 5 — DATABASE INITIALIZATION

First, set up your Python environment and dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Start your backend application to run automatic SQLAlchemy migrations safely. No explicit Alembic seeding is needed to boot since `main.py` explicitly issues `Base.metadata.create_all()` initially mapping `User`, `Order`, `Product`, `Cart`, etc.

---

## SECTION 6 — START THE BACKEND

While still in the `backend/` directory, start the FastAPI API application:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **Live API Endpoint:** `http://localhost:8000/api`
- **Swagger Documentation:** `http://localhost:8000/docs` (Use this UI to explore OpenAPI endpoints, view schema inputs, and test authorizations explicitly).

---

## SECTION 7 — START WORKERS

Open a **new terminal tab**, navigate cleanly into `backend/`, and start the master worker process. 
This process seamlessly bridges polling the RabbitMQ consumer queues *and* executing the BPMN Camunda thread-poller loops:

```bash
cd backend
source venv/bin/activate
export PYTHONPATH=.
python app/messaging/worker.py
```
*(You should immediately see logs indicating connections to the RabbitMQ DLQs and starting Camunda task handlers)*.

---

## SECTION 8 — RUN FRONTEND

To serve the local static files, open a **third terminal**, jump into the root directory, and launch a simple HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Access the web portal locally at `http://localhost:8080`.
Currently, the HTML application mimics API calls utilizing generic fetch hooks, but a developer could hook real generic Axios configurations overriding the `base_url` directly back into `http://localhost:8000/api`.

---

## SECTION 9 — FUNCTIONAL TESTING

To simulate a complete functional user flow, utilize the Swagger UI (`http://localhost:8000/docs`):

1. **User Registration:**
   - POST to `/api/auth/register`. Input an email, name, and password.
2. **Product Catalog Retrieval:**
   - GET `/api/products` (Loads inventory, warming the Redis cache).
3. **Cart Operations:** 
   - Use Auth "Authorize" lock (Log in yielding a JWT).
   - POST `/api/cart` passing a `product_id` and `quantity`.
4. **Checkout Process:**
   - POST `/api/checkout`. 
   - Notice that the API immediately returns `{ "status" : "PENDING" }` decoupling heavy processes!

---

## SECTION 10 — VERIFY ASYNCHRONOUS PROCESSING

After executing checkout:

1. Look closely at your running FastAPI terminal: A log should denote that it `[ORDER_PROCESSOR]` fired an `ORDER_CREATED` object across RabbitMQ reliably utilizing the `correlation_id`.
2. Head gracefully to `http://localhost:15672` (RabbitMQ UI) and peek at `order_processing_queue`.
3. Switch focus quickly to the **Worker Terminal**: 
   - Watch the consumer process dynamically digest the message, jumpstart Camunda logic, walk step-by-step applying Python rules, then gracefully atomic lock state variables into PostgreSQL marking order state transitions `PROCESSING -> COMPLETED`.

---

## SECTION 11 — VERIFY WORKFLOW ORCHESTRATION

To deeply verify the BPMN mechanics visually:

1. Open `http://localhost:8080/camunda/app/cockpit/default/`. (Login: `demo`/`demo`).
2. Navigate to "Processes" -> `Order Fulfillment Process`.
3. If tasks are actively executing natively in Python locally while you sit here, you'll see tiny numbered visual badges atop the flowcharts tracking actual live instances traversing the Parallel gateways dynamically tracking explicit `order_id` values!

---

## SECTION 12 — VERIFY REDIS CACHING

1. Check Response Times explicitly inside the Swagger UI (`http://localhost:8000/docs`). 
2. Trigger the `GET /api/products` endpoint manually. The first request takes generally > 20ms pulling DB bindings natively.
3. Call it again immediately! Response headers will display <3ms since it hit `Redis`.
4. You can visually inspect the exact serialized Redis strings locally utilizing docker executing:
   ```bash
   docker exec -it cache-redis redis-cli
   > keys *
   > get "products:catalog"
   ```

---

## SECTION 13 — VERIFY FAULT HANDLING

Demonstrate DLQs, exponential back-offs, and Circuit breaker boundaries explicitly:

1. Kill the backend terminal and update your `.env`: `SIMULATE_PAYMENT_FAILURE=true`.
2. Restart the API Application `uvicorn` and restart the worker.
3. Queue up another POST `/api/checkout`. 
4. Check the **Worker log terminal**:
   - You will visibly witness structured logging warnings: `Operation failed, retrying attempt=1 delay=1` followed rapidly by exponential timeouts: `attempt=2 delay=2`, etc.
   - On Max Failure, the `payment_circuit_breaker` trips gracefully **OPEN** halting any additional process instances gracefully throwing `TimeoutException` bindings. 
   - At terminal failure, Camunda logic skips the hook. The Python AMQP consumer catches the fallback routing explicitly throwing an unrecoverable `Reject`.
   - The message automatically slides out of `order_processing_queue` directly into `order_processing_dlq` dynamically allowing a human developer to investigate later!
