/**
 * Integration tests for role_info branch functionality
 * Tests the proper handling of user profile data structure
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DoctorDashboard from '../pages/DoctorDashboard';
import PatientDashboard from '../pages/PatientDashboard';

// Mock the useAuth hook with role_info structure
const mockUserWithProfile = {
  uid: 'test-doctor-123',
  email: 'doctor@test.com',
  profile: {
    first_name: 'John',
    last_name: 'Doe',
    name: 'John Doe',
    email: 'doctor@test.com',
    role: 'doctor',
    created_at: '2024-01-01T00:00:00Z'
  },
  doctor_profile: {
    license_number: 'MD-123456'
  }
};

const mockPatientWithProfile = {
  uid: 'test-patient-123',
  email: 'patient@test.com',
  profile: {
    first_name: 'Jane',
    last_name: 'Smith',
    name: 'Jane Smith',
    email: 'patient@test.com',
    role: 'patient',
    created_at: '2024-01-01T00:00:00Z'
  }
};

// Mock the AuthContext
jest.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: mockUserWithProfile,
    isAuthenticated: true,
    loading: false
  }),
  AuthProvider: ({ children }) => children
}));

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Role Info Integration Tests', () => {
  describe('Doctor Dashboard with Profile Structure', () => {
    test('displays doctor dashboard title', async () => {
      renderWithRouter(<DoctorDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('DOCTOR DASHBOARD')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('New Patient')).toBeInTheDocument();
      });
    });

    test('displays dashboard stats', async () => {
      renderWithRouter(<DoctorDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Total Patients')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getAllByText('Pending AI Reviews')[0]).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('AI Consultations')).toBeInTheDocument();
      });
    });

    test('displays action cards for doctor functionality', async () => {
      renderWithRouter(<DoctorDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('Patient Management')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Patient AI Consultations')).toBeInTheDocument();
      });
    });
  });

  describe('Patient Dashboard with Profile Structure', () => {
    beforeEach(() => {
      // Override mock for patient tests
      jest.doMock('../context/AuthContext', () => ({
        useAuth: () => ({
          user: mockPatientWithProfile,
          isAuthenticated: true,
          loading: false
        }),
        AuthProvider: ({ children }) => children
      }));
    });

    test('displays patient dashboard title', async () => {
      renderWithRouter(<PatientDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('PATIENT DASHBOARD')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getAllByText('Book Appointment')[0]).toBeInTheDocument();
      });
    });

    test('displays patient dashboard title and stats', async () => {
      renderWithRouter(<PatientDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('PATIENT DASHBOARD')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Total Consultations')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Last Checkup')).toBeInTheDocument();
      });
    });

    test('displays action cards for patient functionality', async () => {
      renderWithRouter(<PatientDashboard />);
      
      await waitFor(() => {
        expect(screen.getByText('My Health Record')).toBeInTheDocument();
      });
      
      await waitFor(() => {
        expect(screen.getByText('AI Health Assistant')).toBeInTheDocument();
      });
    });
  });

  describe('Component Rendering', () => {
    test('renders DoctorDashboard without crashing', () => {
      const { container } = renderWithRouter(<DoctorDashboard />);
      expect(container).toBeInTheDocument();
      expect(screen.getByText('DOCTOR DASHBOARD')).toBeInTheDocument();
    });

    test('renders PatientDashboard without crashing', () => {
      const { container } = renderWithRouter(<PatientDashboard />);
      expect(container).toBeInTheDocument();
      expect(screen.getByText('PATIENT DASHBOARD')).toBeInTheDocument();
    });
  });
});