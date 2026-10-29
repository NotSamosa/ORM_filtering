# Advanced Query Filtering with Django Q Objects & Lookups

## Executive Summary
This report provides an in-depth analysis of complex database queries implemented using Django `Q` objects, pattern matching lookups (`icontains`, `endswith`), regular expressions (`regex`), field expressions (`F()`), and query optimization (`select_related`). All queries were tested and verified using SQLite via the management command `python manage.py q_filter_demo`.

---

## 1. Data Models

### 1.1 Restaurant Model
Represents dining establishments with the following schema:
- `name` (`CharField(max_length=150)`): Restaurant name.
- `restaurant_type` (`CharField(max_length=50)`): Cuisine category using Django `TextChoices` (`Italian`, `Mexican`, `American`, `Chinese`, `Indian`, `French`, `Fast Food`).
- `date_opened` (`DateField`): The opening date of the establishment.

### 1.2 Sale Model
Represents financial transaction records linked to a restaurant:
- `restaurant` (`ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='sales')`): Associated restaurant.
- `income` (`DecimalField(max_digits=12, decimal_places=2)`): Revenue generated.
- `expenditure` (`DecimalField(max_digits=12, decimal_places=2)`): Operating costs incurred.

---

## 2. Query Analysis & SQL Translation

### Query 1a: Restaurant Type is Italian OR Mexican
- **Objective**: Retrieve all restaurants whose cuisine type is either Italian or Mexican.
- **Q Object Expression**:
  ```python
  italian_mexican_q = (
      Q(restaurant_type=Restaurant.RestaurantType.ITALIAN) |
      Q(restaurant_type=Restaurant.RestaurantType.MEXICAN)
  )
  ```
- **ORM Lookup**: Exact match equality (`=`) combined via the bitwise OR (`|`) operator.
- **Generated SQL**:
  ```sql
  SELECT "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_restaurant"
  WHERE ("restaurants_restaurant"."restaurant_type" = 'Italian'
     OR  "restaurants_restaurant"."restaurant_type" = 'Mexican')
  ORDER BY "restaurants_restaurant"."id" ASC;
  ```
- **Explanation**: Standard Django `filter(type='Italian', type='Mexican')` creates an impossible SQL `AND` condition. The `Q` object with `|` properly compiles into a SQL `OR` clause.

---

### Query 1b: Restaurants NOT Opened in the Last 30 Days (Negation)
- **Objective**: Retrieve restaurants that opened earlier than the 30-day recent window using Q object negation.
- **Q Object Expression**:
  ```python
  thirty_days_ago = timezone.now().date() - timedelta(days=30)
  recently_opened_q = Q(date_opened__gte=thirty_days_ago)
  not_recently_opened_q = ~recently_opened_q
  ```
- **ORM Lookup**: Date greater than or equal (`gte`) wrapped with the invert operator (`~`).
- **Generated SQL**:
  ```sql
  SELECT "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_restaurant"
  WHERE NOT ("restaurants_restaurant"."date_opened" >= '2026-09-29')
  ORDER BY "restaurants_restaurant"."id" ASC;
  ```
- **Explanation**: Inverting the `Q` object using `~` wraps the condition with SQL `WHERE NOT (...)`, eliminating the need for manual date reversal calculations.

---

### Query 1c: Combined Condition (Italian/Mexican OR Opened in Last 30 Days)
- **Objective**: Retrieve restaurants that are Italian or Mexican, OR opened recently within the last 30 days.
- **Q Object Expression**:
  ```python
  type_or_recently_opened_q = italian_mexican_q | recently_opened_q
  ```
- **ORM Lookup**: Multi-predicate composition using the `|` operator across three discrete conditions.
- **Generated SQL**:
  ```sql
  SELECT "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_restaurant"
  WHERE ("restaurants_restaurant"."restaurant_type" = 'Italian'
     OR  "restaurants_restaurant"."restaurant_type" = 'Mexican'
     OR  "restaurants_restaurant"."date_opened" >= '2026-09-29')
  ORDER BY "restaurants_restaurant"."id" ASC;
  ```
- **Explanation**: Demonstrates modular query reusability. Pre-defined Q objects are composed into a unified expression without duplicating logic.

---

### Query 2a: Name Contains Substring "grill" (Case-Insensitive)
- **Objective**: Find all restaurants with "grill" in their name regardless of letter casing (e.g., "Grill", "grill", "GRILL").
- **Q Object Expression**:
  ```python
  name_contains_grill_q = Q(name__icontains='grill')
  ```
- **ORM Lookup**: `icontains` lookup translating to SQL `LIKE '%grill%'`.
- **Generated SQL**:
  ```sql
  SELECT "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_restaurant"
  WHERE "restaurants_restaurant"."name" LIKE '%grill%' ESCAPE '\'
  ORDER BY "restaurants_restaurant"."id" ASC;
  ```
- **Explanation**: On SQLite, `LIKE` is case-insensitive for ASCII characters by default. In PostgreSQL and MySQL, Django translates `icontains` to `ILIKE` or `UPPER(col) LIKE UPPER(...)`.

---

### Query 2b: Name Ends with "Cafe"
- **Objective**: Match restaurants whose names end strictly with "Cafe" (excluding names where "Cafe" appears at the beginning or middle).
- **Q Object Expression**:
  ```python
  name_ends_with_cafe_q = Q(name__endswith='Cafe')
  ```
- **ORM Lookup**: `endswith` lookup translating to SQL `LIKE '%Cafe'`.
- **Generated SQL**:
  ```sql
  SELECT "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_restaurant"
  WHERE "restaurants_restaurant"."name" LIKE '%Cafe' ESCAPE '\'
  ORDER BY "restaurants_restaurant"."id" ASC;
  ```
