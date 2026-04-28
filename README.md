# Sansevieria

Sansevieria is a plant e-commerce application with a static frontend and a FastAPI backend.
The project includes operational order processing plus built-in analytics dashboards (Sales and Product) powered by SQL reporting views.

## Project Overview

### Core business flow
- Browse products, add to cart, checkout
- Order is created and published to RabbitMQ
- Worker + Camunda process async fulfillment flow
- Order state transitions are persisted in PostgreSQL

### Analytics flow
- Historical data is seeded into existing tables (`users`, `products`, `orders`, `order_items`)
- Reporting SQL views provide analytics-ready aggregates
- Backend analytics API reads those views
- Frontend dashboards consume analytics API directly

### Key folders
- `backend/app/routers`: API routes (`analytics_router.py`, `order_router.py`, etc.)
- `backend/app/services`: service layer (`analytics_service.py` is read-only over views)
- `backend/migrations/versions`: DB schema + reporting view migrations
- `frontend`: static pages + JS modules
- `frontend/js/sales_dashboard.js`, `frontend/js/product_dashboard.js`: dashboard logic

## Run the Project (Docker)

### 1. Start stack
```bash
docker compose up --build -d
```

### 2. Useful URLs
- Frontend: http://localhost:8081
- FastAPI docs: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672 (guest/guest)
- Camunda: http://localhost:8080/camunda (demo/demo)

### 3. Re-run migrations + seed manually (optional)
```bash
docker compose run --rm backend sh -c "alembic upgrade head && python -m app.seed"
```

## Analytics Architecture

### Reporting views (source of truth for analytics)
Created by Alembic migration `0002_reporting_views.py`:
- `sales_order_items_fact_view`
- `sales_summary_view`
- `sales_over_time_view`
- `product_performance_view`

### Analytics API
- `GET /api/analytics/sales/summary`
- `GET /api/analytics/sales/trend`
- `GET /api/analytics/products/performance`

### Dashboard pages
- `frontend/sales_dashboard.html`
- `frontend/product_dashboard.html`

Both dashboards use manual **Refresh Analytics** for clear live-demo behavior.

## Live Demo Guide (for presentation)

1. Open `http://localhost:8081/auth.html` and log in (`test@example.com` / `password123`).
2. Create a new order:
- open catalog
- add item to cart
- complete checkout
3. Open Sales Dashboard: `http://localhost:8081/sales_dashboard.html`.
4. Click **Refresh Analytics**.
5. Observe updated metrics (typically pending/completed counts and charts, depending on order state).
6. Open Product Dashboard: `http://localhost:8081/product_dashboard.html`.
7. Click **Refresh Analytics** and observe top/bottom products + table updates.

## Security and Configuration Notes

### Required env vars (root `.env`)
Typical DB/runtime vars:
```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=sansevieria
SIMULATE_PAYMENT_FAILURE=false
```

### LM Studio in Docker
- When backend runs in Docker and LM Studio runs on the host machine, backend must use:
  - `LM_STUDIO_BASE_URL=http://host.docker.internal:1234`
- `127.0.0.1` from inside the container points to the container itself, not the host.

### Analytics access control
- `ANALYTICS_ADMIN_EMAILS` (comma-separated)
- Default: `test@example.com`
- Only emails in this list can call analytics endpoints.

Example:
```dotenv
ANALYTICS_ADMIN_EMAILS=test@example.com,admin@example.com
```

### CORS allowlist
- `ALLOWED_ORIGINS` (comma-separated)
- Default includes localhost frontend origins.

Example:
```dotenv
ALLOWED_ORIGINS=http://localhost:8081,http://127.0.0.1:8081
```

## Logging and Monitoring (lightweight)

Structured console logs are used for:
- startup and health checks
- order creation events
- analytics endpoint usage
- denied analytics access attempts
- handled analytics errors

Tail logs during demo:
```bash
docker compose logs -f backend
```

## Notes / Current Scope

- Analytics dashboards are in-app (no Power BI integration).
- Access control is lightweight allowlist-based, not full RBAC.
- Monitoring is console-log based (no Prometheus/ELK stack).

## Assignment 5: AI/ML + Semantic Ontology Extension

This project is extended with an assignment-focused **Product Performance Classification** pipeline and a lightweight **semantic ontology layer**.

- ML classes:
  - `Top Performer`
  - `Average Performer`
  - `Low Performer`
- Semantic layer:
  - JSON-LD ontology + RDF-style triples
  - ML prediction is represented semantically and returned by API
