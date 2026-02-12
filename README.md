# Aforro Backend Assignment

A complete Django-based inventory and order management system with Redis caching, Celery background tasks, and Docker containerization.

## Features
- **Data Models**: Category, Product, Store, Inventory, Order, OrderItem.
- **REST APIs**: Order creation (atomic), Order listing, Inventory listing, Product Search, and Autocomplete.
- **Query Optimization**: Efficient queries with `select_related`, `prefetch_related`, and `annotate`.
- **Search**: Full-text keyword search with multi-field filtering and sorting.
- **Redis Integration**:
  - **Caching**: Inventory listing API is cached for 15 minutes.
  - **Rate Limiting**: (Implemented logic structure) Suggest API is candidate for DRF-based throttling.
- **Celery Integration**: Asynchronous order confirmation task.
- **Docker**: Fully containerized environment (Django, PostgreSQL, Redis, Celery).
- **Seed Data**: Custom management command to generate 1000+ products and 20+ stores.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.

### Run with Docker (Recommended)
1. Clone the repository.
2. Build and start containers:
   ```bash
   docker-compose up --build
   ```
3. Run migrations and seed data (in a new terminal):
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py seed_data
   ```

## Sample API Requests

### Order Creation
**POST** `/orders/`
```json
{
  "store_id": 1,
  "items": [
    {"product_id": 10, "quantity_requested": 2},
    {"product_id": 15, "quantity_requested": 1}
  ]
}
```

### Product Search
**GET** `/api/search/products/?q=phone&min_price=100&store_id=1&in_stock=true`

### Autocomplete
**GET** `/api/search/suggest/?q=lap`

## Engineering Notes

### Caching
The Inventory list API for a specific store is cached to reduce DB load. The cache invalidates based on the timeout (15 mins) or can be manually cleared.

### Asynchronous Logic
When an order is successfully confirmed, a Celery task `send_order_confirmation` is triggered. This task runs in the background to handle emails/notifications without blocking the API response.

### Consistency
Order creation uses `transaction.atomic()` and `select_for_update()` to ensure data consistency and prevent race conditions when multiple orders are placed simultaneously for the same product.

### Scalability Considerations
- **Database**: Indexing on search fields (Title, Category Name) can further improve performance.
- **Cache**: Using Redis allows distributed caching across multiple app instances.
- **Workers**: Celery workers can be scaled horizontally to handle high volumes of background tasks.
