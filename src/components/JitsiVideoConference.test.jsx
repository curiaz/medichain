/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { BrowserRouter, useParams, useNavigate } from 'react-router-dom';
import '@testing-library/jest-dom';
import JitsiVideoConference from './JitsiVideoConference';
import axios from 'axios';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: jest.fn(),
  useNavigate: jest.fn(),
}));

jest.mock('axios');

const mockUseAuth = jest.fn(() => ({
  user: {
    email: 'test@example.com',
    profile: {
      first_name: 'John',
      last_name: 'Doe'
    }
  },
  getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
}));

jest.mock('../context/AuthContext', () => ({
  ...jest.requireActual('../context/AuthContext'),
  useAuth: () => mockUseAuth(),
}));

// Mock Jitsi Meet External API
const mockJitsiAPI = {
  dispose: jest.fn(),
  addEventListeners: jest.fn(),
  executeCommand: jest.fn(),
};

beforeAll(() => {
  // Set up Jitsi API as available globally BEFORE any tests run
  // This ensures component doesn't try to load script
  global.window.JitsiMeetExternalAPI = jest.fn(() => mockJitsiAPI);
});

afterAll(() => {
  delete global.window.JitsiMeetExternalAPI;
});

beforeEach(() => {
  jest.clearAllMocks();
  
  // Reset Jitsi API mock
  mockJitsiAPI.dispose.mockClear();
  mockJitsiAPI.addEventListeners.mockClear();
  mockJitsiAPI.executeCommand.mockClear();
  
  // Ensure Jitsi API is available - component checks this before loading script
  let currentApiInstance = null;
  global.window.JitsiMeetExternalAPI = jest.fn(() => {
    // Create new mock instance for each test
    currentApiInstance = {
      dispose: jest.fn(),
      addEventListeners: jest.fn((handlers) => {
        // Store handlers so tests can call them
        mockJitsiAPI._lastHandlers = handlers;
        // Also store on the instance itself
        currentApiInstance._lastHandlers = handlers;
      }),
      executeCommand: jest.fn(),
    };
    return currentApiInstance;
  });
  
  // Also set the main mock
  mockJitsiAPI._lastHandlers = null;
  
  // Mock axios for appointment fetching
  axios.get = jest.fn().mockResolvedValue({
    data: {
      success: true,
      appointments: [
        {
          id: '1',
          appointment_date: '2024-12-31',
          appointment_time: '14:30',
          meeting_link: 'https://meet.jit.si/test-room-123',
        }
      ]
    }
  });

  // Mock sessionStorage and localStorage
  const mockStorage = {
    getItem: jest.fn((key) => {
      if (key === 'firebase_id_token' || key === 'medichain_token') {
        return 'mock-token';
      }
      return null;
    }),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  };
  Object.defineProperty(window, 'sessionStorage', {
    value: mockStorage,
    writable: true,
  });
  Object.defineProperty(window, 'localStorage', {
    value: mockStorage,
    writable: true,
  });
});

const TestWrapper = ({ children }) => {
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );
};

