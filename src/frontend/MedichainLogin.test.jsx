import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import '@testing-library/jest-dom';
import MedichainLogin from './MedichainLogin';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/CustomToast';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
  useLocation: jest.fn(),
  useSearchParams: jest.fn(),
}));

jest.mock('../context/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('../components/CustomToast', () => ({
  showToast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

jest.mock('../components/MedichainLogo', () => {
  return function MockMedichainLogo({ size, usePng }) {
    return <div data-testid="medichain-logo" data-size={size} data-use-png={usePng} />;
  };
});

jest.mock('../components/LoadingSpinner', () => {
  return function MockLoadingSpinner({ fullScreen, text, size }) {
    return (
      <div 
        data-testid="loading-spinner" 
        data-full-screen={fullScreen}
        data-size={size}
      >
        {text}
      </div>
    );
  };
});

jest.mock('../components/RoleSelectionModal', () => {
  return function MockRoleSelectionModal({ isOpen, onClose, onRoleSelect }) {
    return isOpen ? (
      <div data-testid="role-selection-modal">
        <button onClick={() => onRoleSelect('doctor')} data-testid="select-doctor">
          Doctor
        </button>
        <button onClick={() => onRoleSelect('patient')} data-testid="select-patient">
          Patient
        </button>
        <button onClick={onClose} data-testid="close-modal">
          Close
        </button>
      </div>
    ) : null;
  };
});

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('MedichainLogin Component', () => {
  const mockNavigate = jest.fn();
  const mockLogin = jest.fn();
  const mockResendVerification = jest.fn();
  
  const defaultAuthContext = {
    login: mockLogin,
    isAuthenticated: false,
    loading: false,
    resendVerification: mockResendVerification,
  };

  const defaultLocation = {
    state: null,
  };

  const mockSearchParams = {
    get: jest.fn(() => null),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    useNavigate.mockReturnValue(mockNavigate);
    useLocation.mockReturnValue(defaultLocation);
    useSearchParams.mockReturnValue([mockSearchParams]);
    useAuth.mockReturnValue(defaultAuthContext);
    
    // Mock localStorage
    const localStorageMock = {
      getItem: jest.fn(() => null),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true,
    });
  });

  describe('Component Rendering', () => {
    it('renders login form with all essential elements', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      expect(screen.getByText('Welcome Back!')).toBeInTheDocument();
      expect(screen.getByText('Sign in to your MediChain account')).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument();
      expect(screen.getByText("Don't have an account?")).toBeInTheDocument();
    });

    it('renders MediChain logo with correct props', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const logo = screen.getByTestId('medichain-logo');
      expect(logo).toBeInTheDocument();
      expect(logo).toHaveAttribute('data-size', '50');
      expect(logo).toHaveAttribute('data-use-png', 'true');
    });

    it('shows loading spinner when authentication is loading', () => {
      useAuth.mockReturnValue({
        ...defaultAuthContext,
        loading: true,
      });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const spinner = screen.getByTestId('loading-spinner');
      expect(spinner).toBeInTheDocument();
      expect(spinner).toHaveAttribute('data-full-screen', 'true');
      expect(spinner).toHaveTextContent('Authenticating...');
    });
  });

  describe('Form Interactions', () => {
    it('updates email and password fields on user input', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      expect(emailInput.value).toBe('test@example.com');
      expect(passwordInput.value).toBe('password123');
    });

    it('toggles password visibility when eye icon is clicked', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText(/password/i);
      const toggleButton = screen.getByRole('button', { name: '' }); // Password toggle button

      expect(passwordInput.type).toBe('password');

      fireEvent.click(toggleButton);
      expect(passwordInput.type).toBe('text');

      fireEvent.click(toggleButton);
      expect(passwordInput.type).toBe('password');
    });

    it('toggles remember me checkbox', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const rememberCheckbox = screen.getByLabelText(/remember me/i);
      expect(rememberCheckbox.checked).toBe(false);

      fireEvent.click(rememberCheckbox);
      expect(rememberCheckbox.checked).toBe(true);
    });
  });

  describe('Form Submission', () => {
    it('shows error when submitting empty form', async () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /log in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Please fill in all fields');
      });
      expect(mockLogin).not.toHaveBeenCalled();
    });

    it('shows error when email is missing', async () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Please fill in all fields');
      });
    });

    it('successfully submits form with valid credentials', async () => {
      mockLogin.mockResolvedValue({ success: true });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
        expect(showToast.success).toHaveBeenCalledWith('Login successful!');
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
      });
    });

    it('handles login failure with error message', async () => {
      mockLogin.mockResolvedValue({ 
        success: false, 
        message: 'Invalid credentials' 
      });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Invalid credentials');
      });
    });

    it('handles verification required scenario', async () => {
      mockLogin.mockResolvedValue({ 
        success: false, 
        requiresVerification: true 
      });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith(
          'Please verify your email before logging in. Check your inbox for the verification link.'
        );
      });
    });
  });

  describe('Remember Me Functionality', () => {
    it('saves credentials when remember me is checked', async () => {
      mockLogin.mockResolvedValue({ success: true });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const rememberCheckbox = screen.getByLabelText(/remember me/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(rememberCheckbox);

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(localStorage.setItem).toHaveBeenCalledWith('medichain_remembered_email', 'test@example.com');
        expect(localStorage.setItem).toHaveBeenCalledWith('medichain_remembered_password', 'password123');
      });
    });

    it('removes saved credentials when remember me is not checked', async () => {
      mockLogin.mockResolvedValue({ success: true });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(localStorage.removeItem).toHaveBeenCalledWith('medichain_remembered_email');
        expect(localStorage.removeItem).toHaveBeenCalledWith('medichain_remembered_password');
      });
    });

    it('loads remembered credentials on component mount', () => {
      localStorage.getItem
        .mockReturnValueOnce('saved@example.com')
        .mockReturnValueOnce('savedpassword');

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const rememberCheckbox = screen.getByLabelText(/remember me/i);

      expect(emailInput.value).toBe('saved@example.com');
      expect(passwordInput.value).toBe('savedpassword');
      expect(rememberCheckbox.checked).toBe(true);
    });
  });

  describe('Navigation Features', () => {
    it('navigates to signup when role is selected', async () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const signUpLink = screen.getByText('Sign Up');
      fireEvent.click(signUpLink);

      expect(screen.getByTestId('role-selection-modal')).toBeInTheDocument();

      const doctorButton = screen.getByTestId('select-doctor');
      fireEvent.click(doctorButton);

      expect(mockNavigate).toHaveBeenCalledWith('/signup?role=doctor');
    });

    it('navigates to forgot password page', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const forgotPasswordLink = screen.getByText('Forgot Password?');
      fireEvent.click(forgotPasswordLink);

      expect(mockNavigate).toHaveBeenCalledWith('/reset-password');
    });

    it('navigates to home when logo is clicked', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const logoContainer = screen.getByRole('heading', { name: 'MEDICHAIN' }).closest('div');
      fireEvent.click(logoContainer);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Email Verification', () => {
    it('shows verification prompt when verification is pending', () => {
      mockSearchParams.get.mockReturnValue('pending');
      localStorage.getItem.mockReturnValue('pending@example.com');

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      expect(screen.getByText('Email verification required')).toBeInTheDocument();
      expect(screen.getByText('Resend verification email')).toBeInTheDocument();
    });

    it('resends verification email when button is clicked', async () => {
      mockResendVerification.mockResolvedValue({ success: true });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      // Simulate showing verification prompt
      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      // Trigger verification prompt by simulating verification required login
      mockLogin.mockResolvedValue({ 
        success: false, 
        requiresVerification: true 
      });

      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(screen.getByText('Resend verification email')).toBeInTheDocument();
      });

      const resendButton = screen.getByText('Resend verification email');
      
      await act(async () => {
        fireEvent.click(resendButton);
      });

      await waitFor(() => {
        expect(mockResendVerification).toHaveBeenCalledWith('test@example.com');
        expect(showToast.success).toHaveBeenCalledWith('Verification email sent! Please check your inbox.');
      });
    });
  });

  describe('Authenticated User Redirect', () => {
    it('redirects authenticated users to dashboard', () => {
      useAuth.mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        loading: false,
      });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true });
    });

    it('redirects to intended page after authentication', () => {
      useLocation.mockReturnValue({
        state: {
          from: { pathname: '/profile' }
        }
      });

      useAuth.mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: true,
        loading: false,
      });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      expect(mockNavigate).toHaveBeenCalledWith('/profile', { replace: true });
    });
  });

  describe('Error Handling', () => {
    it('handles unexpected login errors', async () => {
      mockLogin.mockRejectedValue(new Error('Network error'));

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /log in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('An unexpected error occurred. Please try again.');
      });
    });

    it('handles resend verification errors', async () => {
      mockResendVerification.mockResolvedValue({ 
        success: false, 
        error: 'Email not found' 
      });

      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      // Simulate verification prompt
      const passwordInput = screen.getByLabelText(/password/i);
      mockLogin.mockResolvedValue({ 
        success: false, 
        requiresVerification: true 
      });

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      const submitButton = screen.getByRole('button', { name: /log in/i });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        const resendButton = screen.getByText('Resend verification email');
        fireEvent.click(resendButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Email not found');
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper labels for form elements', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/remember me/i)).toBeInTheDocument();
    });

    it('has proper form submission handling', () => {
      render(
        <TestWrapper>
          <MedichainLogin />
        </TestWrapper>
      );

      const form = screen.getByRole('button', { name: /log in/i }).closest('form');
      expect(form).toBeInTheDocument();
    });
  });
});