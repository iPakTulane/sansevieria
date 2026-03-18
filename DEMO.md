# Sansevieria Enterprise Architecture: Live Demonstration Guide

This document provides a structured, step-by-step guide for a 3–5 minute live university presentation demonstrating the enterprise architecture features of the Sansevieria Web Application. The focus is on mapping visible user actions to backend microservice processes like asynchronous messaging, workflow orchestration, caching, correlation, and fault handling.

---

## PART 1 — USER JOURNEY MAPPING

The following user actions in the frontend UI correspond directly to specific backend enterprise features.

| UI Action | Triggered API Endpoint | Initiated Backend Process |
| :--- | :--- | :--- |
| **Browse Products** (Catalog Page) | `GET /api/products` | **Caching (Redis):** Fetches the product list. The first request hits PostgreSQL. Subsequent requests hit the Redis cache for sub-millisecond responses. |
| **Add to Cart** (Product/Catalog Page) | Frontend Local State | Updates the local cart state in the browser (no major backend process until checkout). |
| **Checkout / Submit Order** (Checkout Page) | `POST /api/checkout` | **Messaging (RabbitMQ) & Workflow (Camunda):** Generates a unique `order_id`, publishes a message to the `order_processing_queue` in RabbitMQ, and starts the `Order Fulfillment Process` in Camunda. |

---

## PART 2 — FEATURE TRIGGER MAPPING

Here is exactly how each Assignment 3 enterprise feature is triggered and observed during the demo.

### 1. Asynchronous Messaging (RabbitMQ)
- **UI Trigger:** Clicking "Place Order" on the Checkout page.
- **Message Sent:** A JSON payload containing the `order_id` and cart details.
- **Observability:** Open the **RabbitMQ Management UI** (`http://localhost:15672`). Under the "Queues" tab, watch the `order_processing_queue` spike in activity as the message is published and immediately consumed by the Python worker.

### 2. Workflow Orchestration (Camunda)
- **UI Trigger:** Clicking "Place Order" on the Checkout page.
- **Observability:** Open the **Camunda Cockpit** (`http://localhost:8080/camunda`). Navigate to `Processes > Order Fulfillment Process`.
- **Visible Steps:** You will see a visual BPMN diagram with active token badges migrating through steps synchronously (e.g., `Validate Order` ➡️ `Process Payment` ➡️ `Gateway`).

### 3. Correlation (`order_id`)
- **Generation:** Generated instantly by the FastAPI backend when `POST /api/checkout` is called.
- **Flow:** Passed from the API response ➡️ into the RabbitMQ message payload ➡️ assigned as the Business Key in the Camunda workflow instance ➡️ logged by the worker.
- **Observability:** Visible in the frontend UI confirmation screen, the Swagger API response, the RabbitMQ message payload, and as the `Business Key` in Camunda Cockpit.

### 4. Caching (Redis)
- **UI Trigger:** Refreshing the Catalog page multiple times.
- **Demonstration:** Use Swagger UI (`http://localhost:8000/docs`). Execute `GET /api/products`.
- **Observability:** The first call shows a "Server Response Time" of ~20-50ms (PostgreSQL hit). Hit "Execute" again immediately, and the response time drops to `<3ms` (Redis cache hit). 

### 5. Fault Handling (Circuit Breaker & DLQ)
- **Simulation:** Set `SIMULATE_PAYMENT_FAILURE=true` in the `.env` file and restart/apply changes.
- **UI Trigger:** Attempting a checkout. 
- **Observability:** 
  - **Logs:** Run `docker compose logs -f worker` in the terminal. You will see warning logs for exponential backoff retries, followed by a `Circuit Breaker OPEN` state.
  - **DLQ:** The message is rejected and routed to the Dead Letter Queue (`order_processing_dlq`) in RabbitMQ.

---

## PART 3 — DEMO SCENARIOS

### Scenario 1: The Fast Path (Caching)
**Goal:** Show how Redis accelerates data retrieval.
1. **Action:** Open Swagger UI (`http://localhost:8000/docs`) and find `GET /api/products`. (Alternatively, use the Network tab of standard browser dev tools on the Catalog page).
2. **Execute:** Click execute. Point to the response time (~30ms).
3. **Re-Execute:** Click execute again. Point to the massive drop in response time (<3ms).
4. **Script:** *"When users load our catalog, a backend call fetches products. The first time, it hits our database. But watch what happens on subsequent loads—Redis caching intercepts the request, dropping our response time to under 3 milliseconds."*

