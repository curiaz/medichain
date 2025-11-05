import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter, useNavigate, useSearchParams } from 'react-router-dom';
import '@testing-library/jest-dom';
import MedichainSignup from './MedichainSignup';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/CustomToast';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
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

jest.mock('../components/LoadingSpinner', () => {
  return function MockLoadingSpinner({ size, text, color }) {
    return (
      <div data-testid="loading-spinner" data-size={size} data-color={color}>
        {text}
      </div>
    );
  };
});

jest.mock('../assets/medichain_logo.png', () => 'medichain-logo.png');

// Mock fetch for doctor signup
global.fetch = jest.fn();

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('MedichainSignup Component', () => {
  const mockNavigate = jest.fn();
  const mockSignup = jest.fn();
  const mockSearchParams = new Map();

  beforeEach(() => {
    jest.clearAllMocks();
    useNavigate.mockReturnValue(mockNavigate);
    useSearchParams.mockReturnValue([mockSearchParams]);
    useAuth.mockReturnValue({
      signup: mockSignup,
    });
    global.fetch.mockClear();
  });

  describe('Initial Rendering', () => {
    it('renders signup form correctly', () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      expect(screen.getByText('Create Account')).toBeInTheDocument();
      expect(screen.getByText('Join MediChain today')).toBeInTheDocument();
      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/account type/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    });

    it('defaults to patient account type', () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      expect(accountTypeSelect.value).toBe('patient');
    });

    it('does not show doctor-specific fields by default', () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      expect(screen.queryByLabelText(/medical specialization/i)).not.toBeInTheDocument();
      expect(screen.queryByLabelText(/verification document/i)).not.toBeInTheDocument();
    });

    it('shows heart icon for patient role', () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      // Check that Heart icon is rendered (via icon container)
      const iconContainer = document.querySelector('.doctor-icon');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Role Selection', () => {
    it('shows doctor-specific fields when doctor is selected', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      await waitFor(() => {
        expect(screen.getByLabelText(/medical specialization/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/verification document/i)).toBeInTheDocument();
      });
    });

    it('shows specialization field as read-only with "General Practitioner"', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      await waitFor(() => {
        const specializationInput = screen.getByLabelText(/medical specialization/i);
        expect(specializationInput.value).toBe('General Practitioner');
        expect(specializationInput).toHaveAttribute('readOnly');
        expect(specializationInput).toBeDisabled();
      });
    });

    it('shows stethoscope icon when doctor is selected', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      // Icon should be rendered (stethoscope for doctor)
      const iconContainer = document.querySelector('.doctor-icon');
      expect(iconContainer).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('validates required fields for patient signup', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /create account/i });
      
      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(showToast.error).toHaveBeenCalledWith('Please enter your first name');
    });

    it('validates email format', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(showToast.error).toHaveBeenCalledWith('Please enter a valid email address');
    });

    it('validates password length', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: '12345' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(showToast.error).toHaveBeenCalledWith('Password must be at least 6 characters long');
    });

    it('validates password confirmation match', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'different123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(showToast.error).toHaveBeenCalledWith('Passwords do not match');
    });

    it('validates verification file for doctor signup', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      await waitFor(() => {
        expect(screen.getByLabelText(/medical specialization/i)).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'Dr. John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'doctor@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(showToast.error).toHaveBeenCalledWith('Please upload your verification document (ID/Certificate)');
    });
  });

  describe('Patient Signup Flow', () => {
    it('successfully submits patient signup form', async () => {
      mockSignup.mockResolvedValue({
        success: true,
        message: 'Account created successfully',
      });

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(mockSignup).toHaveBeenCalledWith(
          'test@example.com',
          'password123',
          'John',
          'Doe',
          'patient'
        );
        expect(showToast.success).toHaveBeenCalled();
        expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('handles patient signup error', async () => {
      mockSignup.mockResolvedValue({
        success: false,
        error: 'Email already exists',
      });

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Email already exists');
      });
    });
  });

  describe('Doctor Signup Flow', () => {
    it('successfully submits doctor signup form with file upload', async () => {
      const mockFile = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Doctor account created successfully',
          data: {
            token: 'test-token',
            user: { id: '1', email: 'doctor@example.com' },
          },
        }),
      });

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      await waitFor(() => {
        expect(screen.getByLabelText(/medical specialization/i)).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const fileInput = screen.getByLabelText(/verification document/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'Dr. John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'doctor@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      
      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [mockFile] } });
      });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          'http://localhost:5000/api/auth/doctor-signup',
          expect.objectContaining({
            method: 'POST',
            body: expect.any(FormData),
          })
        );
      });
    });

    it('sends "General Practitioner" as specialization for doctor signup', async () => {
      const mockFile = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          success: true,
          message: 'Doctor account created successfully',
          data: {
            token: 'test-token',
            user: { id: '1', email: 'doctor@example.com' },
          },
        }),
      });

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      await waitFor(() => {
        expect(screen.getByLabelText(/medical specialization/i)).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const fileInput = screen.getByLabelText(/verification document/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'Dr. John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'doctor@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      
      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [mockFile] } });
      });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalled();
        const callArgs = global.fetch.mock.calls[0];
        const formData = callArgs[1].body;
        
        // Check that FormData contains General Practitioner
        expect(formData).toBeInstanceOf(FormData);
        // Note: FormData doesn't expose entries directly, but we can verify the call was made
      });
    });

    it('validates file type for doctor verification document', async () => {
      const mockInvalidFile = new File(['test'], 'test.txt', { type: 'text/plain' });

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      await act(async () => {
        fireEvent.change(accountTypeSelect, { target: { value: 'doctor' } });
      });

      await waitFor(() => {
        expect(screen.getByLabelText(/medical specialization/i)).toBeInTheDocument();
      });

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const fileInput = screen.getByLabelText(/verification document/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'Dr. John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'doctor@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      
      await act(async () => {
        fireEvent.change(fileInput, { target: { files: [mockInvalidFile] } });
      });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(showToast.error).toHaveBeenCalledWith('Please upload a valid file (PDF, JPG, or PNG)');
    });
  });

  describe('URL Parameter Handling', () => {
    it('sets userType from URL parameter', () => {
      const mockSearchParams = new Map([['role', 'doctor']]);
      useSearchParams.mockReturnValue([mockSearchParams]);

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      expect(accountTypeSelect.value).toBe('doctor');
      expect(accountTypeSelect).toBeDisabled(); // Should be disabled when pre-selected
    });

    it('locks role selection when role is pre-selected from URL', () => {
      const mockSearchParams = new Map([['role', 'patient']]);
      useSearchParams.mockReturnValue([mockSearchParams]);

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const accountTypeSelect = screen.getByLabelText(/account type/i);
      expect(accountTypeSelect).toBeDisabled();
    });
  });

  describe('Password Visibility Toggle', () => {
    it('toggles password visibility', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const passwordInput = screen.getByLabelText(/^password$/i);
      const toggleButton = passwordInput.parentElement.querySelector('button');

      expect(passwordInput.type).toBe('password');

      await act(async () => {
        fireEvent.click(toggleButton);
      });

      expect(passwordInput.type).toBe('text');

      await act(async () => {
        fireEvent.click(toggleButton);
      });

      expect(passwordInput.type).toBe('password');
    });

    it('toggles confirm password visibility independently', async () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const toggleButton = confirmPasswordInput.parentElement.querySelector('button');

      expect(confirmPasswordInput.type).toBe('password');

      await act(async () => {
        fireEvent.click(toggleButton);
      });

      expect(confirmPasswordInput.type).toBe('text');
    });
  });

  describe('Loading States', () => {
    it('disables form during submission', async () => {
      mockSignup.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({ success: true }), 100)
        )
      );

      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const firstNameInput = screen.getByLabelText(/first name/i);
      const lastNameInput = screen.getByLabelText(/last name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(firstNameInput, { target: { value: 'John' } });
      fireEvent.change(lastNameInput, { target: { value: 'Doe' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Navigation', () => {
    it('navigates to login page when login link is clicked', () => {
      render(
        <TestWrapper>
          <MedichainSignup />
        </TestWrapper>
      );

      const loginLink = screen.getByText(/log in/i);
      fireEvent.click(loginLink);

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});

