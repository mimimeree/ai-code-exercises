# Exercise 17: Learning a New Framework with AI — FastAPI

---

## Part 1: Understanding FastAPI Fundamentals

### Prompt Used

> What is FastAPI and how does it compare to Flask? I've already seen Flask in Exercise 5 when we documented an API endpoint. Explain FastAPI's core concepts and why I might choose it over Flask.

### AI Response — FastAPI vs Flask

**What is FastAPI?**

FastAPI is a modern Python web framework for building APIs. It's built on top of Starlette (for the web parts) and Pydantic (for data validation). It was designed from the ground up to be fast to code, fast to run, and hard to get wrong.

**Comparison to Flask:**

| Aspect | Flask | FastAPI |
|--------|-------|---------|
| **Type checking** | None — you validate manually | Built-in via Pydantic models |
| **API docs** | Manual (we wrote them in Exercise 5) | Auto-generated at `/docs` |
| **Async support** | Limited (add-on) | Native `async/await` |
| **Speed** | Moderate | Very fast (comparable to Node.js) |
| **Error messages** | Generic | Detailed validation errors |
| **Learning curve** | Simpler to start | Slightly more concepts upfront, but fewer surprises later |

**Key insight:** Remember Exercise 5 where we manually wrote OpenAPI/Swagger documentation for the Flask user registration endpoint? FastAPI generates that *automatically* from your code. The type hints and Pydantic models you write for validation double as documentation.

### Core Concepts Glossary

| Term | What It Means | Python Equivalent You Know |
|------|--------------|---------------------------|
| **Endpoint** | A URL + HTTP method that does something (e.g., `GET /todos/`) | Same as Flask's routes |
| **Path parameter** | Variable in the URL: `/todos/{id}` extracts the ID | Flask's `<int:id>` |
| **Query parameter** | Optional filter after `?`: `/todos/?status=pending` | Flask's `request.args` |
| **Request body** | JSON data the client sends (for POST/PUT) | Flask's `request.json` |
| **Pydantic model** | A class that defines and validates data shape | Like a dataclass with validation |
| **Response model** | Defines what the API sends back | Flask's `jsonify()` return |
| **Status code** | HTTP result number (201=created, 404=not found) | Same everywhere |
| **Router** | Groups related endpoints together | Flask's `Blueprint` |
| **Dependency injection** | FastAPI automatically provides what your function needs | No direct Flask equivalent |
| **`async def`** | Non-blocking function (for handling many requests) | Same Python keyword |

### Design Philosophy

FastAPI's philosophy is: **"If you can describe the shape of your data, the framework handles the rest."**

In Flask, you:
1. Receive raw JSON
2. Manually check if required fields exist
3. Manually check if types are correct
4. Manually check if values are in valid ranges
5. Manually write error responses for each validation failure
6. Manually write API documentation

In FastAPI, you:
1. Define a Pydantic model (the data shape)
2. Use it as a function parameter
3. FastAPI handles steps 2-6 automatically

---

## Part 2: Creating the First API (Hello World)

### Prompt Used

> Show me a basic FastAPI "Hello World" with comments explaining each part, especially how it compares to Flask. I've used Flask decorators like @app.route('/api/users/register', methods=['POST']) before.

### Hello World — Flask vs FastAPI

```python
# ─── Flask (what we used in Exercise 5) ──────────────
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return jsonify({"item_id": item_id, "message": f"Item {item_id}"})

# Run: flask run
```

```python
# ─── FastAPI equivalent ──────────────────────────────
from fastapi import FastAPI
app = FastAPI()

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    return {"item_id": item_id, "message": f"Item {item_id}"}

# Run: uvicorn main:app --reload
```

**What's different:**

1. **Decorator syntax:** Flask uses `@app.route('/path', methods=['GET'])`. FastAPI uses `@app.get("/path")` — the HTTP method is part of the decorator name, which is cleaner.

2. **Path parameters:** Flask uses `<int:item_id>`. FastAPI uses `{item_id}` in the path and `item_id: int` in the function signature — the type hint IS the validation.

