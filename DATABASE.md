# Sansevieria Data Architecture & Storage

This document outlines how the database, data storage, and data models are structured in the Sansevieria project.

## 1. Infrastructure and Data Persistence Services

The project relies on a distributed data architecture with different services handling distinct aspects of data persistence and flow:

- **PostgreSQL**: The primary relational database used as the single source of truth for persistent domain entities (Users, Products, Carts, Orders).
- **Redis**: An in-memory data store used as a caching layer. It caches frequently accessed read-heavy operational data (e.g., retrieving the product catalog) to provide low-latency responses and reduce the load on the PostgreSQL database.
- **RabbitMQ**: The message broker used to handle asynchronous data flow (e.g., processing checkout events). Orders created via the API act as events dispatched through RabbitMQ queues.
- **Camunda**: A workflow engine that persists stateful business processes (like order fulfillment steps).

## 2. Data Flow

1. **Client Request**: The frontend makes HTTP requests to the FastAPI backend.
2. **Read Operations**: For retrieval requests like viewing the product catalog, the backend checks the **Redis** cache first. If a cache miss occurs, it queries PostgreSQL, returns the data, and updates Redis.
3. **Write Operations**: For transactional actions (e.g., adding to cart, placing an order), the backend uses SQLAlchemy ORM to safely write state changes to **PostgreSQL**.
4. **Asynchronous/Event-Driven Processing**: When a user checks out, an order is inserted into PostgreSQL with a "PENDING" status. Simultaneously, a message is published to **RabbitMQ**, which a Python worker picks up to orchestrate complex logic synchronously via **Camunda**, updating the database incrementally down the line.

## 3. Data Models and Schemas

The application uses **SQLAlchemy** as the ORM to bridge object-oriented code with the relational database. The schemas are mapped as follows:

### Users (`users` table)
Stores basic user profiles and authentication details.
- `id` (Integer, Primary Key)
- `name` (String)
- `email` (String, Unique)
- `password_hash` (String)
- `created_at` (DateTime)

### Products (`products` table)
Stores the catalog of Sansevieria plants.
- `id` (Integer, Primary Key)
- `title` (String)
- `description` (String)
- `size` (String)
- `light_level` (String)
- `price` (Float)
- `image_url` (String)
- `category` (String)

### Carts and Cart Items
Represents the shopping carts of users, utilizing a parent-child relationship.

**`carts` table:** 
Linked 1:1 with a user.
- `id` (Integer, Primary Key)
- `user_id` (Integer, Foreign Key to `users.id`, Unique)
- `created_at` (DateTime)

**`cart_items` table:**
Linked many-to-one to a cart.
- `id` (Integer, Primary Key)
- `cart_id` (Integer, Foreign Key to `carts.id`)
- `product_id` (Integer, Foreign Key to `products.id`)
- `quantity` (Integer)

### Orders and Order Items
Manages order history and fulfillment state. Has a parent-child relationship similar to carts.

**`orders` table:**
- `id` (Integer, Primary Key)
- `order_id` (String, Unique identifier)
- `user_id` (Integer, Foreign Key to `users.id`)
- `status` (String, e.g., "PENDING")
- `total_amount` (Float)
- `created_at` (DateTime)
- `updated_at` (DateTime)

**`order_items` table:**
Captures point-in-time pricing.
- `id` (Integer, Primary Key)
- `order_id` (Integer, Foreign Key to `orders.id`)
- `product_id` (Integer, Foreign Key to `products.id`)
- `quantity` (Integer)
- `price_at_purchase` (Float)

## Summary

The state of the system relies on structured **Relational Data (PostgreSQL/SQLAlchemy)** for long-term storage and integrity of Users, Carts, Products, and Orders. Performance and flow are optimized and decentralized using **Redis** for read-caching and **RabbitMQ/Camunda** for eventual consistency and asynchronous workflow orchestration.
