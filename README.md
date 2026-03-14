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
python3 -m http.server 8000
```
Then visit `http://localhost:8000/index.html` or just `http://localhost:8000/`.

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

## 🐳 Running the System with Docker Compose (Recommended)

The entire Sansevieria distributed system has been containerized and can be launched locally using Docker Compose. This single command boots up:
- The Static **Frontend**
- The FastAPI **Backend**
- The **RabbitMQ** Message Broker & Workers
- The **Redis** Caching Layer
- The **Camunda** BPMN Orchestrator
- The **PostgreSQL** Database

### 1. Build and Start the System
From the root of the project repository (where `docker-compose.yml` is located), simply run:
```bash
docker compose up --build -d
```
All images will be built and downloaded. The services will communicate natively across an internal bridge network (`sansevieria-net`).

### 2. Available Services URL Map
Once the services are booted, they are mapped securely to your localhost:
- **Frontend App**: [http://localhost:8081](http://localhost:8081)
- **FastAPI Backend Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **RabbitMQ Management UI**: [http://localhost:15672](http://localhost:15672) *(guest / guest)*
- **Camunda BPMN Cockpit**: [http://localhost:8080/camunda](http://localhost:8080/camunda) *(demo / demo)*

### 3. Inspecting Logs
To cleanly monitor the distributed traces and error fault handling inside the workers:
```bash
# View all container aggregation logs
docker compose logs -f

# View specifically the worker node output
docker compose logs -f worker

# View the API backend
docker compose logs -f backend
```

### 4. Simulating Distributed Network Failures
You can natively test Circuit Breakers, Exponential Backoffs, and DLQs natively through Docker. 
1. The `.env` file at the root handles shared environment variables.
2. Edit `.env` to map `SIMULATE_PAYMENT_FAILURE=true`.
3. Restart the specific container: `docker compose up -d`
4. Use Swagger or the app to place an order and watch the `docker compose logs -f worker` explicitly trip!

### 5. Stopping the Environment
To gracefully shred memory, orchestrator overlays, and exit containers:
```bash
docker compose down
```
