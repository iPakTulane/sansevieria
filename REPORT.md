# Sansevieria - Enterprise Integration Analysis Report

## 1. Project Overview
- **What the system does:** A web application focusing on the cataloging, care, and commerce of Sansevieria (Snake Plants). It acts as a comprehensive portal providing AI-driven care assistance, e-commerce shopping, and user plant management.
- **Main user flows:**
  - AI Assistant Interaction: Conversing with a plant care AI on the homepage.
  - E-commerce Flow: Catalog filtering -> Viewing product details -> Managing Cart -> Checkout and Confirmation.
  - User Management Flow: Registration/Login -> Dashboard (viewing recent orders, interacting with plant care task reminders).
  - Informational Flow: Exploring pages covering plant varieties, care guides, problems, and a blog.
- **Core features:**
  - Integrated AI chatbot UI.
  - Dynamic UI mockups for product filtering (by size, light needs, price).
  - Cart and Order summary displays.
  - A user dashboard featuring gamified/task-based plant care reminders and order history tracking.
- **Business domain:** Botanical care, e-commerce, and personalized digital plant assistance.

---

## 2. System Architecture
- **Frontend framework:** Pure static HTML5 and CSS, leveraging Tailwind CSS via CDN.
- **Backend framework:** Currently non-existent. The application consists entirely of static pages.
- **Programming languages used:** HTML, CSS, JavaScript (for inline basic UI routing), and Python (for static site maintenance scripts).
- **Database technology:** Currently non-existent (mocked via static HTML).
- **Deployment model:** Static file hosting capability (e.g., Python `http.server`, or scalable static hosts like AWS S3 / Vercel).
- **External services or APIs (Currently used):** Google Fonts, Material Symbols, external Image CDNs.

**Architecture Diagram:**
```text
[ Client Browser ]
        |
        +-- (HTTP GET) --> [ Static Web Server (HTML Files) ]
                                  ^
                                  |
                           [ Python Build Utilities ]
                           (update_headers.py, update_links.py)
```

---

## 3. Page and Feature Inventory
- **`index.html`** (Home): Features an AI chatbot interface. Interaction: Users typing and sending messages.
- **`catalog.html`** (Catalog): Displays product grids with sidebar filters (Size, Light Needs, Price). Interaction: Checking boxes and sliders.
- **`product.html`** (Product Details): Deep dive into a single plant, showing price, specs, and care level. Interaction: Changing quantity, adding to cart.
- **`cart.html`** (Cart): Reviews pending items and order summary. Interaction: Adjusting quantities, deleting items.
- **`checkout.html`** (Checkout): Gathers Shipping and Payment Details. Interaction: Form input.
- **`confirmation.html`** (Confirmation): Static success message post-purchase.
- **`auth.html`** (Authentication): Login and Registration forms. Interaction: Form submission.
- **`dashboard.html`** (User Dashboard): Displays "Care Reminders" (with checkable tasks) and "Recent Orders". Interaction: Checking off plant care duties, viewing order details.
- **Informational Pages** (`care.html`, `blog.html`, `problems.html`, `varieties.html`, `about.html`, `team.html`, `contact.html`): Static content ingestion.

---

## 4. Backend Services and APIs
*Note: As the backend is currently mocked by static HTML, the following table lists the identified REQUIRED APIs based on the frontend UI components.*

| Endpoint | Method | Purpose | Input | Output |
| :--- | :--- | :--- | :--- | :--- |
| `/api/chat` | POST | Process AI query for plant care | User text prompt | AI text response |
| `/api/products` | GET | Retrieve catalog items | Filter params (size, light, price) | Array of Product models |
| `/api/products/{id}` | GET | Retrieve single product | Path parameter `id` | Product model |
| `/api/cart` | GET | Retrieve user cart | User session/token | Cart model |
| `/api/cart` | POST | Add/Update cart items | ProductID, Quantity | Updated Cart model |
| `/api/checkout` | POST | Process order payment | Extracted Shipping & Payment data | Order Confirmation ID |
| `/api/orders` | GET | Retrieve order history | User token | Array of Order summaries |
| `/api/care-reminders` | GET | Retrieve user plant tasks | User token | Array of Task objects |
| `/api/auth/login` | POST | Authenticate user account | Email, Password | Auth JWT Token |

---

## 5. Data Model
*Key inferred entities based on the UI specifications:*

- **User:** ID, Name, Email, PasswordHash
- **Product:** ID, Title, Description, Size, LightLevel, Price, Category, ImageURL
- **Order:** OrderID, UserID, Date, Status (Shipped, Delivered, Processing), TotalAmount, Items[]
- **OrderItem:** ID, OrderID, ProductID, Quantity, PriceAtTimeOfPurchase
- **CareReminder:** ID, UserID, PlantName, TaskType (Water, Fertilize, Prune), DueDate, Completed (Boolean)

