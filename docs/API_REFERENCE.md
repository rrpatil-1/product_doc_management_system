# API Reference — Product Management System

## Overview

This document provides comprehensive API reference for the Product Management System REST API. All endpoints are RESTful and return JSON responses.

**Base URL**: `http://localhost:8000/api/v1/products`

**Authentication**: Currently optional (client-side only). Server endpoints are open.

## Response Format

### Success Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Example Product",
  "category": "Electronics",
  "description": "Product description",
  "price": 99.99,
  "discount": 10.00,
  "thumbnail_url": "https://example.com/image.jpg"
}
```

### Error Response
```json
{
  "error": "error_type",
  "message": "Human-readable error description",
  "code": "ERROR_CODE",
  "details": [
    {
      "field": "field_name",
      "message": "Specific error message",
      "code": "FIELD_ERROR_CODE"
    }
  ],
  "timestamp": "2024-04-02T10:30:00"
}
```

## Endpoints

### 1. Create Product

Creates a new product.

**Request**
```
POST /
Content-Type: application/json
```

**Request Body**
```json
{
  "name": "Wireless Mouse",
  "category": "Peripherals",
  "description": "Bluetooth wireless mouse with ergonomic design",
  "price": 29.99,
  "discount": 5.00,
  "thumbnail_url": "https://example.com/mouse.jpg",
  "id": "optional-custom-id"
}
```

**Parameters**
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| name | string | Yes | min_length: 1 |
| category | string | Yes | min_length: 1 |
| description | string | Yes | min_length: 1 |
| price | number | Yes | > 0 |
| discount | number | No | >= 0, default: 0 |
| thumbnail_url | string | No | Valid HTTP/HTTPS URL |
| id | string | No | Auto-generated UUID if omitted |

**Response**
```
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Wireless Mouse",
  "category": "Peripherals",
  "description": "Bluetooth wireless mouse with ergonomic design",
  "price": 29.99,
  "discount": 5.0,
  "thumbnail_url": "https://example.com/mouse.jpg"
}
```

**Error Responses**
- `400 Bad Request`: Validation error (negative price, invalid URL, etc.)
- `409 Conflict`: Duplicate product ID
- `422 Unprocessable Entity`: Invalid request format

**Examples**

cURL:
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "category": "Peripherals",
    "description": "Bluetooth wireless mouse",
    "price": 29.99,
    "discount": 5.00
  }'
```

Python:
```python
import httpx

client = httpx.Client()
response = client.post(
    "http://localhost:8000/api/v1/products/",
    json={
        "name": "Wireless Mouse",
        "category": "Peripherals",
        "description": "Bluetooth wireless mouse",
        "price": 29.99,
        "discount": 5.00
    }
)
print(response.json())
```

---

### 2. List Products

Retrieves a paginated list of products with optional sorting.

**Request**
```
GET /?skip=0&limit=10&sort_field=name&sort_order=asc
```

**Query Parameters**
| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| skip | integer | 0 | >= 0 | Number of products to skip |
| limit | integer | 10 | 1-100 | Max products per page |
| sort_field | string | "name" | name, category, price, discount | Field to sort by |
| sort_order | string | "asc" | asc, desc | Sort direction |

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "total": 50,
  "skip": 0,
  "limit": 10,
  "products": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Product 1",
      "category": "Electronics",
      "description": "Description 1",
      "price": 99.99,
      "discount": 10.0,
      "thumbnail_url": "https://example.com/1.jpg"
    },
    ...
  ]
}
```

**Error Responses**
- `400 Bad Request`: Invalid sort_field or sort_order

**Examples**

cURL:
```bash
# Default pagination and sorting
curl "http://localhost:8000/api/v1/products/"

# Custom pagination and sorting
curl "http://localhost:8000/api/v1/products/?skip=10&limit=20&sort_field=price&sort_order=desc"
```

Python:
```python
import httpx