3. **No jsonify needed:** Flask requires `jsonify()` to convert dicts to JSON. FastAPI does it automatically.

4. **`async def`:** FastAPI functions are async by default. This means the server can handle other requests while waiting for slow operations (like database queries). Flask functions block until they finish.

5. **Auto-docs:** Visit `/docs` and you get an interactive Swagger UI — the same thing we manually wrote in YAML in Exercise 5.

---

## Part 3: The To-Do API — Full Implementation

### Project Structure

```
todo_api/
├── app/
│   ├── __init__.py           # Makes app/ a Python package
│   ├── main.py               # FastAPI app creation and config
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py           # Pydantic models (data shapes)
│   ├── routes/
│   │   ├── __init__.py
│   │   └── todos.py          # API endpoints (CRUD operations)
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py     # Custom error handling
└── test_todos.py             # Test suite
```

**Why this structure?** It follows **separation of concerns** (Exercise 12):
- `models/` — defines what the data looks like
- `routes/` — defines what the API does
- `utils/` — shared helper code
- `main.py` — orchestrator that wires everything together

### New Concepts Learned

#### Pydantic Models — Validation as Code

The biggest difference from Flask. Instead of manually checking request data:

```python
# Flask approach (Exercise 5) — manual validation
@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if 'username' not in data:
        return jsonify({"error": "username required"}), 400
    if len(data['username']) < 3:
        return jsonify({"error": "username too short"}), 400
    # ... more manual checks ...
```

```python
# FastAPI approach — declare the shape, validation is automatic
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[date] = None

@router.post("/")
async def create_todo(todo: TodoCreate):
    # If we get here, `todo` is guaranteed valid
    # FastAPI already rejected bad requests with detailed error messages
    pass
```

**What `Field()` does:**
- `...` (Ellipsis) means "required, no default"
- `None` means "optional, defaults to None"
- `min_length`, `max_length`, `gt`, `ge`, `le` add validation rules
- `description` appears in the auto-generated docs

**What `Optional[str]` means:** The type hint `Optional[str]` means "this can be a string OR None." It's Python's way of saying "this field is optional." Equivalent to `str | None` in Python 3.10+.

#### Separate Models for Different Operations

```python
class TodoCreate(BaseModel):    # For POST — title required, no id/status
class TodoUpdate(BaseModel):    # For PUT  — all fields optional (partial update)
class TodoResponse(BaseModel):  # For GET  — includes id and status
```

**Why three models?** Because each operation needs different data:
- **Creating:** Client provides title (required) + optional fields. No ID yet.
- **Updating:** Client sends only the fields they want to change. Everything optional.
- **Responding:** Server sends everything including the generated ID and status.

This is a common API design pattern called **request/response models**.

#### `model_dump(exclude_unset=True)` — Partial Updates

```python
update_data = updates.model_dump(exclude_unset=True)
```

This is the key to partial updates. If the client sends `{"status": "completed"}`, only `status` is in the dict — title, description, and due_date are excluded because the client didn't set them. Without `exclude_unset=True`, you'd get `{"title": None, "description": None, ...}` which would accidentally erase existing data.

#### APIRouter — Organizing Endpoints

```python
# routes/todos.py
router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/")     # Becomes POST /todos/
@router.get("/")      # Becomes GET /todos/
@router.get("/{id}")  # Becomes GET /todos/{id}
```

```python
# main.py
app.include_router(todos.router)  # Plug it into the app
```

`APIRouter` is like Flask's `Blueprint` — it groups related endpoints. The `prefix="/todos"` means every route in this router starts with `/todos/`. The `tags=["todos"]` groups them in the docs.

**Adding a new resource** (like users) would mean creating `routes/users.py` with its own router, and adding `app.include_router(users.router)` in main.py. The existing code doesn't change.

#### Query() and Path() — Parameter Validation

```python
@router.get("/")
async def list_todos(
    status_filter: Optional[TodoStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
```

`Query()` and `Path()` add validation to URL parameters, just like `Field()` does for request body fields:
- `ge=0` means "greater than or equal to 0" — can't skip a negative number
- `ge=1, le=100` means "between 1 and 100" — can't request 0 or 10000 items
- `alias="status"` means the URL uses `?status=pending` but the Python variable is `status_filter`

