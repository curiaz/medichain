import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, useNavigate } from 'react-router-dom';
import '@testing-library/jest-dom';
import PatientAppointments from '../pages/PatientAppointments';
import { AuthProvider } from '../context/AuthContext';
import axios from 'axios';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

jest.mock('axios');

jest.mock('../pages/Header', () => {
  return function MockHeader() {
    return <div data-testid="mock-header">Header</div>;
  };
});

const mockUseAuth = jest.fn(() => ({
  user: { role: 'patient', email: 'patient@test.com' },
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

describe('PatientAppointments - Video Call Integration', () => {
  const mockNavigate = jest.fn();
  const mockAxios = axios;

  const mockAppointments = [
    {
      id: '1',
      appointment_date: '2024-01-15',
      appointment_time: '14:30',
      meeting_url: 'https://meet.jit.si/medichain-doctor123-20240115-1430-abc123',
      meeting_link: 'https://meet.jit.si/medichain-doctor123-20240115-1430-abc123',
    },
    {
      id: '2',
      appointment_date: '2024-01-20',
      appointment_time: '10:00',
      meeting_url: null,
      meeting_link: null,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    useNavigate.mockReturnValue(mockNavigate);
    
    // Reset useAuth mock
    mockUseAuth.mockReturnValue({
      user: { role: 'patient', email: 'patient@test.com' },
      isAuthenticated: true,
      loading: false,
      getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
    });
    
    // Mock localStorage
    const localStorageMock = {
      getItem: jest.fn(() => 'mock-token'),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });

    // Mock axios get
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
          <PatientAppointments />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Join Video Consultation')).toBeInTheDocument();
      });
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
          <PatientAppointments />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.queryByText('Join Video Consultation')).not.toBeInTheDocument();
      });
    });

    it('prioritizes meeting_link over meeting_url', async () => {
      const appointmentWithBoth = {
        id: '3',
        appointment_date: '2024-01-25',
        appointment_time: '15:00',
        meeting_url: 'https://meet.jit.si/old-url',
        meeting_link: 'https://meet.jit.si/new-url',
      };

      mockAxios.get.mockResolvedValue({
        data: {
          success: true,
          appointments: [appointmentWithBoth],
        },
      });

      render(
        <TestWrapper>
          <PatientAppointments />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Join Video Consultation')).toBeInTheDocument();
      });

      const button = screen.getByText('Join Video Consultation');
      fireEvent.click(button);
      
      // Should extract room name from meeting_link (new-url)
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/video/new-url');
      }, { timeout: 2000 });
    });
  });

  describe('Room Name Extraction', () => {
    it('extracts room name from Jitsi URL correctly', async () => {
      render(
        <TestWrapper>
          <PatientAppointments />
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
        id: '4',
        appointment_date: '2024-01-30',
        appointment_time: '16:00',
        meeting_url: 'https://meet.jit.si/test-room#config.prejoinPageEnabled=true',
      };

      mockAxios.get.mockResolvedValue({
        data: {
          success: true,
          appointments: [appointmentWithHash],
        },
      });

      render(
        <TestWrapper>
          <PatientAppointments />
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
        id: '5',
        appointment_date: '2024-02-01',
        appointment_time: '17:00',
        meeting_url: invalidUrl,
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
          <PatientAppointments />
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
          <PatientAppointments />
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
});

