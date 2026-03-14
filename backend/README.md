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

---

## 🔗 Stateful Processing & Correlation Mechanism

To support reliable distributed architectures and concurrent processes, this backend employs **Correlation Identifiers**:

### Correlation ID (`order_id`)
The business identifier format (e.g., `ORD-000123`) is strictly utilized as the primary correlation key across:
- **API Requests**: Generated at checkout and bundled into HTTP responses.
- **Queue Messages**: Bundled in JSON payloads *and* explicitly as RabbitMQ Message Headers (`correlation_id`).
- **Database Records**: Serves as the primary unique key reference (`Order.order_id`).
- **Logging Traceability**: Required structure inside all worker prints: `[ORDER_PROCESSOR] correlation_id=ORD-000123 status=PROCESSING`.

### Order State Machine
Orders enforce strict lifecycle states using `services/order_state_service.py`:
- `PENDING` -> `PROCESSING` -> `COMPLETED`
- `[ANY]` -> `FAILED`

### Concurrency & Idempotency
1. **Row-level Locking**: The state machine operates using SQLAlchemy's `with_for_update()`. This protects against multiple workers grabbing the exact same order instance simultaneously (pessimistic locking) and ensures transitions are strictly atomic.
2. **Idempotency**: The state processor validates transitions before saving to DB. Therefore, redundant or out-of-order messages arriving at the consumer are caught and discarded cleanly instead of crashing the system.

---

## 🗺 Business Process Orchestration (Camunda BPMN)

The Order Fulfillment Process is now managed as a formal diagrammatic orchestration flow using **Camunda Platform 7**.

### 1. The BPMN Workflow (`order_fulfillment.bpmn`)
When a user begins the checkout, the system no longer executes python code linearly. The following workflow instances are handled directly by Camunda:
1. `validate_order` (Service Task)
2. `process_payment` (Service Task)
3. `reserve_inventory` (Service Task)
4. A **Parallel Split Gateway** spanning:
    - `generate_shipment` (Service Task)
    - `generate_invoice` (Service Task)
5. **Parallel Merge Gateway** merging back the flow execution.
6. `send_confirmation` (Service Task) which fires an event payload into the `email_notification_queue`.

### 2. Running Camunda Engine (Docker)
In root or wherever docker is configured, start up standard Camunda 7 REST API server:
```bash
docker run -d --name camunda -p 8080:8080 camunda/camunda-bpm-platform:run-latest
```
*Wait ~1 minute for deployment* - The UI will spawn at `http://localhost:8080/camunda` (Demo login: `demo`/`demo`). You will need to manually upload (`POST http://localhost:8080/engine-rest/deployment/create`) or deploy `order_fulfillment.bpmn` via the Camunda Modeler desktop client.

### 3. Orchestration Mechanics & Correlation
Once the Camunda Server is deployed:
- When the RabbitMQ python Consumer sees an `ORDER_CREATED` event on its queue, instead of firing python logic, it issues an HTTP `start_process_instance` REST call to `http://localhost:8080/engine-rest/process-definition/key/OrderFulfillmentProcess/start`.
- The `order_id` is explicitly passed into the API as the `.businessKey` mapping the BPMN flow forever natively back to the Backend DB.
- At the exact same time, inside `worker.py`, a dedicated parallel thread (`WorkflowWorker.poll_loop()`) rapidly issues Long-Polling `fetchAndLock` requests to Camunda asking "What tasks are waiting?".
- Python code grabs available work blocks via task topics (e.g. `process_payment`), applies Python business logic, and hits `complete_task` returning state to the BPEL engine.