- **Explanation**: The pattern `%Cafe` anchors the search term to the end of the text. For example, "Bella Roma Cafe" matches, while "Cafe Royale" is correctly rejected.

---

### Query 3a: Name Contains One or More Digits (Regex)
- **Objective**: Filter restaurants whose name contains numerical characters (`0-9`).
- **Q Object Expression**:
  ```python
  name_has_digit_q = Q(name__regex=r'\d+')
  ```
- **ORM Lookup**: `regex` lookup using regular expression character class `\d+` (or `[0-9]`).
- **Generated SQL**:
  ```sql
  SELECT "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_restaurant"
  WHERE "restaurants_restaurant"."name" REGEXP '\d+'
  ORDER BY "restaurants_restaurant"."id" ASC;
  ```
- **Explanation**: Django leverages SQLite's user-defined function registration to provide full POSIX/Python regular expression support via the `REGEXP` SQL keyword.

---

### Query 3b: Profitable Sale OR Associated Restaurant Name Has Digits
- **Objective**: Query `Sale` records where income exceeds expenditure (`income > expenditure`), OR the associated restaurant has a digit in its name.
- **Q Object Expression**:
  ```python
  profitable_q = Q(income__gt=F('expenditure'))
  restaurant_has_digit_q = Q(restaurant__name__regex=r'\d+')
  sale_profitable_or_digit_restaurant_q = profitable_q | restaurant_has_digit_q
  ```
- **ORM Lookup**: `F()` expression comparing two model fields (`income` vs `expenditure`) combined via `|` with a relational regex filter across a foreign key (`restaurant__name__regex`).
- **Generated SQL**:
  ```sql
  SELECT "restaurants_sale"."id",
         "restaurants_sale"."restaurant_id",
         "restaurants_sale"."income",
         "restaurants_sale"."expenditure",
         "restaurants_restaurant"."id",
         "restaurants_restaurant"."name",
         "restaurants_restaurant"."restaurant_type",
         "restaurants_restaurant"."date_opened"
  FROM "restaurants_sale"
  INNER JOIN "restaurants_restaurant"
          ON ("restaurants_sale"."restaurant_id" = "restaurants_restaurant"."id")
  WHERE ("restaurants_sale"."income" > ("restaurants_sale"."expenditure")
     OR  "restaurants_restaurant"."name" REGEXP '\d+')
  ORDER BY "restaurants_sale"."id" ASC;
  ```
- **Explanation**: `F('expenditure')` instructs the database engine to perform column-to-column comparison directly inside the SQL `WHERE` clause without pulling records into Python memory.

---

## 3. Performance Optimization Benchmark: `select_related`

When querying related foreign keys in Django ORM, traversing relationships without optimization introduces the classic **N+1 query issue**:

```python
# Unoptimized (N+1 queries)
sales = Sale.objects.filter(sale_profitable_or_digit_restaurant_q)
for sale in sales:
    print(sale.restaurant.name)  # Triggers an individual SELECT query per iteration

# Optimized (Single SQL JOIN)
sales = Sale.objects.select_related('restaurant').filter(sale_profitable_or_digit_restaurant_q)
for sale in sales:
    print(sale.restaurant.name)  # Data already loaded from memory
```

### Empirical Test Results:
| Metric | Without `select_related` | With `select_related` | Improvement |
| :--- | :--- | :--- | :--- |
| **Sales Records Evaluated** | 12 | 12 | Identical dataset |
| **Database Queries Executed** | **13 queries** | **1 query** | **92.3% reduction** |
| **SQL Execution Strategy** | 1 query for Sales + 12 individual queries for Restaurants | 1 single `INNER JOIN` | Zero round-trip latency |

---

## 4. Query & Lookup Reference Summary

| Requirement | ORM Lookup | Encapsulated Variable | SQL Operator / Keyword |
| :--- | :--- | :--- | :--- |
| **Italian OR Mexican** | `exact` + `Q(...) \| Q(...)` | `italian_mexican_q` | `WHERE (col = 'Italian' OR col = 'Mexican')` |
| **Not Opened in 30 Days** | `gte` + `~Q(...)` | `not_recently_opened_q` | `WHERE NOT (col >= 'YYYY-MM-DD')` |
| **Type OR Recent** | `\|` Operator | `type_or_recently_opened_q` | `WHERE (col = 'A' OR col = 'B' OR col >= ...)` |
| **Contains "grill"** | `icontains` | `name_contains_grill_q` | `WHERE col LIKE '%grill%'` |
| **Ends with "Cafe"** | `endswith` | `name_ends_with_cafe_q` | `WHERE col LIKE '%Cafe'` |
| **Name Contains Digits** | `regex` | `name_has_digit_q` | `WHERE col REGEXP '\d+'` |
| **Profitable OR Digit Name** | `F()`, `gt`, `regex`, `\|` | `sale_profitable_or_digit_restaurant_q` | `WHERE (income > expenditure OR col REGEXP '\d+')` |
| **Optimized Sales Query** | `select_related('restaurant')` | `get_sales_profitable_or_restaurant_has_digit` | `INNER JOIN "restaurants_restaurant"` |

---

## 5. Verification & Test Suite
The implementation includes 9 automated unit tests verifying correctness, regex support, and query count assertions:
- `python manage.py test` → **9 passed, 0 failures, 0 errors**
- `python manage.py q_filter_demo` → **All queries successfully formatted and printed**

