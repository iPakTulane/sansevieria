# Fault Handling Mechanisms

This document details the robust resiliency suite built into the Sansevieria distributed system. Since network calls fail inherently in microservices, this architecture gracefully protects its critical infrastructure natively rather than crashing abruptly.

## 1. Retry Logic (Exponential Backoff)

Transitional network hiccups are intercepted instantly across the executing Python worker threads. Fast-paced integrations like the Camunda workflow initiator or simulated REST Payment gateways are decorated dynamically using the `@with_retries` net.
- **Max Retries:** 3 attempts globally on bound functions explicitly.
- **Exponential Backoff:** If the first attempt fails natively, the execution pauses using intelligent delays (`1s -> 2s -> 4s`) rather than aggressively bombarding the recovering target system explicitly ensuring the downstream component natively revives!

## 2. Dead Letter Queues (DLQ)

If a payload reaches an irrecoverable state explicitly, it natively must be dropped safely without crashing the AMQP ingestion pipeline globally.
- Both the `order_processing_queue` and `email_notification_queue` are tightly bound to exclusive `x-dead-letter-exchange` mappings locally securely routing exclusively into `_dlq` buckets.
- If the core Python RabbitMQ Consumer hits a fatal error starting workflows iteratively (and fully exhausts its retry attempts), it natively throws a deliberate `ch.basic_reject(requeue=False)`.
- **Result:** Instead of evaporating into nothingness (or blocking the executing pool indefinitely looping forever), RabbitMQ natively preserves the original JSON wrapper and headers routing natively onto the DLQ exactly as it found it, preserving data integrity completely inherently.

## 3. Circuit Breaker

Cascading failures bring down entire fleets natively. The `@payment_circuit_breaker` object safely brackets dangerous external HTTP tasks universally.
- **Open / Closed Behaviors:** While normally executing freely (CLOSED bounds), if errors continuously accrue dynamically tracking consecutive limits locally (e.g., `3` total failures dynamically), the Breaker explicitly trips completely (OPEN bounds).
- **Protection:** During the OPEN state, any secondary executing functions natively instantly skip hitting the backend task explicitly, actively returning a fallback trace exception without executing business computations!
- **Cooldown Limit:** After `15` seconds elapses dynamically, the system intuitively shifts to a `HALF-OPEN` probing mode dynamically checking if external components magically recovered natively.

## 4. Timeout Handling

Slow functions dynamically tie up threads routing natively crashing concurrent bounds broadly. Explicit endpoints are strictly decorated cleanly using `@with_timeout`.
- **Execution Windows:** By explicitly limiting runtime (e.g., maximum `5s` per execution bounds universally), if an external DB lock natively holds threads arbitrarily, the wrapper automatically throws a `TimeoutException`. 
- **Chaining Bounds**: Catching this explicitly automatically engages our `@with_retries` exponential backup mechanisms explicitly, cleanly freeing thread pools.

## 5. Graceful Degradation & User Notification

Perhaps the most important resiliency check natively applies explicitly onto the User API interactions broadly. 
- Fast API never exposes a hard HTTP `500 Internal Server Error` natively crashing browsers unexpectedly.
- When `POST /api/checkout` fires naturally, it wraps immediately natively returning `status: PENDING` explicitly to the user.
- If all asynchronous background retry loops totally fail dynamically, if Circuit Breakers trip cleanly, and message blobs eventually land neatly inside DLQs natively, the system cleanly isolates the execution context modifying PostgreSQL states exclusively into a distinct state `FAILED`. The end user's UI is never blocked waiting iteratively!
