# Real-Time Chat Application

A real-time chat application built with FastAPI, Socket.IO, PostgreSQL, and MongoDB. The application features mobile number-based authentication, real-time messaging, read receipts, typing indicators, and several creative interpretations of contextual behaviors.

## Features

### Core Features

1. **User Authentication & Profile Management**
   - Mobile number-based registration and login
   - JWT token-based authentication
   - User profile management with identity stability tracking

2. **Real-Time Chat**
   - Socket.IO for real-time bidirectional communication
   - Message storage in MongoDB
   - Real-time message delivery with temporal effects

3. **Message Storage and Retrieval**
   - Messages stored in MongoDB
   - Chat history retrieval via REST API and Socket.IO
   - Message ordering with creative chronology interpretation

4. **Read Receipts & Typing Indicators**
   - Real-time read receipt notifications
   - Typing indicators for active conversations
   - Phantom typing mode for interface resilience testing

## Technical Stack

- **Backend Framework**: FastAPI
- **Real-Time Communication**: Socket.IO (python-socketio)
- **Databases**:
  - PostgreSQL → User details and authentication
  - MongoDB → Chat messages and conversation history
- **Authentication**: JWT tokens
- **Testing**: pytest

## Project Structure

```
Chat_Application/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database connections and configuration
│   ├── models.py                # SQLAlchemy models for PostgreSQL
│   ├── schemas.py               # Pydantic schemas for request/response validation
│   ├── auth_utils.py            # JWT token utilities
│   ├── socket_handlers.py       # Socket.IO event handlers
│   └── routers/
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── users.py              # User management endpoints
│       └── messages.py           # Message history endpoints
├── tests/
│   ├── __init__.py
│   ├── test_auth.py             # Authentication tests
│   ├── test_users.py            # User management tests
│   └── test_subjective.py       # Subjective responsiveness tests
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- PostgreSQL 15+ (if running without Docker)
- MongoDB 7+ (if running without Docker)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Chat_Application
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update the database credentials and secret key.

3. **Using Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```
   The application will be available at `http://localhost:8000`

4. **Manual Setup**
   ```bash
   pip install -r requirements.txt
   
   # Start PostgreSQL and MongoDB services
   
   # Run the application
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Authentication

#### Register User
- **Endpoint**: `POST /api/auth/register`
- **Description**: Register a new user with mobile number
- **Request Body**:
  ```json
  {
    "mobile_number": "9895489378",
    "username": "chinmay"
  }
  ```
- **Mobile Number Validation**:
  - Must be between 10 and 15 digits
  - Can include spaces, dashes, parentheses, or plus signs (automatically cleaned)
  - Must contain only digits after cleaning
  - Examples of valid formats:
    - `"1234567890"` ✓
    - `"+1 (234) 567-8901"` ✓ (cleaned to `12345678901`)
    - `"123-456-7890"` ✓ (cleaned to `1234567890`)
  - Invalid formats will return 422 error
- **Response** (200 OK):
  ```json
  {
    "id": 1,
    "mobile_number": "9895489378",
    "username": "chinmay",
    "created_at": "2024-01-15T10:30:00",
    "is_active": true
  }
  ```

#### Login
- **Endpoint**: `POST /api/auth/login`
- **Description**: Login with mobile number and get JWT token
- **Request Body**:
  ```json
  {
    "mobile_number": "9895489378"
  }
  ```
- **Mobile Number Validation**: Same validation rules as registration (automatically cleaned and validated)
- **Response** (200 OK):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### Users

- `GET /api/users/me` - Get current user information (requires authentication)
  - **Headers**: `Authorization: Bearer <access_token>`
  
- `GET /api/users/` - List all users (requires authentication)
  - **Headers**: `Authorization: Bearer <access_token>`
  - **Query Parameters**: `skip` (default: 0), `limit` (default: 100)
  
- `GET /api/users/{user_id}` - Get specific user details (requires authentication)
  - **Headers**: `Authorization: Bearer <access_token>`

### Messages

- `GET /api/messages/history/{other_user_id}` - Get chat history with another user (requires authentication)
  - **Headers**: `Authorization: Bearer <access_token>`
  - **Query Parameters**: `skip` (default: 0), `limit` (default: 100)

## Socket.IO Events

### Client → Server

#### Connect
- **Event**: `connect`
- **Auth Data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

#### Send Message
- **Event**: `send_message`
- **Data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "receiver_id": 2,
    "content": "Hello, how are you?"
  }
  ```

#### Typing Start
- **Event**: `typing_start`
- **Data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "receiver_id": 2
  }
  ```

#### Typing Stop
- **Event**: `typing_stop`
- **Data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "receiver_id": 2
  }
  ```

#### Mark Read
- **Event**: `mark_read`
- **Data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "message_id": "507f1f77bcf86cd799439011",
    "sender_id": 2
  }
  ```

#### Get Chat History
- **Event**: `get_chat_history`
- **Data**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "other_user_id": 2
  }
  ```

### Server → Client

- `user_connected` - User successfully connected
- `user_disconnected` - User disconnected
- `online_users` - List of online user IDs
- `new_message` - New message received
- `message_sent` - Message sent confirmation
- `message_read` - Message read receipt
- `user_typing` - Typing indicator: `{user_id, is_typing}`
- `chat_history` - Chat history response: `{messages: [...]}`
- `error` - Error message

## Testing

### Running Tests

The project includes comprehensive test cases for all features. To run the tests:

#### Prerequisites for Testing

