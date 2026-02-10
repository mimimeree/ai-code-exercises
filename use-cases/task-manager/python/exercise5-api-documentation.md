# Exercise 5: API Documentation

## API Chosen: Python/Flask User Registration Endpoint

---

## Original API Endpoint Code

```python
@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': 'Missing required field',
                'message': f'{field} is required'
            }), 400

    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({
            'error': 'Username taken',
            'message': 'Username is already in use'
        }), 409

    if User.query.filter_by(email=data['email']).first():
        return jsonify({
            'error': 'Email exists',
            'message': 'An account with this email already exists'
        }), 409

    # Validate email format
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", data['email']):
        return jsonify({
            'error': 'Invalid email',
            'message': 'Please provide a valid email address'
        }), 400

    # Validate password strength
    if len(data['password']) < 8:
        return jsonify({
            'error': 'Weak password',
            'message': 'Password must be at least 8 characters long'
        }), 400

    # Create new user
    try:
        password_hash = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'].lower(),
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()

        confirmation_token = generate_confirmation_token(new_user.id)
        try:
            send_confirmation_email(new_user.email, confirmation_token)
        except Exception as e:
            app.logger.error(f"Failed to send confirmation email: {str(e)}")

        user_data = {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'created_at': new_user.created_at.isoformat(),
            'role': new_user.role
        }

        return jsonify({
            'message': 'User registered successfully',
            'user': user_data
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': 'Failed to register user'
        }), 500
```

---

## Prompt 1 Output: Comprehensive Endpoint Documentation

# User Registration API

Register a new user account in the system. This endpoint validates the provided information, creates the user in the database, hashes the password for security, and sends a confirmation email.

## Endpoint

`POST /api/users/register`

## Authentication

No authentication required — this is a public endpoint for new user registration.

## Request

### Headers

| Header       | Value              | Required |
|--------------|--------------------|----------|
| Content-Type | application/json   | Yes      |

### Request Body

| Field    | Type   | Required | Description                          | Constraints                    |
|----------|--------|----------|--------------------------------------|--------------------------------|
| username | String | Yes      | Desired username for the account     | Must be unique across all users |
| email    | String | Yes      | User's email address                 | Must be valid email format; must be unique; stored in lowercase |
| password | String | Yes      | Account password                     | Minimum 8 characters           |

### Example Request Body

```json
{
  "username": "janedoe",
  "email": "jane@example.com",
  "password": "securePass123"
}
```

## Responses

### 201 Created — Registration Successful

Returned when the user is successfully created.

```json
{
  "message": "User registered successfully",
  "user": {
    "id": 42,
    "username": "janedoe",
    "email": "jane@example.com",
    "created_at": "2026-02-09T14:30:00",
    "role": "user"
  }
}
```

**Note:** The password is never included in the response. A confirmation email is sent to the provided email address. If the email fails to send, the user is still created — the email failure is logged but does not block registration.

### 400 Bad Request — Missing Required Field

Returned when any of the required fields (username, email, password) is missing.

```json
{
  "error": "Missing required field",
  "message": "email is required"
}
```

### 400 Bad Request — Invalid Email Format

Returned when the email does not match a valid format.

```json
{
  "error": "Invalid email",
  "message": "Please provide a valid email address"
}
```

### 400 Bad Request — Weak Password

Returned when the password is shorter than 8 characters.

```json
{
  "error": "Weak password",
  "message": "Password must be at least 8 characters long"
}
```

### 409 Conflict — Username Already Taken

Returned when a user with the same username already exists.

```json
{
  "error": "Username taken",
  "message": "Username is already in use"
}
```

### 409 Conflict — Email Already Registered

Returned when a user with the same email already exists.

```json
{
  "error": "Email exists",
  "message": "An account with this email already exists"
}
```

### 500 Internal Server Error — Server Failure

Returned when an unexpected error occurs during user creation. The database transaction is rolled back.

```json
{
  "error": "Server error",
  "message": "Failed to register user"
}
```

## Example Requests

### Example 1: Successful Registration

