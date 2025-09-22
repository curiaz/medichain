import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';

// Mock the dashboard components at module level
jest.mock('../pages/PatientDashboard', () => {
  return function PatientDashboard() {
    return <div>Patient Dashboard Component</div>;
  };
});

jest.mock('../pages/DoctorDashboard', () => {
  return function DoctorDashboard() {
    return <div>Doctor Dashboard Component</div>;
  };
});

jest.mock('../pages/AdminDashboard', () => {
  return function AdminDashboard() {
    return <div>Admin Dashboard Component</div>;
  };
});

// Default mock context
let mockAuthContext = {
  user: {
    profile: {
      role: 'patient',
      first_name: 'John',
      last_name: 'Doe'
    }
  },
  isAuthenticated: true,
  loading: false
};

// Mock the AuthContext at module level
jest.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuthContext,
  AuthProvider: ({ children }) => <div>{children}</div>
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Reset to default mock context
    mockAuthContext = {
      user: {
        profile: {
          role: 'patient',
          first_name: 'John',
          last_name: 'Doe'
        }
      },
      isAuthenticated: true,
      loading: false
    };
  });

  test('renders patient dashboard for patient role', async () => {
    renderWithRouter(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Patient Dashboard Component')).toBeInTheDocument();
    });
  });

  test('renders doctor dashboard for doctor role', async () => {
    // Update mock context for this test
    mockAuthContext = {
      user: {
        profile: {
          role: 'doctor',
          first_name: 'Dr. Smith'
        }
      },
      isAuthenticated: true,
      loading: false
    };

    renderWithRouter(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Doctor Dashboard Component')).toBeInTheDocument();
    });
  });

  test('shows loading spinner when loading', () => {
    mockAuthContext = {
      user: {
        profile: {
          role: 'patient',
          first_name: 'John',
          last_name: 'Doe'
        }
      },
      isAuthenticated: true,
      loading: true
    };

    renderWithRouter(<Dashboard />);

    expect(screen.getByText('Loading dashboard...')).toBeInTheDocument();
  });

  test('shows access denied when not authenticated', () => {
    mockAuthContext = {
      user: null,
      isAuthenticated: false,
      loading: false
    };

    renderWithRouter(<Dashboard />);

    expect(screen.getByText('Access Denied')).toBeInTheDocument();
    expect(screen.getByText('Please log in to access the dashboard.')).toBeInTheDocument();
  });

  test('shows unknown user role for invalid role', async () => {
    mockAuthContext = {
      user: {
        profile: {
          role: 'invalid_role'
        }
      },
      isAuthenticated: true,
      loading: false
    };

    renderWithRouter(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Unknown User Role')).toBeInTheDocument();
    });
  });
});
