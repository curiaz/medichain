import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter, useNavigate } from 'react-router-dom';
import '@testing-library/jest-dom';
import ResetPassword from './ResetPassword';
import { showToast } from '../components/CustomToast';
import axios from 'axios';

// Mock dependencies
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn(),
}));

jest.mock('../components/CustomToast', () => ({
  showToast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

jest.mock('axios');
const mockedAxios = axios;

jest.mock('../components/MedichainLogo', () => {
  return function MockMedichainLogo({ size }) {
    return <div data-testid="medichain-logo" data-size={size} />;
  };
});

jest.mock('../components/LoadingSpinner', () => {
  return function MockLoadingSpinner({ size, text }) {
    return (
      <div data-testid="loading-spinner" data-size={size}>
        {text}
      </div>
    );
  };
});

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('ResetPassword Component - OTP Enhanced', () => {
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useNavigate.mockReturnValue(mockNavigate);
    mockedAxios.post.mockReset();
  });

  describe('Step 1: Email Input', () => {
    it('renders email input form correctly', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      expect(screen.getByText('Reset Password')).toBeInTheDocument();
      expect(screen.getByText("Enter your email address and we'll send you a verification code")).toBeInTheDocument();
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send reset code/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /back to login/i })).toBeInTheDocument();
    });

    it('shows step indicator with correct active step', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const stepIndicator = screen.getByText('Email').closest('.step');
      expect(stepIndicator).toHaveClass('active');
      
      const verifyStep = screen.getByText('Verify').closest('.step');
      expect(verifyStep).not.toHaveClass('active');
      
      const resetStep = screen.getByText('Reset').closest('.step');
      expect(resetStep).not.toHaveClass('active');
    });

    it('validates email input before submission', async () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /send reset code/i });
      
      // Test empty email
      fireEvent.click(submitButton);
      expect(showToast.error).toHaveBeenCalledWith('Please enter your email address');

      // Test invalid email format
      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);
      expect(showToast.error).toHaveBeenCalledWith('Please enter a valid email address');
    });

    it('successfully sends OTP request', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'Reset OTP has been sent to your email',
        }
      });

      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset code/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          'http://localhost:5000/api/auth/password-reset-request',
          { email: 'test@example.com' }
        );
        expect(showToast.success).toHaveBeenCalledWith('Reset OTP has been sent to your email!');
      });

      // Should move to step 2
      expect(screen.getByText('verify & continue')).toBeInTheDocument();
    });

    it('handles API errors gracefully', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          data: {
            error: 'Email not found'
          }
        }
      });

      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset code/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Email not found');
      });
    });

    it('navigates back to login when back button is clicked', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const backButton = screen.getByRole('button', { name: /back to login/i });
      fireEvent.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  describe('Step 2: OTP Verification', () => {
    beforeEach(async () => {
      // Setup component in step 2
      mockedAxios.post.mockResolvedValueOnce({
        data: { success: true, message: 'OTP sent' }
      });

      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      const submitButton = screen.getByRole('button', { name: /send reset code/i });
      await act(async () => {
        fireEvent.click(submitButton);
      });
    });

    it('renders OTP verification form correctly', () => {
      expect(screen.getByText('verify & continue')).toBeInTheDocument();
      expect(screen.getByText(/enter the 6-digit verification code sent to/i)).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /verify & continue/i })).toBeInTheDocument();
    });

    it('formats OTP input correctly', () => {
      const otpInput = screen.getByLabelText(/verification code/i);
      
      // Test numeric only input
      fireEvent.change(otpInput, { target: { value: 'abc123def' } });
      expect(otpInput.value).toBe('123');

      // Test 6-digit limit
      fireEvent.change(otpInput, { target: { value: '1234567890' } });
      expect(otpInput.value).toBe('123456');
    });

    it('validates OTP before submission', async () => {
      const verifyButton = screen.getByRole('button', { name: /verify & continue/i });
      
      // Test empty OTP
      fireEvent.click(verifyButton);
      expect(showToast.error).toHaveBeenCalledWith('Please enter the OTP code');

      // Test incomplete OTP
      const otpInput = screen.getByLabelText(/verification code/i);
      fireEvent.change(otpInput, { target: { value: '123' } });
      fireEvent.click(verifyButton);
      expect(showToast.error).toHaveBeenCalledWith('Please enter a valid 6-digit OTP code');
    });

    it('successfully verifies OTP', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'OTP verified successfully',
          reset_token: 'test-token-123'
        }
      });

      const otpInput = screen.getByLabelText(/verification code/i);
      const verifyButton = screen.getByRole('button', { name: /verify & continue/i });

      fireEvent.change(otpInput, { target: { value: '123456' } });

      await act(async () => {
        fireEvent.click(verifyButton);
      });

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          'http://localhost:5000/api/auth/verify-otp',
          { email: 'test@example.com', otp: '123456' }
        );
        expect(showToast.success).toHaveBeenCalledWith('OTP verified successfully!');
      });

      // Should move to step 3
      expect(screen.getByText('Create New Password')).toBeInTheDocument();
    });

    it('handles invalid OTP error', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          data: {
            error: 'Invalid OTP code'
          }
        }
      });

      const otpInput = screen.getByLabelText(/verification code/i);
      const verifyButton = screen.getByRole('button', { name: /verify & continue/i });

      fireEvent.change(otpInput, { target: { value: '123456' } });

      await act(async () => {
        fireEvent.click(verifyButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Invalid OTP code');
      });
    });

    it('allows reSending...async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: { success: true, message: 'New OTP sent' }
      });

      const resendButton = screen.getByRole('button', { name: /resend code/i });

      await act(async () => {
        fireEvent.click(resendButton);
      });

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          'http://localhost:5000/api/auth/password-reset-request',
          { email: 'test@example.com' }
        );
        expect(showToast.success).toHaveBeenCalledWith('New OTP has been sent to your email!');
      });
    });

    it('allows changing email', () => {
      const changeEmailButton = screen.getByRole('button', { name: /change email/i });
      fireEvent.click(changeEmailButton);

      // Should go back to step 1
      expect(screen.getByText('Reset Password')).toBeInTheDocument();
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    });
  });

  describe('Step 3: New Password', () => {
    beforeEach(async () => {
      // Setup component in step 3
      mockedAxios.post
        .mockResolvedValueOnce({ data: { success: true, message: 'OTP sent' } })
        .mockResolvedValueOnce({ 
          data: { 
            success: true, 
            message: 'OTP verified', 
            reset_token: 'test-token' 
          } 
        });

      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      // Navigate through steps
      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      const emailSubmit = screen.getByRole('button', { name: /send reset code/i });
      await act(async () => {
        fireEvent.click(emailSubmit);
      });

      const otpInput = screen.getByLabelText(/verification code/i);
      fireEvent.change(otpInput, { target: { value: '123456' } });
      
      const otpSubmit = screen.getByRole('button', { name: /verify & continue/i });
      await act(async () => {
        fireEvent.click(otpSubmit);
      });
    });

    it('renders password form correctly', () => {
      expect(screen.getByText('Create New Password')).toBeInTheDocument();
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
      expect(screen.getByText('Password must contain:')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reset password/i })).toBeInTheDocument();
    });

    it('validates password requirements', () => {
      const newPasswordInput = screen.getByLabelText(/new password/i);
      
      // Test password length requirement
      fireEvent.change(newPasswordInput, { target: { value: 'abc' } });
      const lengthRequirement = screen.getByText('At least 6 characters');
      expect(lengthRequirement).not.toHaveClass('met');

      // Test valid password
      fireEvent.change(newPasswordInput, { target: { value: 'Test123!' } });
      expect(lengthRequirement).toHaveClass('met');
      expect(screen.getByText('One uppercase letter')).toHaveClass('met');
      expect(screen.getByText('One lowercase letter')).toHaveClass('met');
      expect(screen.getByText('One number')).toHaveClass('met');
    });

    it('validates password confirmation', async () => {
      const newPasswordInput = screen.getByLabelText(/new password/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /reset password/i });

      fireEvent.change(newPasswordInput, { target: { value: 'Test123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'Test456!' } });

      fireEvent.click(submitButton);

      expect(showToast.error).toHaveBeenCalledWith('Passwords do not match');
    });

    it('successfully resets password', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'Password reset successful'
        }
      });

      const newPasswordInput = screen.getByLabelText(/new password/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /reset password/i });

      fireEvent.change(newPasswordInput, { target: { value: 'Test123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'Test123!' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          'http://localhost:5000/api/auth/password-reset',
          {
            email: 'test@example.com',
            reset_token: 'test-token',
            new_password: 'Test123!'
          }
        );
        expect(showToast.success).toHaveBeenCalledWith(
          'Password reset successful! You can now login with your new password.'
        );
      });

      // Should navigate to login after success
      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/login');
      }, { timeout: 3000 });
    });

    it('handles password reset error', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          data: {
            error: 'Reset token expired'
          }
        }
      });

      const newPasswordInput = screen.getByLabelText(/new password/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /reset password/i });

      fireEvent.change(newPasswordInput, { target: { value: 'Test123!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'Test123!' } });

      await act(async () => {
        fireEvent.click(submitButton);
      });

      await waitFor(() => {
        expect(showToast.error).toHaveBeenCalledWith('Reset token expired');
      });
    });
  });

  describe('Loading States', () => {
    it('disables form during submission', async () => {
      // Mock a delayed response
      mockedAxios.post.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({ data: { success: true } }), 100)
        )
      );

      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset code/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      act(() => {
        fireEvent.click(submitButton);
      });

      // Should show loading state
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.getByText('Sending...')).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
      expect(emailInput).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels and structure', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send reset code/i })).toBeInTheDocument();
    });

    it('maintains proper focus management', async () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      expect(emailInput).toHaveFocus();
    });
  });
});
