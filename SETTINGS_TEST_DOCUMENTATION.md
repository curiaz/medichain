# Settings Feature - Test Documentation

## Overview
Comprehensive test suite for the MediChain Settings feature, covering frontend components, backend API routes, and integration testing.

## Test Structure

### Frontend Tests

#### 1. **SettingsPage.test.js** (Component Tests)
**Location:** `src/tests/SettingsPage.test.js`

**Test Coverage:**
- ✅ Component Rendering (5 tests)
  - Loading state display
  - Settings page after loading
  - All main sections (Notifications, Security, Danger Zone)
  - Back button
  - Header component integration

- ✅ Notification Preferences (8 tests)
  - Load preferences on mount
  - Display notification toggles
  - Toggle notification switches
  - Save preferences successfully
  - Handle save errors
  - Loading state while saving
  - Error handling for API failures
  - Success message display

- ✅ Password Change (8 tests)
  - Render password change form
  - Type in password fields
  - Toggle password visibility (show/hide)
  - Submit password change successfully
  - Password mismatch validation
  - API error handling
  - Clear fields after successful change
  - Loading state while changing

- ✅ Account Deactivation (4 tests)
  - Open deactivation modal
  - Close modal with cancel
  - Successful account deactivation
  - Error when password is empty

- ✅ Account Deletion (4 tests)
  - Open deletion modal
  - Close modal with cancel
  - Successful account deletion request
  - Deletion with reason

- ✅ Navigation (1 test)
  - Back button navigation

- ✅ Error Handling (3 tests)
  - Failed preference loading
  - API exceptions when loading
  - API exceptions when saving

- ✅ UI State Management (3 tests)
  - Success message auto-dismiss (3 seconds)
  - Disable save button while saving
  - Disable change password button while processing

**Total Tests:** 36 comprehensive test cases

#### 2. **settingsService.test.js** (API Integration Tests)
**Location:** `src/tests/settingsService.test.js`

**Test Coverage:**
- ✅ Get Notification Preferences (4 tests)
  - Successful fetch
  - Error handling
  - Network error handling
  - Missing auth token error

- ✅ Update Notification Preferences (3 tests)
  - Successful update
  - Validation error handling
  - Empty preferences error

- ✅ Change Password (4 tests)
  - Successful password change
  - Password validation errors
  - Incorrect current password
  - Missing required fields

- ✅ Deactivate Account (3 tests)
  - Successful deactivation
  - Incorrect password error
  - Missing password error

- ✅ Delete Account (4 tests)
  - Successful deletion request
  - Deletion with reason
  - Already pending deletion error
  - Missing password error

- ✅ Common Error Handling (6 tests)
  - 401 Unauthorized
  - 403 Forbidden
  - 500 Server Error
  - Request timeout
  - Network error with no response
  - Generic error handling

- ✅ Token Management (2 tests)
  - Use token from localStorage
  - Retrieve token with correct key

- ✅ API Endpoint URLs (1 test)
  - Correct base URL for all endpoints

**Total Tests:** 27 integration test cases

### Backend Tests

#### 3. **test_settings_routes.py** (Backend API Tests)
**Location:** `backend/tests/test_settings_routes.py`

**Test Coverage:**
- ✅ Helper Functions (9 tests)
  - Password strength validation (various cases)
  - Input sanitization
  - Password hashing

- ✅ Health Check (1 test)
  - Health check endpoint

- ✅ Notification Preferences (4 tests)
  - Get defaults when none exist
  - Get existing preferences
  - Update preferences
  - Invalid field validation

- ✅ Password Change (3 tests)
  - Valid password change
  - Password mismatch
  - Weak password validation

- ✅ Account Management (2 tests)
  - Account deactivation
  - Account deletion request

- ✅ Audit Log (1 test)
  - Get audit log

- ✅ Authentication (2 tests)
  - No auth token
  - Invalid auth token

- ✅ Integration Tests (3 tests)
  - Module imports
  - Blueprint configuration
  - Endpoint registration

**Total Tests:** 25 backend test cases

## Running Tests

### Run All Tests
```bash
# Frontend tests
npm test

# Backend tests
cd backend
pytest tests/test_settings_routes.py -v
```

### Run Settings Tests Only

#### Frontend
```bash
# Component tests
npm test -- --testPathPattern=SettingsPage.test.js

# Service tests
npm test -- --testPathPattern=settingsService.test.js

# All Settings tests
npm test -- --testPathPattern="Settings|settings"

# With coverage
npm test -- --testPathPattern="Settings|settings" --coverage --collectCoverageFrom="src/pages/SettingsPage.jsx,src/services/settingsService.js"
```

#### Backend
```bash
cd backend

# All settings tests
pytest tests/test_settings_routes.py -v

# With coverage
pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=term-missing

# Specific test class
pytest tests/test_settings_routes.py::TestNotificationPreferences -v

# Specific test
pytest tests/test_settings_routes.py::TestPasswordChange::test_change_password_valid -v
```

