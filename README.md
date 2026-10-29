# Django Q Objects & Lookups Assignment

This project demonstrates advanced Django query filtering using `Q` objects, pattern matching (`icontains`, `endswith`), regular expressions (`regex`), field-level comparisons (`F()`), and performance optimization (`select_related`).

## Features
- **Restaurant & Sale Models**: Fully relational data schema.
- **Encapsulated Q Expressions**: Located in `restaurants/queries.py` for modular reuse.
- **SQL Logging Demonstration**: Management command `q_filter_demo` executing queries and printing raw SQL via `connection.queries`.
- **Database Seeder**: `seed_data` management command generating realistic test data.
- **Automated Tests**: Unit tests with `assertNumQueries` verification.

## Setup & Execution

### 1. Run Migrations
```bash
python manage.py migrate
```

### 2. Populate Test Data
```bash
python manage.py seed_data
```

### 3. Run Query Demonstration
```bash
python manage.py q_filter_demo
```

### 4. Run Automated Test Suite
```bash
python manage.py test
```

## Documentation
See [`REPORT.md`](REPORT.md) for detailed explanations of each query, the lookup mechanisms, and generated SQL queries.

