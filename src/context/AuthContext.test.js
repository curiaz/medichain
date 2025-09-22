import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';

// Mock Firebase functions
jest.mock('firebase/auth', () => ({
  signInWithEmailAndPassword: jest.fn(),
  createUserWithEmailAndPassword: jest.fn(),
  signOut: jest.fn(),
  onAuthStateChanged: jest.fn()
}));

// Mock Firebase config
jest.mock('../config/firebase', () => ({
  auth: {}
}));

// Mock Axios
jest.mock('axios', () => ({
  __esModule: true,
  default: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn()
  }
}));
const mockAxios = require('axios').default;

const TestComponent = () => {
  const { user, isAuthenticated, loading, login, logout } = useAuth();

  return (
    <div>
      <div data-testid="auth-status">
        {loading ? 'Loading' : isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
      </div>
      <div data-testid="user-info">
        {user ? `User: ${user.email || 'No email'}` : 'No user'}
      </div>
      <button onClick={() => login('test@example.com', 'password')}>
        Login
      </button>
      <button onClick={logout}>
        Logout
      </button>
    </div>
  );
};

const renderWithAuthProvider = (component) => {
  return render(
    <AuthProvider>
      {component}
    </AuthProvider>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Setup Firebase mocks
    const { onAuthStateChanged } = require('firebase/auth');
    onAuthStateChanged.mockImplementation((auth, callback) => {
      // Simulate no user initially
      callback(null);
      // Return unsubscribe function
      return jest.fn();
    });
  });

  test('provides authentication context to children', () => {
    renderWithAuthProvider(<TestComponent />);

    expect(screen.getByTestId('auth-status')).toBeInTheDocument();
    expect(screen.getByTestId('user-info')).toBeInTheDocument();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  test('shows loading state initially', async () => {
    // For this test, we want to check the initial loading state before Firebase callback
    const { onAuthStateChanged } = require('firebase/auth');

    // Mock to not call callback immediately
    onAuthStateChanged.mockImplementationOnce((auth, callback) => {
      // Don't call callback immediately to keep loading state
      return jest.fn();
    });

    renderWithAuthProvider(<TestComponent />);

    // Should show loading initially
    expect(screen.getByText('Loading')).toBeInTheDocument();
  });

  test('handles successful login', async () => {
    const mockUser = {
      email: 'test@example.com',
      profile: { role: 'patient' }
    };

    // Mock successful Firebase sign in
    const { signInWithEmailAndPassword } = require('firebase/auth');
    signInWithEmailAndPassword.mockResolvedValue({
      user: { getIdToken: () => Promise.resolve('mock-token') }
    });

    // Mock successful backend response
    mockAxios.post.mockResolvedValue({
      data: {
        success: true,
        user: mockUser
      }
    });

    renderWithAuthProvider(<TestComponent />);

    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(signInWithEmailAndPassword).toHaveBeenCalledWith(
        expect.any(Object),
        'test@example.com',
        'password'
      );
    });
  });

  test('handles login failure', async () => {
    // Mock failed Firebase sign in
    const { signInWithEmailAndPassword } = require('firebase/auth');
    signInWithEmailAndPassword.mockRejectedValue(
      new Error('Invalid credentials')
    );

    renderWithAuthProvider(<TestComponent />);

    const loginButton = screen.getByText('Login');
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(signInWithEmailAndPassword).toHaveBeenCalled();
    });
  });

  test('handles logout', async () => {
    // Mock successful logout
    const { signOut } = require('firebase/auth');
    signOut.mockResolvedValue();

    renderWithAuthProvider(<TestComponent />);

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    await waitFor(() => {
      expect(signOut).toHaveBeenCalled();
    });
  });

  test('throws error when useAuth is used outside provider', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => render(<TestComponent />)).toThrow(
      'useAuth must be used within an AuthProvider'
    );

    consoleSpy.mockRestore();
  });
});