**Request:**
```
POST /api/users/register
Content-Type: application/json

{
  "username": "alex_smith",
  "email": "Alex.Smith@example.com",
  "password": "myStr0ngP@ss"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 15,
    "username": "alex_smith",
    "email": "alex.smith@example.com",
    "created_at": "2026-02-09T12:00:00",
    "role": "user"
  }
}
```

Note: The email is stored in lowercase regardless of input.

### Example 2: Registration with Missing Fields

**Request:**
```
POST /api/users/register
Content-Type: application/json

{
  "username": "bob"
}
```

**Response (400):**
```json
{
  "error": "Missing required field",
  "message": "email is required"
}
```

## Important Notes

- Passwords are hashed using `generate_password_hash()` before storage — plaintext passwords are never stored
- Email addresses are normalized to lowercase before storage
- The validation order is: required fields → username uniqueness → email uniqueness → email format → password strength
- All new users are assigned the role `"user"` by default
- If the confirmation email fails to send, the registration still succeeds — the failure is only logged
- On any database error during creation, the transaction is rolled back to prevent partial data

---

## Prompt 2 Output: OpenAPI/Swagger Format

```yaml
openapi: 3.0.0
info:
  title: User Registration API
  description: API endpoint for creating new user accounts
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /api/users/register:
    post:
      summary: Register a new user
      description: >
        Creates a new user account. Validates input, checks for duplicate
        usernames and emails, hashes the password, and sends a confirmation email.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - username
                - email
                - password
              properties:
                username:
                  type: string
                  description: Desired username (must be unique)
                  example: janedoe
                email:
                  type: string
                  format: email
                  description: User's email address (must be unique, stored lowercase)
                  example: jane@example.com
                password:
                  type: string
                  format: password
                  minLength: 8
                  description: Account password (minimum 8 characters)
                  example: securePass123
      responses:
        '201':
          description: User registered successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: User registered successfully
                  user:
                    $ref: '#/components/schemas/UserResponse'
        '400':
          description: Invalid input (missing field, invalid email, or weak password)
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                missingField:
                  summary: Missing required field
                  value:
                    error: Missing required field
                    message: email is required
                invalidEmail:
                  summary: Invalid email format
                  value:
                    error: Invalid email
                    message: Please provide a valid email address
                weakPassword:
                  summary: Password too short
                  value:
                    error: Weak password
                    message: Password must be at least 8 characters long
        '409':
          description: Username or email already exists
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              examples:
                usernameTaken:
                  summary: Username already in use
                  value:
                    error: Username taken
                    message: Username is already in use
                emailExists:
                  summary: Email already registered
                  value:
                    error: Email exists
                    message: An account with this email already exists
        '500':
          description: Internal server error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
              example:
                error: Server error
                message: Failed to register user
components:
  schemas:
    UserResponse:
      type: object
      properties:
        id:
          type: integer
          description: Unique user ID
          example: 42
        username:
          type: string
          description: User's username
          example: janedoe
        email:
          type: string
          format: email
          description: User's email (lowercase)
          example: jane@example.com
        created_at:
          type: string
          format: date-time
          description: Account creation timestamp (ISO 8601)
          example: "2026-02-09T14:30:00"
        role:
          type: string
          description: User role
          example: user
    Error:
      type: object
      properties:
        error:
          type: string
          description: Error type identifier
        message:
          type: string
          description: Human-readable error description
```

---

## Prompt 3 Output: Developer Usage Guide

# Developer Guide: User Registration Endpoint

This guide walks you through how to register new users via the API. It's written for developers who are integrating this endpoint into a frontend application, mobile app, or third-party service.

## Quick Start

To register a new user, send a `POST` request to `/api/users/register` with a JSON body containing `username`, `email`, and `password`.

## Step 1: Format Your Request

The endpoint expects a JSON body with three required fields:

```python
import requests

url = "https://api.example.com/api/users/register"
headers = {"Content-Type": "application/json"}

payload = {
    "username": "janedoe",
    "email": "jane@example.com",
    "password": "securePass123"
}

response = requests.post(url, json=payload, headers=headers)
```