- UI integration:
  - Product Dashboard now displays class badge, confidence, semantic explanation, and triples preview.

### Assignment 5 Flow

`historical orders`  
→ `product_performance_view`  
→ preprocessing  
→ `DecisionTreeClassifier`  
→ `performance_class` prediction  
→ JSON-LD ontology / RDF-style triples  
→ semantic API endpoint  
→ Product Dashboard UI

### Dataset Source and Features

- Dataset source: `product_performance_view`
- Main features:
  - `units_sold`
  - `revenue`
  - `orders_count`
  - `price` (joined from `products` in ML service)
- Label strategy:
  - Labels are **simulated** from historical performance ranking (top/middle/bottom thirds).
  - This is intentional for assignment context with seeded/mock historical data.

### Assignment 5 Endpoints

- `GET /api/analytics/products/performance-ml`  
  Purpose: returns ML-enhanced product performance classification.

- `GET /api/analytics/products/performance-semantic`  
  Purpose: returns ML classification + semantic triples + semantic explanation.  
  Optional query: `class_name=Top Performer`

- `GET /api/analytics/products/performance-ontology`  
  Purpose: returns ontology metadata (JSON-LD) and sample triples.

All three endpoints use the same analytics access control as existing analytics endpoints (`require_analytics_user`).

### Ontology File

- `backend/app/ontology/sansevieria_product_performance.jsonld`

Defined classes/entities:
- `Product`
- `ProductCategory`
- `PerformanceClass`
- `MetricSnapshot`
- `ProductPerformancePrediction`

Defined relationships/properties:
- `hasPerformanceClass`
- `belongsToCategory`
- `hasMetricSnapshot`
- `hasUnitsSold`
- `hasRevenue`
- `hasOrdersCount`
- `hasConfidence`
- `hasExplanation`
- `generatedByModel`

### Sample RDF-Style Triples

- `Product_1` → `hasPerformanceClass` → `Top Performer`
- `Product_1` → `belongsToCategory` → `Classic`
- `MetricSnapshot_Product_1` → `hasUnitsSold` → `120`
- `MetricSnapshot_Product_1` → `hasRevenue` → `3120.50`
- `Prediction_Product_1` → `generatedByModel` → `ProductPerformanceClassifier`

### Demo / Testing Steps

1. Start stack:
```bash
docker compose up --build -d
```
2. Login:
   - URL: `http://localhost:8081/auth.html`
   - Credentials: `test@example.com` / `password123`
3. Open Product Dashboard:
   - `http://localhost:8081/product_dashboard.html`
4. Click **Refresh Analytics**
5. Verify on Product Dashboard:
   - Performance Class badges are visible
   - Confidence values are visible
   - Semantic Explanation is visible
   - **View Triples** expands RDF-style triples
   - Class filter works (`All`, `Top Performer`, `Average Performer`, `Low Performer`)
6. Optional API checks (Swagger):
   - `http://localhost:8000/docs`
   - `GET /api/analytics/products/performance-ml`
   - `GET /api/analytics/products/performance-semantic`
   - `GET /api/analytics/products/performance-ontology`

### Assignment Requirement Mapping

- AI/ML component → `DecisionTreeClassifier`
- Dataset → `product_performance_view`
- Preprocessing → numeric feature preparation (`units_sold`, `revenue`, `orders_count`, `price`)
- Training → in-memory classifier training
- Prediction → `performance_class`
- Intelligent decision-making → dashboard highlights product performance classes
- Ontology → JSON-LD file (`sansevieria_product_performance.jsonld`)
- RDF triples → `semantic_triples`
- Semantic reasoning/querying → `class_name` API filter + dashboard class filter
- AI + ontology integration → ML prediction becomes `hasPerformanceClass` triple
- UI display → Product Dashboard (`product_dashboard.html`)

### Limitations (Intentional for Assignment Scope)

- Assignment-level ML implementation (not production-grade).
- Labels are simulated from historical sales ranking.
- Model is trained in memory per request for demo simplicity.
- Semantic reasoning is lightweight and does not use an external RDF store.
- Architecture is intentionally minimal to satisfy assignment requirements cleanly.

### Final Verification Checklist

- [ ] Existing analytics endpoints still work.
- [ ] ML endpoint works (`/performance-ml`).
- [ ] Semantic endpoint works (`/performance-semantic`).
- [ ] Ontology endpoint works (`/performance-ontology`).
- [ ] Product Dashboard displays class/confidence/semantic fields.
- [ ] Chatbot remains unchanged.
- [ ] Checkout/order processing flow remains unchanged.