#### HTTP Status Codes in Practice

| Code | Meaning | When We Use It |
|------|---------|---------------|
| **200** | OK | Successful GET, PUT |
| **201** | Created | Successful POST (new resource created) |
| **204** | No Content | Successful DELETE (nothing to return) |
| **404** | Not Found | Item doesn't exist |
| **422** | Unprocessable Entity | Validation failed (bad input data) |

These map exactly to the status codes we documented in Exercise 5, but now we see them from the *server* side instead of the *documentation* side.

### Test Results

```
==================================================
To-Do API — Test Suite
==================================================

--- CREATE ---
✅ Created to-do item (ID: 1)
✅ Created minimal to-do (ID: 2)
✅ Validation error caught (missing title)
✅ Validation error caught (empty title)

--- READ ---
✅ Listed 2 to-do items
✅ Retrieved to-do item 1: 'Learn FastAPI'
✅ 404 returned for nonexistent item

--- UPDATE ---
✅ Updated to-do 1 (partial update)
✅ Marked to-do 1 as completed
✅ Filtered pending: 1 items
✅ Filtered completed: 1 items
✅ Pagination works (limit=1 returned 1 item)

--- DELETE ---
✅ Deleted to-do 2 (verified with 404)
✅ 404 returned when deleting nonexistent item

--- ROOT ---
✅ Root endpoint works

==================================================
All tests passed! ✅
==================================================
```

14 tests covering all CRUD operations, validation, filtering, pagination, and error handling.

---

## Part 4: Reflection

### How FastAPI Connects to Previous Exercises

| Previous Exercise | Connection to FastAPI |
|-------------------|---------------------|
| **Ex 5 (API Docs)** | We manually wrote OpenAPI/Swagger YAML for Flask. FastAPI generates it automatically from type hints. |
| **Ex 10 (Testing)** | Same test pattern: arrange inputs, call function, assert results. FastAPI's TestClient is like Flask's test client. |
| **Ex 12 (Function Decomposition)** | The project structure uses the orchestrator pattern: `main.py` delegates to routers, which delegate to models and utils. |
| **Ex 13 (Readability)** | Pydantic models are self-documenting — `Field(min_length=1, max_length=200)` is clearer than manual `if len(title) < 1`. |
| **Ex 14 (Design Patterns)** | The Factory pattern appears in the router system: `app.include_router()` plugs in new endpoint groups without modifying existing code. |

### What FastAPI Does Differently (and Better)

1. **Type hints are the API.** In Flask, type hints are optional documentation. In FastAPI, they ARE the validation, serialization, and documentation. One source of truth instead of three.

2. **Errors are specific.** Send `{"title": ""}` to the create endpoint and you get: `"String should have at least 1 character"` with the exact field name and constraint. In Flask, you'd have to write that error message yourself.

3. **The /docs page is free.** Visit `/docs` and you get interactive documentation where you can try every endpoint directly from the browser. We spent an entire exercise (Ex 5) learning to write this manually.

### What Felt Familiar from Python

- **Decorators:** `@router.get("/")` works exactly like Flask's `@app.route("/")`
- **Type hints:** `item_id: int` is standard Python, FastAPI just uses it for validation
- **Enums:** `TodoStatus(str, Enum)` is the same pattern as our `TaskStatus` and `TaskPriority`
- **Dictionaries:** The in-memory storage is just a Python dict, same as always
- **List comprehensions:** Filtering with `[item for item in items if condition]`
- **f-strings:** Error messages use `f"Item {todo_id} not found"`
- **Testing:** `assert response.status_code == 200` is standard Python assertions

### Gaps to Explore Next

- **Database integration** — Replace the in-memory dict with SQLite or PostgreSQL using SQLAlchemy
- **Authentication** — Add user accounts and API keys
- **Background tasks** — Process things asynchronously (FastAPI supports this natively)
- **Middleware** — Add logging, CORS, rate limiting
- **Deployment** — Run the API on a real server