### Run Tests in CI/CD
The CI/CD pipeline (`.github/workflows/ci.yml`) automatically runs:
1. **backend-tests** job - All backend tests including settings
2. **settings-backend-tests** job - Settings-specific backend tests
3. **frontend-tests** job - All frontend tests including settings
4. **settings-frontend-tests** job - Settings-specific frontend tests

## Test Coverage Goals

### Frontend Coverage
- **SettingsPage.jsx:** Target 90%+ coverage
- **settingsService.js:** Target 95%+ coverage

### Backend Coverage
- **settings_routes.py:** Target 85%+ coverage

## Mocking Strategy

### Frontend Mocks
- **AuthContext:** Mocked user authentication state
- **react-router-dom:** Mocked navigation
- **settingsService:** Mocked API calls
- **lucide-react:** Mocked icon components
- **Header component:** Mocked to simple div

### Backend Mocks
- **Firebase Admin SDK:** Mocked authentication
- **Supabase Client:** Mocked database operations
- **Flask app:** Test client with testing configuration

## Test Data

### Valid Test User
```javascript
{
  uid: 'test-user-123',
  email: 'test@example.com',
  email_verified: true
}
```

### Valid Notification Preferences
```javascript
{
  email_notifications: true,
  sms_notifications: false,
  appointment_reminders: true,
  diagnosis_alerts: true
}
```

### Valid Password Data
```javascript
{
  current_password: 'OldPassword123!',
  new_password: 'NewPassword456!',
  confirm_password: 'NewPassword456!'
}
```

## Continuous Integration

### GitHub Actions Workflow
The CI/CD pipeline includes:

1. **Backend Tests**
   - Python 3.11
   - All backend tests with coverage
   - Settings-specific validation

2. **Settings Backend Tests** (Dedicated Job)
   - Settings module tests
   - Settings route validation
   - Settings API endpoint tests

3. **Frontend Tests**
   - Node.js 18
   - All frontend tests with coverage
   - Settings component validation

4. **Settings Frontend Tests** (Dedicated Job)
   - SettingsPage component tests
   - settingsService integration tests
   - File existence verification
   - Test result analysis
   - Coverage upload

### Test Triggers
Tests run on:
- Push to branches: `master`, `develop`, `settings_page`
- Pull requests to: `master`, `develop`, `settings_page`

## Debugging Tests

### Frontend Test Debugging
```bash
# Run with verbose output
npm test -- --verbose

# Run specific test
npm test -- -t "successfully saves notification preferences"

# Run with coverage and open report
npm test -- --coverage && open coverage/lcov-report/index.html

# Watch mode for development
npm test -- --watch
```

### Backend Test Debugging
```bash
# Run with extra verbosity
pytest tests/test_settings_routes.py -vv

# Run with print statements
pytest tests/test_settings_routes.py -v -s

# Run with debugger
pytest tests/test_settings_routes.py --pdb

# Run failed tests only
pytest tests/test_settings_routes.py --lf
```

## Common Test Failures

### Frontend
1. **Mock not working:** Check jest.mock() paths are correct
2. **Async test timeout:** Use waitFor() for async operations
3. **Component not found:** Ensure component is rendered before querying

### Backend
1. **Import errors:** Check PYTHONPATH is set correctly
2. **Mock not applied:** Ensure mock is applied before importing module
3. **Database errors:** Verify Supabase mock is configured

## Test Metrics

### Current Status (as of implementation)
- **Total Frontend Tests:** 63 tests
- **Total Backend Tests:** 25 tests
- **Total Tests:** 88 tests
- **Frontend Coverage:** Target 90%+
- **Backend Coverage:** Target 85%+

### Test Execution Time
- **Frontend:** ~10-15 seconds
- **Backend:** ~5-8 seconds
- **Total:** ~15-25 seconds

## Best Practices

1. **Test Isolation:** Each test is independent and doesn't rely on others
2. **Mock External Dependencies:** All API calls and external services are mocked
3. **Clear Test Names:** Test names describe what is being tested and expected outcome
4. **Arrange-Act-Assert:** Tests follow AAA pattern
5. **Error Scenarios:** Both success and failure paths are tested
6. **Edge Cases:** Boundary conditions and invalid inputs are tested
7. **Async Handling:** Proper use of async/await and waitFor()
8. **Coverage Targets:** Maintain high code coverage (>85%)

## Future Enhancements

### Planned Test Additions
- [ ] E2E tests with Cypress/Playwright
- [ ] Performance tests for API endpoints
- [ ] Load testing for concurrent requests
- [ ] Security penetration testing
- [ ] Accessibility testing (WCAG compliance)
- [ ] Mobile responsiveness testing

### Test Infrastructure Improvements
- [ ] Automated test report generation
- [ ] Test failure screenshots
- [ ] Integration with SonarQube for code quality
- [ ] Automated performance regression detection
- [ ] Test data factory for easier test setup

## Contributing

When adding new features to Settings:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add new tests for new functionality
4. Update this documentation
5. Maintain coverage above targets

## Resources

- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions](https://docs.github.com/actions)

---

**Last Updated:** October 14, 2025
**Test Suite Version:** 1.0.0
**Status:** ✅ All Tests Passing
