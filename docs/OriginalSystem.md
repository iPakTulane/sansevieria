# Sansevieria - Before Backend Integration

## Architecture
Originally, the Sansevieria project was built as a purely static frontend web application.
- **Frontend Only**: Composed entirely of static HTML, CSS (using Tailwind CSS utility classes), and minimal client-side JavaScript.
- **No Server**: The application ran directly in the browser by opening HTML files or serving them via a simple local HTTP server, with no dynamic server-side rendering or API routing.

## Limitations
- **No Backend or API**: There were no RESTful services to handle business logic or data retrieval.
- **No Data Persistence**: Without a database, all product offerings, prices, and user data were hardcoded directly into the HTML structure.
- **No State Management**: The application could not natively persist a shopping cart across a user session, remember user authentication, or track the real-time status of an order. Any interactive elements were purely visual demonstrations.
- **No Asynchronous Processing**: Actions like placing an order or sending emails could not be processed, queued, or retried if they failed.

## User Flows (Simulated)
Despite the lack of a backend, the static templates simulated standard e-commerce flows:
1. **Catalog Browsing**: Users could view a hardcoded list of snake plant varieties and care products on `catalog.html`.
2. **Shopping Cart**: Users could navigate to `cart.html` to see a mocked visualization of selected items.
3. **Checkout**: The `checkout.html` page provided a visual form for shipping and payment details, but submitting it did not process payments, reduce inventory, or trigger any order fulfillment logic.
4. **Content Pages**: Users could read static informational pages like `care.html`, `blog.html`, and `varieties.html`.