client = httpx.Client()
response = client.get(
    "http://localhost:8000/api/v1/products/",
    params={
        "skip": 0,
        "limit": 10,
        "sort_field": "price",
        "sort_order": "desc"
    }
)
data = response.json()
print(f"Total products: {data['total']}")
print(f"Current page: {len(data['products'])} products")
```

---

### 3. Get Single Product

Retrieves a specific product by ID.

**Request**
```
GET /{product_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| product_id | string | Unique product identifier |

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Wireless Mouse",
  "category": "Peripherals",
  "description": "Bluetooth wireless mouse",
  "price": 29.99,
  "discount": 5.0,
  "thumbnail_url": "https://example.com/mouse.jpg"
}
```

**Error Responses**
- `404 Not Found`: Product doesn't exist

**Examples**

cURL:
```bash
curl "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000"
```

Python:
```python
import httpx

client = httpx.Client()
response = client.get("http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000")
if response.status_code == 200:
    product = response.json()
    print(f"Product: {product['name']} - ${product['price']}")
else:
    print("Product not found")
```

---

### 4. Update Product

Updates an existing product (full or partial update).

**Request**
```
PUT /{product_id}
Content-Type: application/json
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| product_id | string | Unique product identifier |

**Request Body** (all fields optional)
```json
{
  "name": "Updated Name",
  "category": "Updated Category",
  "description": "Updated description",
  "price": 39.99,
  "discount": 3.00,
  "thumbnail_url": "https://example.com/new.jpg"
}
```

**Parameters**
| Field | Type | Constraints |
|-------|------|-------------|
| name | string | min_length: 1 |
| category | string | min_length: 1 |
| description | string | min_length: 1 |
| price | number | > 0 |
| discount | number | >= 0 |
| thumbnail_url | string | Valid HTTP/HTTPS URL |

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Updated Name",
  "category": "Updated Category",
  "description": "Updated description",
  "price": 39.99,
  "discount": 3.0,
  "thumbnail_url": "https://example.com/new.jpg"
}
```

**Error Responses**
- `404 Not Found`: Product doesn't exist
- `400 Bad Request`: Validation error
- `422 Unprocessable Entity`: Invalid request format

**Examples**

cURL (partial update):
```bash
curl -X PUT "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"price": 39.99}'
```

cURL (full update):
```bash
curl -X PUT "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Mouse",
    "category": "Accessories",
    "description": "Updated wireless mouse",
    "price": 39.99,
    "discount": 3.00
  }'
```

Python:
```python
import httpx

client = httpx.Client()
response = client.put(
    "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000",
    json={"price": 39.99}
)
if response.status_code == 200:
    updated = response.json()
    print(f"New price: ${updated['price']}")
```

---

### 5. Delete Product

Deletes an existing product.

**Request**
```
DELETE /{product_id}
```

**Path Parameters**
| Parameter | Type | Description |
|-----------|------|-------------|
| product_id | string | Unique product identifier |

**Response**
```
HTTP/1.1 204 No Content
```

(or)

```
HTTP/1.1 200 OK
Content-Type: application/json

{"message": "Product deleted successfully"}
```

**Error Responses**
- `404 Not Found`: Product doesn't exist

**Examples**

cURL:
```bash
curl -X DELETE "http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000"
```

Python:
```python
import httpx

client = httpx.Client()
response = client.delete("http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000")
if response.status_code in [200, 204]:
    print("Product deleted successfully")
else:
    print("Product not found")
```

---

### 6. Search Products

Searches products by name, category, or description.

**Request**
```
GET /search/?q=keyword&field=name
```

**Query Parameters**
| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| q | string | Yes | min_length: 1 | Search query |
| field | string | No | name, category, description | Specific field to search (searches all if omitted) |

**Response**
```
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Wireless Mouse",
    "category": "Peripherals",
    "description": "Bluetooth wireless mouse",
    "price": 29.99,
    "discount": 5.0,
    "thumbnail_url": "https://example.com/mouse.jpg"
  },
  ...
]
```

**Search Behavior**
- Case-insensitive regex matching
- Searches across multiple fields if `field` is omitted
- Returns all matching products (no pagination)

**Error Responses**
- `400 Bad Request`: Invalid field parameter
- `422 Unprocessable Entity`: Missing required `q` parameter

**Examples**

cURL (search all fields):
```bash
curl "http://localhost:8000/api/v1/products/search/?q=mouse"
```

cURL (search specific field):
```bash
curl "http://localhost:8000/api/v1/products/search/?q=wireless&field=name"
```

cURL (search by category):
```bash
curl "http://localhost:8000/api/v1/products/search/?q=electronics&field=category"
```

Python:
```python
import httpx

