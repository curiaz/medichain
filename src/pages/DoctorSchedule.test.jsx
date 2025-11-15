import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, useNavigate } from 'react-router-dom';
import '@testing-library/jest-dom';
import DoctorSchedule from '../pages/DoctorSchedule';
import axios from 'axios';
import { auth } from '../config/firebase';

import { AuthProvider } from '../context/AuthContext';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

jest.mock('axios');
jest.mock('../config/firebase', () => ({
  auth: {
    currentUser: {
      getIdToken: jest.fn(),
    },
  },
}));

jest.mock('../pages/Header', () => {
  return function MockHeader() {
    return <div data-testid="mock-header">Header</div>;
  };
});

const mockUseAuth = jest.fn(() => ({
  user: { role: 'doctor', email: 'doctor@test.com' },
  isAuthenticated: true,
  loading: false,
  getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
}));

jest.mock('../context/AuthContext', () => ({
  ...jest.requireActual('../context/AuthContext'),
  useAuth: () => mockUseAuth(),
  AuthProvider: ({ children }) => children,
}));

const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('DoctorSchedule - Video Call Integration', () => {
  const mockNavigate = jest.fn();
  const mockAxios = axios;
  const mockGetIdToken = auth.currentUser.getIdToken;

  const mockAppointments = [
    {
      id: '1',
      appointment_date: '2024-01-15',
      appointment_time: '14:30',
      patient_firebase_uid: 'patient-123',
      meeting_url: 'https://meet.jit.si/medichain-doctor123-20240115-1430-abc123',
      meeting_link: 'https://meet.jit.si/medichain-doctor123-20240115-1430-abc123',
      patient: {
        first_name: 'Jane',
        last_name: 'Smith',
        email: 'jane@example.com',
      },
    },
    {
      id: '2',
      appointment_date: '2024-01-20',
      appointment_time: '10:00',
      patient_firebase_uid: 'patient-456',
      meeting_url: null,
      meeting_link: null,
      patient: {
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
      },
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    useNavigate.mockReturnValue(mockNavigate);
    mockGetIdToken.mockResolvedValue('mock-token');

    // Reset useAuth mock
    mockUseAuth.mockReturnValue({
      user: { role: 'doctor', email: 'doctor@test.com' },
      isAuthenticated: true,
      loading: false,
      getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
    });

    // Mock axios get with default successful response
    mockAxios.get = jest.fn().mockResolvedValue({
      data: {
        success: true,
        appointments: mockAppointments,
      },
    });

    // Mock axios.create if used
    mockAxios.create = jest.fn(() => mockAxios);
  });

  describe('Video Call Button Rendering', () => {
    it('renders "Join Video Consultation" button when meeting URL exists', async () => {
      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      // Wait for loading to complete and appointments to render
      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      }, { timeout: 3000 });

      await waitFor(() => {
        expect(screen.getByText('Join Video Consultation')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('does not render video button when meeting URL is null', async () => {
      mockAxios.get.mockResolvedValue({
        data: {
          success: true,
          appointments: [mockAppointments[1]], // Appointment without meeting URL
        },
      });

      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.queryByText('Join Video Consultation')).not.toBeInTheDocument();
      });
    });

    it('displays patient name in appointment card', async () => {
      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      });
    });
  });

  describe('Room Name Extraction', () => {
    it('extracts room name from Jitsi URL correctly', async () => {
      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        const button = screen.getByText('Join Video Consultation');
        fireEvent.click(button);
      });

      expect(mockNavigate).toHaveBeenCalledWith(
        '/video/medichain-doctor123-20240115-1430-abc123'
      );
    });

    it('handles URLs with hash fragments', async () => {
      const appointmentWithHash = {
        id: '3',
        appointment_date: '2024-01-30',
        appointment_time: '16:00',
        patient_firebase_uid: 'patient-789',
        meeting_url: 'https://meet.jit.si/test-room#config.prejoinPageEnabled=true',
        patient: {
          first_name: 'Bob',
          last_name: 'Johnson',
        },
      };

      mockAxios.get.mockResolvedValue({
        data: {
          success: true,
          appointments: [appointmentWithHash],
        },
      });

      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        const button = screen.getByText('Join Video Consultation');
        fireEvent.click(button);
      });

      expect(mockNavigate).toHaveBeenCalledWith('/video/test-room');
    });

    it('falls back to opening external URL if room name extraction fails', async () => {
      const invalidUrl = 'https://invalid-url.com/room';
      const appointmentWithInvalidUrl = {
        id: '4',
        appointment_date: '2024-02-01',
        appointment_time: '17:00',
        patient_firebase_uid: 'patient-999',
        meeting_url: invalidUrl,
        patient: {
          first_name: 'Alice',
          last_name: 'Brown',
        },
      };

      mockAxios.get.mockResolvedValue({
        data: {
          success: true,
          appointments: [appointmentWithInvalidUrl],
        },
      });

      // Mock window.open
      const mockOpen = jest.fn();
      window.open = mockOpen;

      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        const button = screen.getByText('Join Video Consultation');
        fireEvent.click(button);
      });

      expect(mockOpen).toHaveBeenCalledWith(invalidUrl, '_blank');
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  describe('Navigation', () => {
    it('navigates to video route when button is clicked', async () => {
      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        const button = screen.getByText('Join Video Consultation');
        fireEvent.click(button);
      });

      expect(mockNavigate).toHaveBeenCalledWith(
        '/video/medichain-doctor123-20240115-1430-abc123'
      );
    });
  });

  describe('Appointment Display', () => {
    it('displays appointment date and time correctly', async () => {
      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/January 15, 2024/i)).toBeInTheDocument();
        expect(screen.getByText(/2:30/i)).toBeInTheDocument();
      });
    });

    it('displays multiple appointments', async () => {
      render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Jane Smith')).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
      });
    });
  });
});

