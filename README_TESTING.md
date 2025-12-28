# Testing Guide for EduPace

This document provides information about the testing infrastructure and how to run tests for the EduPace project.

## Testing Infrastructure

The project uses the following testing tools:

- **pytest**: Modern testing framework for Python
- **pytest-django**: Django plugin for pytest
- **pytest-cov**: Coverage plugin for pytest
- **factory-boy**: Test data factories
- **faker**: Generate fake data for tests

## Installation

Install testing dependencies:

```bash
pip install -r requirements.txt
```

This will install all testing dependencies along with the project dependencies.

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=edupace_app --cov-report=html --cov-report=term-missing
```

This will:
- Run all tests
- Generate coverage report in terminal
- Generate HTML coverage report in `htmlcov/` directory

### Run Specific Test Files

```bash
# Run model tests only
pytest edupace_app/tests/test_models.py

# Run form tests only
pytest edupace_app/tests/test_forms.py

# Run utility tests only
pytest edupace_app/tests/test_utils.py

# Run view tests only
pytest edupace_app/tests/test_views_*.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest edupace_app/tests/test_models.py::TestCourse

# Run a specific test function
pytest edupace_app/tests/test_models.py::TestCourse::test_course_creation
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

## Test Structure

Tests are organized in the `edupace_app/tests/` directory:

```
edupace_app/tests/
├── __init__.py
├── test_models.py          # Model unit tests
├── test_forms.py           # Form unit tests
├── test_utils.py           # Utility function tests
├── test_views_auth.py      # Authentication/authorization tests
└── test_views_crud.py      # CRUD operation tests
```

## Test Categories

### Unit Tests

- **Model Tests** (`test_models.py`): Test model validation, relationships, and methods
- **Form Tests** (`test_forms.py`): Test form validation and field requirements
- **Utility Tests** (`test_utils.py`): Test utility functions like permissions, calculations, Excel processing

### Integration Tests

- **Authentication Tests** (`test_views_auth.py`): Test login, logout, role-based access
- **CRUD Tests** (`test_views_crud.py`): Test create, read, update, delete operations

## Test Factories

Test factories are defined in `edupace_app/factories.py` and use `factory-boy` to create test data:

- `UserFactory`: Create test users
- `StudentFactory`: Create test students
- `TeacherFactory`: Create test teachers
- `AcademicBoardFactory`: Create test academic board members
- `CourseFactory`: Create test courses
- `GradeFactory`: Create test grades
- And more...

## Coverage Reports

After running tests with coverage, view the HTML report:

```bash
# Generate HTML coverage report
pytest --cov=edupace_app --cov-report=html

# Open the report (on macOS/Linux)
open htmlcov/index.html

# Open the report (on Windows)
start htmlcov/index.html
```

## Writing New Tests

### Example: Adding a New Model Test

```python
def test_my_new_feature(db):
    """Test description"""
    # Arrange
    course = CourseFactory()
    
    # Act
    result = course.some_method()
    
    # Assert
    assert result == expected_value
```

### Example: Adding a New View Test

```python
def test_my_new_view(client, teacher_user, course):
    """Test description"""
    teacher_user.teacher_profile.courses.add(course)
    client.force_login(teacher_user)
    
    response = client.get(reverse('edupace_app:my_view', args=[course.id]))
    
    assert response.status_code == 200
    assert 'expected_data' in response.context
```

## Continuous Integration

The test suite is designed to be run in CI/CD pipelines. The pytest configuration in `pytest.ini` ensures:

- Tests use a separate test database
- Migrations are not run (using `--nomigrations`)
- Database is reused between test runs (`--reuse-db`)
- Coverage reports are generated

## Best Practices

1. **Use factories**: Always use factories to create test data instead of manually creating objects
2. **Test isolation**: Each test should be independent and not depend on other tests
3. **Clear test names**: Use descriptive test function names that explain what is being tested
4. **Arrange-Act-Assert**: Structure tests with clear sections for setup, execution, and verification
5. **Test edge cases**: Don't just test happy paths, test error conditions and edge cases
6. **Keep tests fast**: Avoid slow operations in tests when possible

## Troubleshooting

### Tests Fail with Database Errors

If you see database-related errors, try:

```bash
# Delete test database and recreate
pytest --create-db
```

### Import Errors

Make sure you're running tests from the project root directory and that all dependencies are installed.

### Coverage Not Showing

Make sure you're using the `--cov` flag:

```bash
pytest --cov=edupace_app
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [factory-boy Documentation](https://factoryboy.readthedocs.io/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)

