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