### Scenario 2: The E-Commerce Engine (Messaging & Workflow)
**Goal:** Show asynchronous decoupling and visual orchestration.
1. **Setup:** Have the Checkout page, RabbitMQ UI, and Camunda Cockpit open in separate adjacent tabs or split-screen.
2. **Action:** Submit an order on the Checkout UI. 
3. **Observe RabbitMQ:** Instantly switch to RabbitMQ and point to the `order_processing_queue` throughput spike.
4. **Observe Camunda:** Switch to Camunda Cockpit. Refresh the visual BPMN flow to show the active token processing the order.
5. **Script:** *"When I check out, the API responds instantly because it's asynchronous. Behind the scenes, a message is published to RabbitMQ. Our worker consumes it and triggers a Camunda workflow. Here in Camunda, you can actually see the blue token representing this exact order moving through validation and payment."*

### Scenario 3: Enterprise Resilience (Fault Handling)
**Goal:** Show how the system survives a third-party outage.
1. **Setup:** Ensure `SIMULATE_PAYMENT_FAILURE=true` is set. Have terminal logs running (`docker compose logs -f worker`).
2. **Action:** Submit an order on the Checkout UI.
3. **Observe Logs:** Watch the terminal explicitly log the retry attempts and circuit breaker opening.
4. **Observe DLQ:** Open RabbitMQ and point out the message sitting safely in the `order_processing_dlq`.
5. **Script:** *"What if our payment gateway goes down? Let's simulate a failure. I'll place an order. Watch the worker logs—it smartly retries with exponential backoff. Once the circuit breaker opens, instead of crashing, it safely parks the order in a Dead Letter Queue for manual review later."*

---

## PART 4 — VISUAL OBSERVABILITY

These are the tools you must have open and ready before the demo begins.

| Tool | URL / Command | What It Proves | What To Look At |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | `http://localhost:8081` | Triggering actions naturally | The Checkout and Catalog pages. |
| **Swagger UI** | `http://localhost:8000/docs` | API endpoints and Cache timings | Response times for `GET /api/products`. |
| **RabbitMQ UI** | `http://localhost:15672` | Asynchronous decoupled messaging | `order_processing_queue` and `order_processing_dlq` under the Queues tab. |
| **Camunda Cockpit** | `http://localhost:8080/camunda` | Orchestrated long-running state | The visual BPMN diagram with active token overlays. |
| **Terminal Logs** | `docker compose logs -f worker` | Internal worker behavior & correlation | Log lines showing `order_id` correlation, retries, and Circuit Breaker states. |

---

## PART 5 — DEMO SCRIPT SUPPORT

Use these one-liners to keep the presentation punchy, focusing on *why* these features matter.

- **On Asynchronous APIs:** *"Notice how fast the UI confirms the order? The frontend doesn't wait for payment processing; it just successfully handed the job off to the message queue."*
- **On Messaging:** *"RabbitMQ connects our systems without coupling them. Our backend and our workers don't need to know about each other."*
- **On Workflows:** *"Camunda explicitly maps our business logic. If a microservice crashes step 2, Camunda remembers exactly where we left off."*
- **On Caching:** *"Redis gives us scale. By caching the catalog, we protect our Postgres database from being overwhelmed during traffic spikes."*
- **On Fault Tolerance:** *"In an enterprise system, failure is inevitable. Our Dead Letter Queues ensure that no customer order is ever truly lost."*

---

## PART 6 — TIMING (3.5 Minutes Total)

A suggested timeline to keep the pace brisk and engaging:

- **0:00 - 0:30 (Intro):** Briefly introduce the Sansevieria app. Show the UI. "Today, I will show you the enterprise engine powering this storefront."
- **0:30 - 1:00 (Scenario 1 - Cache):** Demonstrate the catalog caching via Swagger. Emphasize the speed difference.
- **1:00 - 2:30 (Scenario 2 - Happy Path):** Place an order in the UI. Quickly pivot to RabbitMQ to show the queue spike, then to Camunda to show the workflow token. Mention `order_id` correlation. 
- **2:30 - 3:30 (Scenario 3 - Failure Path):** Trigger the predefined failure. Show the terminal logs aggressively retrying, and conclude by highlighting the protected message in the Dead Letter Queue. 
- **3:30 (Outro):** "Thank you."