**Business Identifiers:** `OrderID` (e.g., `#ORD-7721`), `UserID`, `ProductID`. These will serve as correlation IDs during microservice communications.

---

## 6. Current System State Management
- **User sessions:** None. The authentication page visually navigates to the dashboard without creating a secure session.
- **Transactions:** None.
- **Multi-step user flows:** Managed purely by client-side local navigation (`window.location.href`). State does not persist across pages (e.g., adding to cart on `product.html` does not actually populate `cart.html`).
- **Persistent state:** None.

---

## 7. Integration Points
- **Workflow orchestration:** E-commerce order fulfillment lifecycle and user onboarding.
- **Message queues:** Delegating AI chat processing, scheduling reminder tasks, order processing queues.
- **Asynchronous processing:** Generating downloadable PDF invoices, sending bulk care reminder emails.
- **Caching:** Frequently visited, mostly static data such as the Product Catalog, Blog content, and Care Guides.
- **External services:** 
  - Payment Gateways (Stripe, PayPal) for checkout.
  - Large Language Model APIs (OpenAI, Anthropic) for the AI Chatbot.
  - 3rd-party logistics/shipping APIs for tracking numbers.

---

## 8. Candidate Business Processes
*Three business processes primed for a workflow engine (e.g., BPEL, Camunda temporal).*

1. **Order Fulfillment Process**
   - **Step 1:** Receive Order message containing contents and payment details.
   - **Step 2:** Invoke Payment Gateway service to authorize and capture funds.
   - **Step 3:** Allocate/Reserve inventory via the Inventory Management Service.
   - **Step 4:** Dispatch shipping request to external 3PL integration.
   - **Step 5:** Upon receiving shipping confirmation, transition order status to "Shipped" and notify the user.

2. **Plant Care Reminder Orchestration**
   - **Step 1:** System runs a nightly CRON job evaluating all active user profiles.
   - **Step 2:** For each user, analyze owned plants and their specific temporal needs (e.g., "Water Snake Plant every 4 weeks").
   - **Step 3:** Generate pending `CareReminder` tasks for the dashboard.
   - **Step 4:** Asynchronously dispatch a compilation email/push notification queueing service.

3. **User Onboarding and Verification**
   - **Step 1:** Receive account registration request.
   - **Step 2:** Create unverified User record.
   - **Step 3:** Assign initial "Welcome" dashboard care tasks (e.g., "Read your first care guide").
   - **Step 4:** Dispatch verification notification to email service.
   - **Step 5:** Wait for user validation callback; upon success, transition account status to "Verified".

---

## 9. Messaging Opportunities
- **Order Confirmation Emails:** Fire-and-forget message processing upon successful checkout.
- **Payment Webhooks:** Asynchronously receiving updates from external payment operators.
- **Daily Care Reminders:** Dispatching high-volume push notifications or emails.
- **Invoice Generation:** Background task triggered when clicking "Download Invoices" in the Dashboard.

---

## 10. Caching Opportunities
- **Product Catalog:** High read / low write data. Suitable for an aggressive caching strategy (e.g., Redis layer).
- **Varieties and Care Information:** Static text/image data that should be CDN cached or held in-memory.
- **Dashboard UI Fragments:** Pre-computing basic user metadata counts to save database roundtrips.

---

## 11. Reliability and Fault Scenarios
- **External Payment API downtime:** Requires fallback logic or delayed processing queues during checkout.
- **AI Chat Service rate limits/timeouts:** Must implement circuit breakers to gracefully degrade the UI if the AI service is unavailable.
- **Database/Inventory Locking:** Handling transactional rollbacks (Saga pattern) if an item runs out of stock after payment is processed.
- **Asynchronous email delivery failures:** Requires retry mechanisms and dead-letter queues.

---

## 12. Recommended Integration Architecture
- **Workflow Engine:** Implement a tool like **Camunda** or **Temporal** to orchestrate the multi-step `Order Fulfillment Process`, assuring state recoverability and saga execution in case of payment failure.
- **Message Broker:** Utilize **RabbitMQ** or **Apache Kafka** to decouple the UI from heavy tasks. The checkout API publishes to an `Order_Pending` topic rather than handling the process synchronously.
- **Caching Layer:** Implement **Redis** to intercept `GET /api/products` requests to reduce load on the primary relational database.
- **Service Contracts:** Transition the mock APIs to formalized **OpenAPI (Swagger)** specifications for strict typing and integration boundary enforcement among upcoming microservices.
- **Fault-Handling Mechanisms:** Implement **Circuit Breaker protocols** around external API calls (Payments, LLMs) and **Dead Letter Queues (DLQ)** in the message broker for failed notification dispatches.
