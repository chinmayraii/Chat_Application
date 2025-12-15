# Testing Guide

## Quick Start

### 1. Install Dependencies

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

### 2. Start Databases

**Option A: Using Docker (Recommended)**
```bash
docker-compose up -d postgres mongodb
```

**Option B: Local Databases**
- Start PostgreSQL on port 5432
- Start MongoDB on port 27017

### 3. Run Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_register_user
```

## Test Files Overview

### `test_auth.py` - Authentication Tests
Tests user registration and login functionality:
- ✅ Valid registration
- ✅ Duplicate mobile number prevention
- ✅ Valid login
- ✅ Invalid login
- ✅ Mobile number validation

**Example Output:**
```
test_auth.py::test_register_user PASSED
test_auth.py::test_login_user PASSED
test_auth.py::test_register_duplicate_mobile PASSED
```

### `test_users.py` - User Management Tests
Tests user-related endpoints:
- ✅ Get current user info
- ✅ Unauthorized access prevention
- ✅ List all users

**Example Output:**
```
test_users.py::test_get_current_user PASSED
test_users.py::test_list_users PASSED
```

### `test_messages.py` - Message Tests
Tests message storage and retrieval:
- ✅ Empty chat history
- ✅ Chat history with messages
- ✅ Unauthorized access
- ✅ Auto-mark messages as read

**Example Output:**
```
test_messages.py::test_get_chat_history_empty PASSED
test_messages.py::test_get_chat_history_with_messages PASSED
```

### `test_subjective.py` - Subjective Tests
Tests that verify "feeling" and subjective expectations:
- ✅ System responsiveness
- ✅ Identity stability consistency

**Example Output:**
```
test_subjective.py::test_system_feels_responsive PASSED
test_subjective.py::test_identity_stability_feels_consistent PASSED
```

## Understanding Test Results

### Successful Test
```
tests/test_auth.py::test_register_user PASSED    [ 14%]
```

### Failed Test
```
tests/test_auth.py::test_register_user FAILED    [ 14%]

def test_register_user():
    response = client.post(...)
>   assert response.status_code == 200
E   Assert 400 == 200
```

### Skipped Test
```
tests/test_auth.py::test_register_user SKIPPED    [ 14%]
```

## Common Issues

### Issue: Database Connection Error
**Error:** `psycopg2.OperationalError: could not connect to server`

**Solution:**
- Make sure PostgreSQL is running
- Check database credentials in `.env` file
- For tests, you can use a test database

### Issue: MongoDB Connection Error
**Error:** `pymongo.errors.ServerSelectionTimeoutError`

**Solution:**
- Make sure MongoDB is running
- Check MongoDB URI in `.env` file

### Issue: Import Errors
**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
- Make sure you're running tests from the project root directory
- Install dependencies: `pip install -r requirements.txt`

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      mongodb:
        image: mongo:7
        options: >-
          --health-cmd "mongosh --eval 'db.adminCommand(\"ping\")'"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```

## Test Coverage

To see test coverage:

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

## Best Practices

1. **Run tests before committing code**
2. **Write tests for new features**
3. **Keep tests independent** (each test should work in isolation)
4. **Use descriptive test names** (e.g., `test_register_user_with_valid_mobile`)
5. **Test both success and failure cases**

## Next Steps

- Add more test cases as you develop new features
- Integrate tests into your CI/CD pipeline
- Monitor test coverage to ensure all code paths are tested

