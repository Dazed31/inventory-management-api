# Inventory Management System — Flask REST API

## A Bit of Backstory

When I first got this summative lab, I honestly didn't know where to start. It felt like a lot all at once, building a full CRUD API, hooking it up to an external API, building a CLI on top of it, and writing tests for all of it. I asked a bunch of people for help trying to piece together a plan, and I also reached out to my Technical Mentor (TM) for guidance. I ended up getting sidetracked and never actually followed up with him, which in hindsight is something I want to be better about next time, following through on the help that's offered instead of trying to figure everything out solo after the fact.

Eventually I worked through it step by step: getting the Flask routes working first, then the external API integration, then the CLI, then the tests. It wasn't a straight line, there were a fair number of errors and moments of "why isn't this working" along the way (documented below), but I got through it.

## Project Overview

This is a Flask-based REST API for managing a store's inventory. It supports full CRUD operations (Create, Read, Update, Delete) on inventory items, and integrates with the [OpenFoodFacts API](https://world.openfoodfacts.org) to pull in real product data by barcode or product name. A command-line interface (CLI) is included so the API can be used interactively without needing Postman or curl.

### Features

- Flask REST API with full CRUD endpoints for inventory management
- Integration with the OpenFoodFacts API to fetch real product data by barcode or name
- CLI tool to add, view, update, delete, and search for inventory items
- In-memory data storage (simulated database) using a Python list
- Unit tests covering the Flask routes and the external API integration, using `pytest` and `unittest.mock`

## Tech Stack

- Python 3
- Flask
- Requests (for calling the external API)
- Pytest + unittest.mock (for testing)

## Project Structure

```
inventory-management-api/
├── app.py                     # Flask app and CRUD routes
├── external_api.py            # OpenFoodFacts API integration
├── cli.py                     # Command-line interface
├── requirements.txt
├── pytest.ini
├── tests/
│   ├── __init__.py
│   ├── test_app.py            # Tests for Flask routes
│   └── test_external_api.py   # Tests for external API integration
└── README.md
```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Dazed31/inventory-management-api.git
   cd inventory-management-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (or manually: `pip install flask requests pytest`)

4. Run the Flask server:
   ```bash
   python app.py
   ```
   The API will be running at `http://localhost:5000`.

5. In a separate terminal (with the server running), run the CLI:
   ```bash
   python cli.py
   ```

6. Run the test suite:
   ```bash
   pytest -v
   ```

## Data Model

Each inventory item is stored as a dictionary with the following shape:

```json
{
  "id": 1,
  "product_name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "3274080005003",
  "quantity": 20,
  "price": 3.49,
  "ingredients_text": "Filtered water, almonds, cane sugar"
}
```

This structure mirrors the kind of data OpenFoodFacts returns, so items pulled from the external API slot directly into the same inventory list as manually added items.

## API Endpoints

### `GET /`
Welcome message confirming the API is running.

**Response — 200 OK**
```json
{ "message": "Welcome to the Inventory Management API" }
```

---

### `GET /inventory`
Returns all inventory items.

**Response — 200 OK**
```json
[
  { "id": 1, "product_name": "Organic Almond Milk", "brand": "Silk", "barcode": "3274080005003", "quantity": 20, "price": 3.49, "ingredients_text": "..." },
  { "id": 2, "product_name": "Peanut Butter", "brand": "Jif", "barcode": "0051500255162", "quantity": 15, "price": 4.99, "ingredients_text": "..." }
]
```

---

### `GET /inventory/<id>`
Returns a single item by id.

**Response — 200 OK**
```json
{ "id": 1, "product_name": "Organic Almond Milk", "brand": "Silk", "barcode": "3274080005003", "quantity": 20, "price": 3.49, "ingredients_text": "..." }
```

**Response — 404 Not Found**
```json
{ "error": "Item with id 99 not found" }
```

---

### `POST /inventory`
Creates a new inventory item. Requires `product_name`.

**Request**
```json
{ "product_name": "Coffee", "brand": "Nescafe", "quantity": 12, "price": 6.99 }
```

**Response — 201 Created**
```json
{ "id": 3, "product_name": "Coffee", "brand": "Nescafe", "barcode": "", "quantity": 12, "price": 6.99, "ingredients_text": "" }
```

**Response — 400 Bad Request** (missing product_name)
```json
{ "error": "Missing required field: product_name" }
```

---

### `PATCH /inventory/<id>`
Updates one or more fields on an existing item (e.g. quantity or price).

**Request**
```json
{ "quantity": 50 }
```

**Response — 200 OK**
```json
{ "id": 1, "product_name": "Organic Almond Milk", "brand": "Silk", "barcode": "3274080005003", "quantity": 50, "price": 3.49, "ingredients_text": "..." }
```

**Response — 404 Not Found**
```json
{ "error": "Item with id 99 not found" }
```

---

### `DELETE /inventory/<id>`
Removes an item from inventory.

