# Sansevieria Web Application 🌿


Welcome to the Sansevieria frontend project! This is a static HTML/CSS web application dedicated to the cataloging, care, and commerce of Sansevieria (Snake Plants).

## Project Overview

The project consists of multiple statically defined HTML pages, styled with modern utility classes (Tailwind CSS format). It also includes custom Python utility scripts designed to perform bulk structural updates across the codebase, ensuring consistency across all pages.

### Key Pages
- `index.html` — The main landing/home page.
- `catalog.html` — The product catalog.
- `cart.html` & `checkout.html` — E-commerce shopping flow.
- `care.html`, `blog.html`, `problems.html`, `varieties.html` — Informational and guide pages.
- `dashboard.html`, `auth.html` — User profile and authentication views.

### Python Utility Scripts

To keep the static HTML files maintainable, several python scripts are provided in the `frontend/` directory:

- **`update_headers.py`**: Rewrites the `<header>` block in all `.html` files, ensuring that the top navigation bar is identical and updated everywhere.
- **`update_links.py`**: Uses Regular Expressions to traverse the HTML files and update placeholder hrefs (`href="#"`) and `<button>` elements to properly mapped internal semantic links.
- **`update_fonts.py`** & **`fix_links.py`**: Additional batch-processing utilities for styling and link structures.

## Usage

### Viewing the Site
You can open any `.html` file directly in your browser, or spin up a local development server for a better experience:

```bash
cd frontend
python3 -m http.server 8081
```
Then visit `http://localhost:8081/index.html` or just `http://localhost:8081/`.

### Running Updates
If you decide to change the global header structure, edit the raw HTML block located inside `frontend/update_headers.py` and execute the script:

```bash
python3 frontend/update_headers.py
```

To automatically link up new placeholder buttons or correct routing changes across the site:

```bash
python3 frontend/update_links.py
```

---

## � Deployment & Testing Guide

The Sansevieria distributed system utilizes a microservice architecture communicating via asynchronous queues and stateful orchestrators. 

### 1. System Requirements
- **Docker** and **Docker Compose** installed globally.
- Ensure ports `8000`, `8080`, `8081`, `5432`, `5672`, `15672`, and `6379` are available.
- *(Optional)* Python 3.10+ if running directly outside containers natively.

### 2. Setup Instructions
1. Clone the repository and navigate to the project root.
2. Ensure you have the `.env` file present at the root:
    ```dotenv
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=sansevieria
    SIMULATE_PAYMENT_FAILURE=false
    ```

### 3. Docker Compose Usage (Recommended)
You can launch the entire stack uniformly natively!
```bash
docker compose up --build -d
```
This builds and seamlessly interconnects the static frontend, FastAPI backend, AMQP python worker node, PostgreSQL, RabbitMQ, Redis, and the Camunda engine automatically across `sansevieria-net`.

### 4. Running Backend and Workers (Without Docker)
If you prefer running the Python scripts locally outside of Docker Compose:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start API
uvicorn app.main:app --reload

# Start Background AMQP/Camunda Polling Worker
export PYTHONPATH=.
python app/messaging/worker.py
```

### 5. Accessing Services (URL Map)
Once running natively via Docker Compose, navigate to these bound addresses:
- **Frontend App**: [http://localhost:8081](http://localhost:8081)
- **FastAPI Backend Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **RabbitMQ Management UI**: [http://localhost:15672](http://localhost:15672) *(guest / guest)*
- **Camunda BPMN Cockpit**: [http://localhost:8080/camunda](http://localhost:8080/camunda) *(demo / demo)*

### 6. Testing Features

You can natively test all enterprise microservice components identically relying directly on the interactive **FastAPI Swagger Docs** (`http://localhost:8000/docs`):

#### A. Checkout & Messaging
1. **Trigger**: Send a `POST /api/checkout` uniformly via Swagger.
2. **Result**: The API instantly replies `{"status": "PENDING"}` asynchronously!
3. **Verify Messaging**: Navigate to `http://localhost:15672` (RabbitMQ UI), select "Queues", and explicitly witness the throughput dynamically crossing `order_processing_queue`!

#### B. Workflow Orchestration
1. **Watch Camunda**: After mapping the checkout API call, open `http://localhost:8080/camunda` (demo/demo).
2. Go to `Cockpit > Processes > Order Fulfillment Process`.
3. You will natively witness active token badges tracking tasks (`Validate Order` -> `Process Payment` -> `Gateway`...) cleanly marching synchronously!

#### C. Redis Caching
1. Perform a `GET /api/products` via Swagger. 
2. Look at the `Server response time` inside Swagger visually. The first loop natively hits PostgreSQL generating ~20ms-50ms bounds.
3. Call identically immediately again! The cache intercepts execution dropping times natively `<3ms`!

#### D. Fault Handling
1. Edit the root `.env` to logically trap execution: `SIMULATE_PAYMENT_FAILURE=true`.
2. Apply changes natively: `docker compose up -d`.
3. Hit `POST /api/checkout`.
4. Open your terminal explicitly tailing logs dynamically: `docker compose logs -f worker` natively. 
5. You will cleanly watch the worker `[WARNING]` logs explicitly exponential backoff (Retry 1.. Retry 2), finally explicitly triggering the `Circuit Breaker OPEN` trace bounds, rejecting implicitly safely routing tokens directly onto the `order_processing_dlq` Dead Letter Queue natively!

### 7. Troubleshooting
- **Ports already in use?** If execution fails mapping `8080`, ensure Tomcat or local Postgres aren't already running inherently externally. Modify mapping mappings explicitly inside `docker-compose.yml`.
- **Worker logs show `ConnectionRefusedError` against RabbitMQ?** Ensure RabbitMQ fully initialized inherently. Docker's `depends_on` handles ordering, but AMQP explicitly cleanly restarts iteratively natively backing off natively.
- **Camunda process missing?** The Python worker handles orchestration automatically dynamically. However natively, if the engine refuses deployment natively, manually `POST /engine-rest/deployment/create` utilizing the `.bpmn` diagram natively mapping.
- **Restarting Fresh**: To completely clear the system implicitly flushing Redis explicitly and deleting Postgres bounds: `docker compose down -v`.
