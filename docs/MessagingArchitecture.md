# Messaging Architecture

This document describes the messaging architecture governing the Sansevieria distributed system, ensuring robust, fault-tolerant asynchronous communication via RabbitMQ.

## 1. AMQP Queues and Dead Letter Queues (DLQ)

The messaging infrastructure is built around RabbitMQ. It leverages persistent, highly durable queues designed to not lose state if systems crash.

### Primary Operational Queues
- **`order_processing_queue`**: Receives messages generated immediately following a successful cart-to-order transition on the HTTP `/api/checkout` endpoint.
- **`email_notification_queue`**: Receives payloads strictly upon the final completion state of an order workflow, simulating an email dispatch sequence to the end-user.

### Dead Letter Queues (DLQ)
To ensure absolute fault tolerance, unprocessable messages are not simply lost but rather safely routed into localized holding tanks:
- **`order_processing_dlq`**: Bound to `order_processing_queue` via `x-dead-letter-exchange` mappings. If a message explicitly fails consumer processing (e.g., throwing a hard `ch.basic_reject(requeue=False)` after Camunda limits are breached), RabbitMQ safely relocates the exact payload to this DLQ.
- **`email_notification_dlq`**: Bound to `email_notification_queue` mapping logic similarly for failed notification tasks.

## 2. Producer / Consumer Flow

The decoupled flow entirely separates UI HTTP thread interactions from heavy-duty backend process orchestration.

### The Producer (FastAPI App Layer)
When the user executes a checkout `POST`, the `app.messaging.producer` module executes. 
Instead of blocking the request thread waiting for payments or allocations, the producer instantly wraps the initial context variables (like the generated `order_id` map mapping to `correlation_id`) securely formatting JSON, then invokes an implicit fire-and-forget `publish_message()` drop natively into the `order_processing_queue`. The user is immediately shown a successful "Order Received" message!

### The Consumer (Python Worker Node)
Running concurrently in an isolated thread process, the python worker script natively holds a `basic_consume` map open against the targeted RabbitMQ queues: 
1. Utilizing a strict `prefetch_count=1`, the worker pulls only **one** message off the stack at a time per routing limit evenly distributing flow under heavy load.
2. It deserializes the wrapper, extracts the metadata header routing `correlation_id`, and drops it safely passing tokens internally into either the local processing components or the BPMN Camunda workflow wrapper!
3. If no Exception is triggered natively across the handling logic, the script gracefully issues a final `ch.basic_ack()`, deleting the persistent AMQP blob confirming absolute execution!

## 3. Standard Message Structure

Messages passed into RabbitMQ follow strict dictionary-driven JSON structures mapping business operations securely. Crucially, they append metadata header fields alongside the core payload body explicitly.

**Example `ORDER_CREATED` Event Payload:**
```json
{
    "event": "ORDER_CREATED",
    "order_id": "ORD-000123",
    "user_id": 99,
    "correlation_id": "ORD-000123",
    "timestamp": "2026-03-18T12:00:00.000000"
}
```
**RabbitMQ Native Headers:**
- `correlation_id`: Used to uniformly map distributed logging systems automatically (e.g., `ORD-000123`), dynamically extracting strings safely routing payloads locally even if nested heavily without inspecting JSON bodies fully!

## 4. Asynchronous Processing Lifecycle

1. **Instantiation**: Event creation drops a payload dynamically on an AMQP queue natively freeing UI execution completely.
2. **Buffering**: RabbitMQ safely stores the payload explicitly until a recognized consumer connects to the node dynamically mapping connections natively guaranteeing robust persistence.
3. **Consumption & Orchestration**: A Python worker grabs the isolated structure, parses standard tags, and issues a Camunda `/start` sequence locking internal bounds implicitly across internal hooks natively. 
4. **Resiliency Validation**: Transient issues engage the `@with_retries` net logic dynamically (1s/2s/4s waits).
5. **Final Atomic Dispatch**: 
    - **Success**: A standard `ch.basic_ack` routes success logs natively terminating persistence routing. The state flips securely inside PostgreSQL (`COMPLETED`).
    - **Failure**: A hard crash routes explicitly unrecoverable execution limits throwing `ch.basic_reject(requeue=False)` saving internal variables neatly wrapping the entire process directly toward the explicit DLQ mapped limits!