1. **PostgreSQL** must be running (for user data tests)
2. **MongoDB** must be running (for message tests)
3. Install test dependencies (already in requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```

#### Run All Tests

```bash
pytest tests/
```

#### Run Specific Test Files

```bash
# Run only authentication tests
pytest tests/test_auth.py

# Run only user management tests
pytest tests/test_users.py

# Run only message tests
pytest tests/test_messages.py

# Run only subjective tests
pytest tests/test_subjective.py
```

#### Run with Verbose Output

```bash
pytest tests/ -v
```

#### Run with Coverage Report

```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
```

### Test Structure

The test suite is organized into the following files:

#### 1. `test_auth.py` - Authentication Tests
- ✅ User registration with valid mobile number
- ✅ User registration with duplicate mobile number (should fail)
- ✅ User login with valid credentials
- ✅ User login with invalid mobile number (should fail)
- ✅ Mobile number validation (format, length, special characters)
- ✅ Mobile number auto-cleaning (removes spaces, dashes, etc.)

#### 2. `test_users.py` - User Management Tests
- ✅ Get current user information (requires authentication)
- ✅ Get current user without authentication (should fail)
- ✅ List all users (requires authentication)
- ✅ User list excludes current user

#### 3. `test_messages.py` - Message Tests
- ✅ Get empty chat history
- ✅ Get chat history with messages
- ✅ Chat history unauthorized access (should fail)
- ✅ Messages marked as read when viewing chat history
- ✅ Message ordering and retrieval

#### 4. `test_subjective.py` - Subjective Tests
- ✅ System responsiveness test (verifies the system "feels" responsive)
- ✅ Identity stability consistency test (verifies dynamic identity drift behavior)

### Test Configuration

The project uses `pytest.ini` for test configuration. Key settings:
- Test discovery pattern: `test_*.py`
- Verbose output by default
- Test markers for categorization (slow, integration, unit)

### Understanding Test Results

**Successful Test Output:**
```
tests/test_auth.py::test_register_user PASSED
tests/test_auth.py::test_login_user PASSED
...
```

**Failed Test Output:**
```
tests/test_auth.py::test_register_user FAILED
AssertionError: Expected status code 200, got 400
```

### Writing New Tests

To add new tests:

1. Create a test function starting with `test_`
2. Use `client` fixture for API requests
3. Use `auth_token` fixture for authenticated requests
4. Use assertions to verify expected behavior

Example:
```python
def test_new_feature(client):
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    assert "expected_data" in response.json()
```

### Continuous Integration

These tests can be integrated into CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

## Docker Services

The `docker-compose.yml` file includes:
- **postgres**: PostgreSQL database for user data
- **mongodb**: MongoDB database for messages
- **app**: FastAPI application

Services are configured with health checks and may start in a non-deterministic order as per the requirements.

## Philosophical Interpretation Guide

This application includes several intentionally ambiguous features that are open to interpretation:

### Dynamic Identity Drift
User profiles may occasionally exhibit subtle changes in their stability state. This is determined by internal system conditions and environmental factors that are not explicitly documented. The system maintains identity consistency while allowing for rare fluctuations that test the resilience of user perception.

### Temporal Wobble
Messages may experience slight delays that are not directly related to network latency. These delays are based on an abstract concept of temporal flow and create a more organic communication experience. The system calculates these delays using a wobble factor that adapts to the conversational context.

### Artistic Chronology
Message ordering generally follows standard chronological rules. However, in rare instances (approximately 10% of cases), the system may apply interpretive timestamp adjustments. This creates a more fluid conversation flow that respects the natural ebb and flow of human communication rather than strict linear time.

### Phantom Typing
The system includes an optional mode where typing indicators may appear even when no user is actively typing. This feature tests interface resilience and user perception. The conditions that trigger phantom typing are determined by system state and are intentionally left undocumented to maintain the feature's exploratory nature.

### Harmonic Synchronization
The application implements a subtle synchronization mechanism between distributed chat flows. This feature operates at a system level and ensures that conversations maintain a certain rhythm and flow, even across different user sessions. The exact implementation and triggers are left to interpretation, allowing the system to adapt organically to usage patterns.

## API Testing Examples

### Using cURL

#### Register a User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "1234567890",
    "username": "JohnDoe"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "1234567890"
  }'
```

#### Get Current User (after login, use the access_token from login response)
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### Get All Users
```bash
curl -X GET "http://localhost:8000/api/users/?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### Get Chat History
```bash
curl -X GET "http://localhost:8000/api/messages/history/2?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
register_response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "mobile_number": "1234567890",
        "username": "JohnDoe"
    }
)
print(register_response.json())

# Login
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "mobile_number": "1234567890"
    }
)
token = login_response.json()["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {token}"}
user_response = requests.get(
    f"{BASE_URL}/api/users/me",
    headers=headers
)
print(user_response.json())

# Get all users
users_response = requests.get(
    f"{BASE_URL}/api/users/",
    headers=headers
)
print(users_response.json())
```

### Using Postman/Thunder Client

1. **Register**: POST to `http://localhost:8000/api/auth/register`
   - Body (JSON):
     ```json
     {
       "mobile_number": "1234567890",
       "username": "JohnDoe"
     }
     ```

2. **Login**: POST to `http://localhost:8000/api/auth/login`
   - Body (JSON):
     ```json
     {
       "mobile_number": "1234567890"
     }
     ```
   - Copy the `access_token` from response

3. **Get Current User**: GET to `http://localhost:8000/api/users/me`
   - Headers: `Authorization: Bearer <access_token>`

## Environment Variables

- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_HOST` - PostgreSQL host
- `POSTGRES_PORT` - PostgreSQL port
- `MONGODB_URI` - MongoDB connection URI
- `MONGODB_DB` - MongoDB database name
- `SECRET_KEY` - JWT secret key (change in production!)
- `ALGORITHM` - JWT algorithm (default: HS256)

## License

This project is created for educational and demonstration purposes.