**Important things to know:**
- No authentication token is needed for registration (it's a public endpoint)
- The `Content-Type` header must be `application/json`
- Email will be automatically converted to lowercase by the server

## Step 2: Handle the Response

Check the status code to determine what happened:

```python
if response.status_code == 201:
    # Success! User was created
    data = response.json()
    user_id = data['user']['id']
    print(f"Welcome, {data['user']['username']}! Your ID is {user_id}")

elif response.status_code == 400:
    # Something wrong with the input
    error = response.json()
    print(f"Registration failed: {error['message']}")

elif response.status_code == 409:
    # Username or email already taken
    error = response.json()
    print(f"Already exists: {error['message']}")

elif response.status_code == 500:
    # Server had an internal error
    print("Server error — please try again later")
```

## Step 3: Understand the Error Codes

| Status Code | Meaning | What To Do |
|-------------|---------|------------|
| 201 | User created successfully | Redirect user to login or confirmation page |
| 400 | Bad input (missing field, bad email, short password) | Show the error message to the user so they can fix their input |
| 409 | Username or email already in use | Suggest the user try a different username or use "forgot password" |
| 500 | Server error | Show a generic "try again later" message. Don't expose technical details to the end user. |

## Step 4: Common Mistakes to Avoid

### Mistake 1: Sending form data instead of JSON
```python
# ❌ WRONG — sends form-encoded data
response = requests.post(url, data={"username": "jane"})

# ✅ CORRECT — sends JSON
response = requests.post(url, json={"username": "jane", "email": "jane@example.com", "password": "secure123"})
```

### Mistake 2: Not checking for duplicate email/username before submitting
The API will catch duplicates and return a 409 error, but for a better user experience, consider checking availability in real-time as the user types (if such an endpoint exists).

### Mistake 3: Not handling the confirmation email
After successful registration, a confirmation email is sent automatically. Your frontend should tell the user to check their inbox. Note that even if the email fails to send, the account is still created — the user can request a new confirmation email later.

## Complete Working Example

```python
import requests

def register_user(username, email, password):
    """Register a new user and return the result."""
    url = "https://api.example.com/api/users/register"

    payload = {
        "username": username,
        "email": email,
        "password": password
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()

        if response.status_code == 201:
            print(f"Success! Welcome, {data['user']['username']}")
            print(f"Check {data['user']['email']} for confirmation email")
            return data['user']

        elif response.status_code == 400:
            print(f"Invalid input: {data['message']}")
            return None

        elif response.status_code == 409:
            print(f"Already exists: {data['message']}")
            return None

        else:
            print(f"Unexpected error ({response.status_code}): {data.get('message', 'Unknown error')}")
            return None

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server")
        return None

# Usage
user = register_user("alex_smith", "alex@example.com", "myStr0ngP@ss")
```

---

## Reflection

### Which parts of the API were most challenging to document?

The **error responses** were the most challenging because there are six different error scenarios (three types of 400 errors, two types of 409 errors, and one 500 error), each with different messages. Organizing these clearly without being repetitive required careful thought about structure. Using a table for the status code summary combined with detailed JSON examples for each error provided the best balance of overview and detail.

### How did I adjust prompts to get better results?

Including the **actual code** in the prompt was essential — it allowed the AI to identify specific error messages, status codes, and validation rules directly from the implementation rather than guessing. Adding context about the validation order (required fields are checked before uniqueness, which is checked before format) helped produce documentation that matches the actual code behavior.

### Which documentation format was most effective?

The **Markdown format** (Prompt 1) was the most useful for day-to-day developer reference because it's readable both as raw text and rendered on GitHub. The OpenAPI/Swagger format (Prompt 2) is more useful for automated tooling (like generating client libraries or interactive API explorers), but is harder to read directly. The developer guide (Prompt 3) was most useful for onboarding new developers who need working code examples.

### How would I incorporate this into my development workflow?

I would generate documentation immediately when creating a new endpoint (not after), using the endpoint code as input to an AI prompt. This ensures documentation stays synchronized with the code. For existing undocumented endpoints, I would use these prompts to backfill documentation during code review or sprint cleanup time.