**Response — 204 No Content**
(empty body)

**Response — 404 Not Found**
```json
{ "error": "Item with id 99 not found" }
```

---

### `POST /inventory/fetch/<barcode>`
Looks up a product on OpenFoodFacts by barcode and adds it directly to the inventory. Optional `quantity` and `price` can be included in the request body since OpenFoodFacts doesn't track those.

**Request**
```json
{ "quantity": 10, "price": 3.99 }
```

**Response — 201 Created**
```json
{ "id": 4, "product_name": "Some Product", "brand": "Some Brand", "barcode": "1234567890123", "quantity": 10, "price": 3.99, "ingredients_text": "..." }
```

**Response — 404 Not Found** (barcode doesn't match any product)
```json
{ "error": "No product found for barcode 1234567890123" }
```

**Response — 502 Bad Gateway** (OpenFoodFacts couldn't be reached)
```json
{ "error": "Failed to reach OpenFoodFacts API: ..." }
```

---

### `GET /inventory/search?name=<query>`
Searches OpenFoodFacts by product name (does not add anything to inventory — just returns results).

**Response — 200 OK**
```json
[
  { "product_name": "Almond Milk", "brands": "Silk", "barcode": "123", "ingredients_text": "..." }
]
```

**Response — 400 Bad Request** (missing name parameter)
```json
{ "error": "Name query parameter is required" }
```

**Response — 404 Not Found** (no matches)
```json
{ "error": "No results found" }
```

## CLI Usage

With the Flask server running (`python app.py`), start the CLI in another terminal:

```bash
python cli.py
```

You'll get a menu like this:

```
--- Inventory Management CLI ---
1. View all inventory
2. View single item
3. Add new item
4. Update item (quantity/price)
5. Delete item
6. Find product on OpenFoodFacts and add
7. Exit
```

Example flow — adding a real product by barcode:
```
Choose an option: 6
Enter barcode to search and add: 3274080005003
Quantity to store (optional): 10
Price (optional): 3.49
Item fetched and added: {'id': 3, 'product_name': 'Organic Almond Milk', ...}
```

## Testing

Tests are split into two files:

- **`tests/test_app.py`** — tests every Flask route (GET, POST, PATCH, DELETE), including success cases and error cases (missing fields, not-found ids). External API calls are mocked using `unittest.mock.patch` so tests don't depend on network access or OpenFoodFacts actually being up.
- **`tests/test_external_api.py`** — tests `fetch_product_by_barcode` and `fetch_product_by_name` directly, mocking `requests.get` to simulate found products, not-found products, and network failures.

Run everything with:
```bash
pytest -v
```

## Challenges Along the Way

Building this wasn't smooth from start to finish, a few things tripped me up that are worth noting (partly for my own future reference, partly in case anyone else runs into the same thing):

- **Git branch confusion**: I created a `feature-external-api` branch, but a later commit accidentally landed on `master` instead because I wasn't actually on the feature branch when I ran the commands. This caused a `src refspec ... does not match any` error when trying to push to a branch that, from my local repo's perspective, didn't have that commit on it.
- **Juggling multiple feature branches got confusing fast**: Trying to keep a separate branch per feature (`feature-external-api`, `feature-flask-crud`, `feature-cli`, `feature-tests`) and constantly switching between them with `git checkout` led to commits landing on the wrong branch, mismatched pushes, and general confusion about which branch had which code. Rather than keep fighting that workflow mid-lab, I made the call to simplify and just work directly on `master` — one branch, one clear history, commit by commit. It's a trade-off (less practice with a full branch/PR workflow), but it let me actually focus on getting the features working instead of debugging git itself.
- **Untracked branch pushes**: The first time pushing a new branch, `git push` alone failed with "no upstream branch" — this needed `git push --set-upstream origin <branch-name>` instead.
- **Function name mismatch**: My `external_api.py` originally defined `fetch_products_by_name` (plural), but `app.py` and the tests were written expecting `fetch_product_by_name` (singular). This caused a cascade of `ImportError` and `NameError` failures across both `pytest` collection and the actual route logic, until every reference to the function name was made consistent.
- **Understanding pytest test discovery**: Early on I ran `pytest app.py` instead of pointing it at the actual test file, which tried to import Flask directly as a test module. Learning the difference between "the file with the code" and "the file with the tests" (and that pytest needs the *test* file) cleared this up.

Working through these errors, reading the tracebacks instead of just re-pasting code — ended up being one of the more useful parts of the lab, even though it was frustrating in the moment.

## Future Improvements

- Swap the in-memory list for a real database (e.g. SQLite with SQLAlchemy) so data persists across restarts.
- Add authentication for write operations, consistent with how OpenFoodFacts itself gates its write endpoints.
- Add pagination to `GET /inventory` for larger inventories.
- Expand the CLI to support editing more fields (currently limited to quantity and price for updates).