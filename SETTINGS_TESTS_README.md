# 🧪 Settings Feature Test Suite - Quick Start Guide

## Overview
Complete testing infrastructure for the MediChain Settings feature, including 88+ comprehensive tests covering frontend components, backend API routes, and integration scenarios.

## ✅ What's Tested

### Frontend (63 Tests)
- **SettingsPage Component** (36 tests)
  - Rendering & UI states
  - Notification preferences management
  - Password change functionality
  - Account deactivation/deletion
  - Navigation & error handling
  
- **settingsService API** (27 tests)
  - GET/PUT notification preferences
  - POST password change
  - POST account deactivation
  - DELETE account deletion
  - Error handling & token management

### Backend (25 Tests)
- **settings_routes.py**
  - Password validation & hashing
  - Notification preferences CRUD
  - Security features
  - Account management
  - Audit logging
  - Authentication & authorization

## 🚀 Quick Start

### Run All Tests
```powershell
# Windows (PowerShell)
.\run_settings_tests.ps1 -TestType all

# Linux/Mac (Bash)
chmod +x run_settings_tests.sh
./run_settings_tests.sh all
```

### Run Settings Tests Only
```powershell
# Windows
.\run_settings_tests.ps1 -TestType settings-only

# Linux/Mac
./run_settings_tests.sh settings-only
```

### Run with Coverage Reports
```powershell
# Windows
.\run_settings_tests.ps1 -TestType coverage -OpenCoverage

# Linux/Mac
./run_settings_tests.sh coverage true
```

### Development Watch Mode
```powershell
# Windows
.\run_settings_tests.ps1 -TestType watch

# Linux/Mac
./run_settings_tests.sh watch
```

## 📊 Test Scripts

### PowerShell Script (Windows)
**File:** `run_settings_tests.ps1`

**Options:**
- `-TestType all` - Run all tests (frontend + backend)
- `-TestType frontend` - Frontend tests only
- `-TestType backend` - Backend tests only
- `-TestType settings-only` - Settings-specific tests only
- `-TestType coverage` - Run with coverage reports
- `-TestType watch` - Watch mode for development
- `-Verbose` - Enable verbose output
- `-OpenCoverage` - Automatically open coverage reports

**Examples:**
```powershell
# Run all tests
.\run_settings_tests.ps1 -TestType all

# Run with verbose output
.\run_settings_tests.ps1 -TestType all -Verbose

# Generate coverage and open reports
.\run_settings_tests.ps1 -TestType coverage -OpenCoverage

# Watch mode for TDD
.\run_settings_tests.ps1 -TestType watch
```

### Bash Script (Linux/Mac)
**File:** `run_settings_tests.sh`

**Usage:**
```bash
./run_settings_tests.sh [test-type] [verbose] [open-coverage]
```

**Examples:**
```bash
# Run all tests
./run_settings_tests.sh all

# Run frontend only
./run_settings_tests.sh frontend

# Run with coverage and open reports
./run_settings_tests.sh coverage true

# Watch mode
./run_settings_tests.sh watch
```

## 🔧 Manual Test Commands

### Frontend Tests

#### Run All Frontend Tests
```bash
npm test
```

#### Run SettingsPage Tests
```bash
npm test -- src/tests/SettingsPage.test.js --verbose
```

#### Run settingsService Tests
```bash
npm test -- src/tests/settingsService.test.js --verbose
```

#### Run All Settings Tests
```bash
npm test -- --testPathPattern="Settings|settings"
```

#### Run with Coverage
```bash
npm test -- --coverage --collectCoverageFrom="src/pages/SettingsPage.jsx,src/services/settingsService.js"
```

#### Watch Mode
```bash
npm test -- --watch --testPathPattern="Settings|settings"
```

### Backend Tests

#### Run All Backend Tests
```bash
cd backend
pytest tests/ -v
```

#### Run Settings Tests
```bash
cd backend
pytest tests/test_settings_routes.py -v
```

#### Run with Coverage
```bash
cd backend
pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=term-missing
```

#### Run Specific Test Class
```bash
cd backend
pytest tests/test_settings_routes.py::TestNotificationPreferences -v
```

#### Run Specific Test
```bash
cd backend
pytest tests/test_settings_routes.py::TestPasswordChange::test_change_password_valid -v
```

## 📋 CI/CD Integration

### GitHub Actions Workflow
Tests automatically run on:
- Push to: `master`, `develop`, `settings_page` branches
- Pull requests to: `master`, `develop`, `settings_page` branches

### CI Jobs
1. **backend-tests** - All backend tests
2. **settings-backend-tests** - Settings-specific backend tests
3. **frontend-tests** - All frontend tests
4. **settings-frontend-tests** - Settings-specific frontend tests (dedicated job)
5. **lint-backend** - Python linting
6. **lint-frontend** - JavaScript linting
7. **security-scan** - Security vulnerability scanning
8. **build-frontend** - Production build validation

### View CI Results
Check GitHub Actions tab in repository for detailed test results and coverage reports.

## 📁 Test Files Location

### Frontend Tests
```
src/tests/
├── SettingsPage.test.js          # Component tests (36 tests)
└── settingsService.test.js       # API integration tests (27 tests)
```

