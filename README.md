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
- (Optional) Python 3.11+ for local development.
- (Optional) PostgreSQL and Redis installed locally if not using Docker.

---

### Run with Docker (Recommended)

1. **Clone the repository.**
2. **Build and start containers**:
   ```bash
   docker-compose up --build
   ```
3. **Run migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```
4. **Seed the database**:
   ```bash
   docker-compose exec web python manage.py seed_data
   ```
5. **Create a Superuser** (for Admin access):
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

The application will be available at [http://localhost:8000](http://localhost:8000).
The Django Admin interface is at [http://localhost:8000/admin](http://localhost:8000/admin).

---

### Local Development Setup (Manual)

If you prefer to run the components individually without Docker:

1. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup**:
   Ensure you have PostgreSQL and Redis running. Create a `.env` file or export the following variables:
   ```bash
   DB_NAME=aforro_db
   DB_USER=postgres
   DB_PASSWORD=password
   DB_HOST=localhost
   DB_PORT=5432
   REDIS_HOST=localhost
   ```
4. **Run Migrations & Seed Data**:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```
5. **Start the Application**:
   - **Run Django Development Server**:
     ```bash
     python manage.py runserver
     ```
   - **Run Celery Worker** (Required for background tasks):
     ```bash
     celery -A core worker -l info
     ```

---

## Testing

The project uses `pytest` for testing.

### Running with Docker:
```bash
docker-compose exec web pytest
```

### Running locally:
```bash
pytest
```

---

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

---

## Engineering Notes

### Caching
The Inventory list API for a specific store is cached to reduce DB load. The cache invalidates based on the timeout (15 mins).

### Asynchronous Logic
When an order is successfully confirmed, a Celery task `send_order_confirmation` is triggered. This task runs in the background.

### Consistency
Order creation uses `transaction.atomic()` and `select_for_update()` to ensure data consistency and prevent race conditions.