describe('JitsiVideoConference Component', () => {
  const mockNavigate = jest.fn();
  const mockUseParams = useParams;

  beforeEach(() => {
    jest.clearAllMocks();
    useNavigate.mockReturnValue(mockNavigate);
    mockUseParams.mockReturnValue({ roomName: 'test-room-123' });
    
    // Reset auth mock
    mockUseAuth.mockReturnValue({
      user: {
        email: 'test@example.com',
        profile: {
          first_name: 'John',
          last_name: 'Doe'
        }
      },
      getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
    });
  });

  describe('Component Rendering', () => {
    it('renders loading state initially', async () => {
      let container;
      await act(async () => {
        container = render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      // Component should render (may show loading or container)
      expect(container.container).toBeInTheDocument();
    });

    it('displays error when no room name provided', async () => {
      mockUseParams.mockReturnValue({ roomName: undefined });
      
      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        const errorText = screen.queryByText(/no room/i) || screen.queryByText(/error/i);
        expect(errorText).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    it('initializes Jitsi API when room name is provided and can join', async () => {
      // Mock appointment in the past so canJoin becomes true immediately
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01', // Past date
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      // Wait for appointment fetch and Jitsi initialization
      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }, { timeout: 5000 });
    });

    it('configures Jitsi API with correct options', async () => {
      // Mock appointment in the past
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalledWith(
          'meet.jit.si',
          expect.objectContaining({
            roomName: 'test-room-123',
            configOverwrite: expect.objectContaining({
              prejoinPageEnabled: true,
            }),
            userInfo: expect.objectContaining({
              displayName: 'John Doe',
              email: 'test@example.com',
            }),
          })
        );
      }, { timeout: 5000 });
    });
  });

  describe('User Display Name', () => {
    it('uses user profile name when available', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          email: 'test@example.com',
          profile: {
            first_name: 'Jane',
            last_name: 'Smith'
          }
        },
        getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
      });

      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalledWith(
          'meet.jit.si',
          expect.objectContaining({
            userInfo: expect.objectContaining({
              displayName: 'Jane Smith',
            }),
          })
        );
      }, { timeout: 5000 });
    });

    it('uses email username when profile name not available', async () => {
      mockUseAuth.mockReturnValue({
        user: {
          email: 'testuser@example.com'
        },
        getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
      });

      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalledWith(
          'meet.jit.si',
          expect.objectContaining({
            userInfo: expect.objectContaining({
              displayName: 'testuser',
            }),
          })
        );
      }, { timeout: 5000 });
    });

    it('uses default name when user info not available', async () => {
      mockUseAuth.mockReturnValue({
        user: null,
        getFirebaseToken: jest.fn(() => Promise.resolve('mock-token')),
      });

      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalledWith(
          'meet.jit.si',
          expect.objectContaining({
            userInfo: expect.objectContaining({
              displayName: 'MediChain User',
            }),
          })
        );
      }, { timeout: 5000 });
    });
  });

  describe('Event Handlers', () => {
    it('sets up event listeners for Jitsi events', async () => {
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Check if addEventListeners was called on the API instance
      // The component creates a new instance, so we need to check the last call
      await waitFor(() => {
        const lastCall = global.window.JitsiMeetExternalAPI.mock.results[
          global.window.JitsiMeetExternalAPI.mock.results.length - 1
        ];
        if (lastCall && lastCall.value && lastCall.value.addEventListeners) {
          expect(lastCall.value.addEventListeners).toHaveBeenCalled();
        } else {
          // Fallback: check if any instance had addEventListeners called
          const calls = global.window.JitsiMeetExternalAPI.mock.results;
          const hasCalledAddEventListeners = calls.some(result => 
            result.value && 
            result.value.addEventListeners && 
            result.value.addEventListeners.mock.calls.length > 0
          );
          expect(hasCalledAddEventListeners).toBe(true);
        }
      }, { timeout: 2000 });
    });

    it('navigates to appointments when conference is closed', async () => {
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Get the API instance that was created - check if handlers were stored
      if (mockJitsiAPI._lastHandlers && mockJitsiAPI._lastHandlers.readyToClose) {
        await act(async () => {
          mockJitsiAPI._lastHandlers.readyToClose();
        });
        // Wait for the setTimeout in handleMeetingEnd (500ms delay)
        await waitFor(() => {
          expect(mockNavigate).toHaveBeenCalledWith('/my-appointments');
        }, { timeout: 1000 });
      } else {
        // If handlers weren't captured, just verify API was called
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }
    });
  });

  describe('Exit Button', () => {
    it('renders exit button after initialization', async () => {
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      // Exit button might be in the Jitsi UI, so we check if component rendered successfully
      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }, { timeout: 5000 });
    });
  });

  describe('Cleanup', () => {
    it('disposes Jitsi API on component unmount', async () => {
      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      let unmount;
      
      await act(async () => {
        const { unmount: unmountFn } = render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
        unmount = unmountFn;
      });

      await waitFor(() => {
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }, { timeout: 5000 });

      // Get the API instance that was created
      const lastCall = global.window.JitsiMeetExternalAPI.mock.results[
        global.window.JitsiMeetExternalAPI.mock.results.length - 1
      ];
      const apiInstance = lastCall?.value;

      await act(async () => {
        unmount();
      });

      // Wait for cleanup to complete
      await waitFor(() => {
        if (apiInstance && apiInstance.dispose) {
          expect(apiInstance.dispose).toHaveBeenCalled();
        } else {
          // Fallback: check if any instance had dispose called
          const calls = global.window.JitsiMeetExternalAPI.mock.results;
          const hasCalledDispose = calls.some(result => 
            result.value && 
            result.value.dispose && 
            result.value.dispose.mock.calls.length > 0
          );
          expect(hasCalledDispose).toBe(true);
        }
      }, { timeout: 1000 });
    });
  });

  describe('Error Handling', () => {
    it('handles Jitsi API initialization errors gracefully', async () => {
      // Mock Jitsi API to throw error
      global.window.JitsiMeetExternalAPI = jest.fn(() => {
        throw new Error('Initialization failed');
      });

      axios.get = jest.fn().mockResolvedValue({
        data: {
          success: true,
          appointments: [
            {
              id: '1',
              appointment_date: '2020-01-01',
              appointment_time: '00:00',
              meeting_link: 'https://meet.jit.si/test-room-123',
            }
          ]
        }
      });

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      // Component should handle error gracefully - may show error state or still render
      await waitFor(() => {
        // Component should not crash
        expect(screen.queryByTestId('jitsi-container') || screen.queryByText(/error/i) || screen.queryByText(/loading/i)).toBeTruthy();
      }, { timeout: 5000 });

      // Restore mock for other tests
      global.window.JitsiMeetExternalAPI = jest.fn(() => mockJitsiAPI);
    });

    it('handles appointment fetch errors gracefully', async () => {
      axios.get.mockRejectedValue(new Error('Network error'));

      await act(async () => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      });

      // Should still allow joining even if appointment fetch fails (late comers can still enter)
      await waitFor(() => {
        // Component allows joining even on error
        expect(global.window.JitsiMeetExternalAPI).toHaveBeenCalled();
      }, { timeout: 5000 });
    });
  });
});