### Backend Tests
```
backend/tests/
└── test_settings_routes.py       # API route tests (25 tests)
```

### Test Scripts
```
run_settings_tests.ps1            # PowerShell test runner
run_settings_tests.sh             # Bash test runner
```

### Documentation
```
SETTINGS_TEST_DOCUMENTATION.md    # Comprehensive test documentation
SETTINGS_IMPLEMENTATION_CHECKLIST.md  # Implementation checklist
```

## 🎯 Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| SettingsPage.jsx | 90%+ | ✅ Ready for testing |
| settingsService.js | 95%+ | ✅ Ready for testing |
| settings_routes.py | 85%+ | ✅ Ready for testing |

## 🔍 Coverage Reports

### Frontend Coverage
```bash
# Generate coverage
npm test -- --coverage

# View HTML report
open coverage/lcov-report/index.html  # Mac/Linux
start coverage/lcov-report/index.html # Windows
```

### Backend Coverage
```bash
# Generate coverage with HTML report
cd backend
pytest tests/test_settings_routes.py -v --cov=settings_routes --cov-report=html

# View report
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

## 🐛 Debugging Tests

### Frontend Debugging
```bash
# Run specific test with verbose output
npm test -- -t "successfully saves notification preferences" --verbose

# Run with debugger (add 'debugger;' statement in test)
node --inspect-brk node_modules/.bin/jest --runInBand src/tests/SettingsPage.test.js

# Show console.log statements
npm test -- --verbose --no-coverage
```

### Backend Debugging
```bash
# Run with extra verbosity
pytest tests/test_settings_routes.py -vv

# Show print statements
pytest tests/test_settings_routes.py -v -s

# Run with debugger
pytest tests/test_settings_routes.py --pdb

# Run only failed tests
pytest tests/test_settings_routes.py --lf
```

## ✨ Test Features

### Frontend Test Features
- ✅ Component rendering validation
- ✅ User interaction testing
- ✅ API call mocking
- ✅ Error handling verification
- ✅ Async operation testing
- ✅ State management testing
- ✅ Navigation testing
- ✅ Form validation testing

### Backend Test Features
- ✅ API endpoint testing
- ✅ Request/response validation
- ✅ Authentication testing
- ✅ Authorization testing
- ✅ Database operation mocking
- ✅ Error handling testing
- ✅ Input validation testing
- ✅ Security feature testing

## 📈 Test Metrics

### Execution Time
- **Frontend:** ~10-15 seconds
- **Backend:** ~5-8 seconds
- **Total:** ~15-25 seconds

### Test Count
- **Total Tests:** 88+
- **Frontend:** 63 tests
- **Backend:** 25 tests

## 🔄 Continuous Testing

### Watch Mode (TDD)
```bash
# Frontend watch mode
npm test -- --watch --testPathPattern="Settings|settings"

# Backend watch mode (with pytest-watch)
cd backend
ptw tests/test_settings_routes.py -v
```

### Pre-commit Testing
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
echo "Running Settings tests..."
npm test -- --testPathPattern="Settings|settings" --watchAll=false --passWithNoTests
if [ $? -ne 0 ]; then
    echo "Frontend tests failed. Commit aborted."
    exit 1
fi

cd backend
pytest tests/test_settings_routes.py -v
if [ $? -ne 0 ]; then
    echo "Backend tests failed. Commit aborted."
    exit 1
fi

echo "All tests passed!"
exit 0
```

## 📚 Additional Documentation

- **Full Test Documentation:** `SETTINGS_TEST_DOCUMENTATION.md`
- **Implementation Checklist:** `SETTINGS_IMPLEMENTATION_CHECKLIST.md`
- **CI/CD Workflow:** `.github/workflows/ci.yml`

## 🆘 Troubleshooting

### Common Issues

#### Jest Tests Not Running
```bash
# Clear Jest cache
npm test -- --clearCache

# Reinstall dependencies
rm -rf node_modules
npm install
```

#### Backend Import Errors
```bash
# Set PYTHONPATH
cd backend
export PYTHONPATH=.  # Linux/Mac
$env:PYTHONPATH="."  # Windows PowerShell
```

#### Coverage Reports Not Generated
```bash
# Ensure coverage directories exist
mkdir -p coverage backend/htmlcov

# Run with explicit coverage flags
npm test -- --coverage --collectCoverageFrom="src/**/*.{js,jsx}"
cd backend && pytest --cov=. --cov-report=html
```

## 🤝 Contributing

When adding new tests:
1. Follow existing test patterns
2. Maintain coverage above 85%
3. Update test documentation
4. Run all tests before committing
5. Verify CI/CD passes

## 📞 Support

For issues or questions:
1. Check `SETTINGS_TEST_DOCUMENTATION.md`
2. Review CI/CD logs in GitHub Actions
3. Run tests with `--verbose` flag
4. Check test output for specific errors

---

**Last Updated:** October 14, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready  

**Quick Links:**
- [Full Test Docs](SETTINGS_TEST_DOCUMENTATION.md)
- [Implementation Checklist](SETTINGS_IMPLEMENTATION_CHECKLIST.md)
- [GitHub Actions](.github/workflows/ci.yml)
