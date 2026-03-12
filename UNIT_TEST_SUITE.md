# Unit Test Suite Documentation

## Overview

This document describes the comprehensive unit test suite created for the MediChain system. The test suite covers both frontend React components and backend API routes.

## Test Structure

### Frontend Tests

#### Component Tests
- **`src/pages/DoctorProfilePage.test.jsx`** - Comprehensive tests for the Doctor Profile Page component
  - Initial render and loading states
  - Tab navigation (Personal Info, Professional Info, Documents, Privacy, Security, Activity)
  - Form editing and validation
  - API integration (save, update, upload)
  - Error handling
  - Authentication and authorization
  - Modal interactions (deactivate account)

#### Service Tests
- **`src/services/aiService.test.js`** - Tests for AI diagnosis service
  - Diagnosis API calls
  - Response formatting
  - Error handling
  - History retrieval

- **`src/services/patientService.test.js`** - Tests for patient management service
  - Get all patients
  - Get patient by ID
  - Create patient
  - Update patient
  - Delete patient
  - Network error handling with mock data fallback

#### Utility Tests
- **`src/utils/clearUserData.test.js`** - Tests for user data clearing utilities
  - Local storage clearing
  - Session storage clearing
  - Firebase sign out
  - Error handling

### Backend Tests

#### Route Tests
- **`backend/tests/test_profile_routes.py`** - Tests for profile management API routes
  - Get doctor profile
  - Update doctor profile
  - Get/upload documents
  - Update privacy settings
  - Get activity log
  - Error handling and validation

- **`backend/tests/test_auth_routes_comprehensive.py`** - Comprehensive authentication route tests
  - User login
  - User signup
  - Password reset flow
  - OTP verification
  - Password verification
  - Token verification
  - Logout
  - Validation errors

- **`backend/tests/test_appointment_routes.py`** - Existing appointment route tests
  - Appointment creation
  - Appointment retrieval
  - Appointment updates
  - Cleanup operations

## Test Coverage

### Frontend Coverage
- ✅ Component rendering and state management
- ✅ User interactions (clicks, form inputs)
- ✅ API integration and mocking
- ✅ Error handling and edge cases
- ✅ Authentication flows
- ✅ Navigation and routing

### Backend Coverage
- ✅ API endpoint functionality
- ✅ Authentication and authorization
- ✅ Database operations (mocked)
- ✅ Input validation
- ✅ Error handling
- ✅ Token verification

## Running Tests

### Frontend Tests

```bash
# Run all frontend tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test -- DoctorProfilePage.test.jsx

# Run tests in CI mode
npm run test:ci
```

### Backend Tests

```bash
# Navigate to backend directory
cd backend

# Run all backend tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_profile_routes.py -v

# Run specific test class
python -m pytest tests/test_auth_routes_comprehensive.py::TestAuthRoutes -v
```

### Run All Tests

```bash
# Using the provided script
.\run_all_tests.ps1  # Windows PowerShell
./run_all_tests.sh   # Linux/Mac
```

## Test Configuration

### Frontend
- **Framework**: Jest + React Testing Library
- **Configuration**: `package.json` and `src/setupTests.js`
- **Mocking**: Firebase, React Router, localStorage, fetch API

### Backend
- **Framework**: pytest
- **Configuration**: `pytest.ini` and `backend/tests/conftest.py`
- **Mocking**: Supabase client, Firebase auth, Flask app

## Test Fixtures and Mocks

### Frontend Mocks
- `AuthContext` - Mocked authentication context
- `react-router-dom` - Mocked navigation
- `firebase/auth` - Mocked Firebase authentication
- `localStorage` and `sessionStorage` - Mocked storage
- `fetch` - Mocked API calls

### Backend Mocks
- `SupabaseClient` - Mocked database operations
- `firebase_auth_service` - Mocked Firebase authentication
- `Flask app` - Test Flask application
- `pytest fixtures` - Reusable test setup

## Writing New Tests

### Frontend Test Template

```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Component from './Component';

describe('Component', () => {
  beforeEach(() => {
    // Setup mocks
  });

  it('should render correctly', () => {
    render(<Component />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    render(<Component />);
    const button = screen.getByRole('button');
    fireEvent.click(button);
    await waitFor(() => {
      expect(screen.getByText('Result')).toBeInTheDocument();
    });
  });
});
```

### Backend Test Template

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

class TestComponent:
    @pytest.fixture
    def client(self):
        # Setup test client
        pass
    
    def test_endpoint_success(self, client):
        # Test successful case
        pass
    
    def test_endpoint_error(self, client):
        # Test error case
        pass
```

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Mocking**: Mock external dependencies (APIs, databases, services)
3. **Coverage**: Aim for high test coverage of critical paths
4. **Naming**: Use descriptive test names that explain what is being tested
5. **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification
6. **Error Cases**: Test both success and error scenarios
7. **Edge Cases**: Test boundary conditions and edge cases

## Continuous Integration

Tests are automatically run in CI/CD pipeline:
- Frontend tests run on every push/PR
- Backend tests run on every push/PR
- Coverage reports are generated
- Tests must pass before merging

## Troubleshooting

### Common Issues

1. **Mock not working**: Ensure mocks are set up in `beforeEach` or test setup
2. **Async issues**: Use `waitFor` for async operations in React tests
3. **Import errors**: Check that all dependencies are properly mocked
4. **Firebase errors**: Ensure Firebase is properly mocked in `setupTests.js`

### Debugging Tests

```bash
# Run tests with verbose output
npm test -- --verbose

# Run single test with debugging
npm test -- --testNamePattern="specific test name"

# Run tests with Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand
```

## Future Improvements

- [ ] Add integration tests for end-to-end flows
- [ ] Add visual regression tests
- [ ] Increase test coverage to >80%
- [ ] Add performance tests
- [ ] Add accessibility tests
- [ ] Add API contract tests

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/react)
- [pytest Documentation](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.3.x/testing/)