client = httpx.Client()
response = client.get(
    "http://localhost:8000/api/v1/products/search/",
    params={
        "q": "mouse",
        "field": "name"
    }
)
results = response.json()
print(f"Found {len(results)} products matching 'mouse'")
for product in results:
    print(f"  - {product['name']}: ${product['price']}")
```

---

## HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PUT, DELETE (with response) |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE (no response body) |
| 400 | Bad Request | Validation error, invalid input |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate product ID |
| 422 | Unprocessable Entity | Request format invalid |
| 500 | Internal Server Error | Unexpected server error |

## Rate Limiting

Currently not implemented. Production deployments should implement rate limiting.

## Versioning

API version: `v1` (included in base URL: `/api/v1/products`)

Future incompatible changes will use `/api/v2/products`

## Pagination Guidelines

For optimal performance:
- Use `limit` <= 100 per request
- Implement client-side pagination UI
- Cache frequently accessed pages
- Use `skip` + `limit` for offset-based pagination

Example pagination flow:
```python
import httpx

client = httpx.Client()

# Get first page
response = client.get(
    "http://localhost:8000/api/v1/products/",
    params={"skip": 0, "limit": 10}
)
data = response.json()

total = data["total"]
page_size = data["limit"]
pages = (total + page_size - 1) // page_size  # Ceiling division

print(f"Total pages: {pages}")
print(f"Products in first page: {len(data['products'])}")
```

## Sorting Examples

```bash
# Sort by price (low to high)
curl "http://localhost:8000/api/v1/products/?sort_field=price&sort_order=asc"

# Sort by name (Z to A)
curl "http://localhost:8000/api/v1/products/?sort_field=name&sort_order=desc"

# Sort by category with custom limit
curl "http://localhost:8000/api/v1/products/?sort_field=category&sort_order=asc&limit=20"
```

## Error Handling Best Practices

Always check HTTP status before processing response:

```python
import httpx

client = httpx.Client()
try:
    response = client.post(
        "http://localhost:8000/api/v1/products/",
        json={"name": "Product", "price": 50.00},
        timeout=10
    )
    
    if response.status_code == 201:
        product = response.json()
        print(f"Created: {product['id']}")
    elif response.status_code == 400:
        error = response.json()
        print(f"Validation error: {error['message']}")
        for detail in error.get("details", []):
            print(f"  Field: {detail['field']}, Message: {detail['message']}")
    else:
        print(f"Unexpected status: {response.status_code}")
        
except httpx.TimeoutException:
    print("Request timed out")
except httpx.RequestError as e:
    print(f"Request failed: {e}")
```

## Integration Examples

### Batch Create Products

```python
import httpx
import time

client = httpx.Client()

products = [
    {"name": "Product 1", "category": "Electronics", "description": "Desc 1", "price": 99.99},
    {"name": "Product 2", "category": "Electronics", "description": "Desc 2", "price": 199.99},
    {"name": "Product 3", "category": "Software", "description": "Desc 3", "price": 49.99},
]

created_ids = []
for product in products:
    response = client.post(
        "http://localhost:8000/api/v1/products/",
        json=product
    )
    if response.status_code == 201:
        created_ids.append(response.json()["id"])
        print(f"✓ Created: {product['name']}")
    else:
        print(f"✗ Failed: {product['name']} - {response.status_code}")
        
print(f"\nCreated {len(created_ids)} products")
```

### Export to CSV

```python
import httpx
import csv

client = httpx.Client()
response = client.get("http://localhost:8000/api/v1/products/?limit=100")
data = response.json()

with open("products.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["id", "name", "category", "price", "discount"])
    writer.writeheader()
    for product in data["products"]:
        writer.writerow({
            "id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "discount": product["discount"]
        })
        
print(f"Exported {len(data['products'])} products to products.csv")
```

---

**Last Updated**: April 2, 2026  
**API Version**: 1.0
