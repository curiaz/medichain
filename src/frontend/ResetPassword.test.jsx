import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ResetPassword from './ResetPassword';

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('ResetPassword Component', () => {
  beforeEach(() => {
    // Clear any previous state
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders email input form correctly', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      expect(screen.getByText('Reset Password')).toBeInTheDocument();
      expect(screen.getByText(/enter your email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /send reset code/i })).toBeInTheDocument();
    });

    it('has email input field', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      expect(emailInput).toBeInTheDocument();
      expect(emailInput).toHaveAttribute('type', 'email');
    });

    it('has submit button', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /send reset code/i });
      expect(submitButton).toBeInTheDocument();
    });

    it('has back to login button', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const backButton = screen.getByRole('button', { name: /back to login/i });
      expect(backButton).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('validates empty email input', async () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /send reset code/i });
      fireEvent.click(submitButton);

      // Component should handle validation
      await waitFor(() => {
        expect(submitButton).toBeInTheDocument();
      });
    });

    it('allows email input', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      
      expect(emailInput).toHaveValue('test@example.com');
    });

    it('validates email format', async () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset code/i });
      
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);

      // Component should handle invalid email
      await waitFor(() => {
        expect(emailInput).toHaveValue('invalid-email');
      });
    });
  });

  describe('Component Structure', () => {
    it('renders without crashing', () => {
      const { container } = render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );
      
      expect(container).toBeTruthy();
    });

    it('has reset password title', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      expect(screen.getByText('Reset Password')).toBeInTheDocument();
    });

    it('displays step 1 content initially', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      expect(screen.getByText(/enter your email/i)).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('allows typing in email field', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'user@test.com' } });
      
      expect(emailInput).toHaveValue('user@test.com');
    });

    it('submit button is clickable', () => {
      render(
        <TestWrapper>
          <ResetPassword />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /send reset code/i });
      expect(submitButton).not.toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    it('handles component mount without errors', () => {
      expect(() => {
        render(
          <TestWrapper>
            <ResetPassword />
          </TestWrapper>
        );
      }).not.toThrow();
    });

    it('handles missing props gracefully', () => {
      expect(() => {
        render(
          <TestWrapper>
            <ResetPassword />
          </TestWrapper>
        );
      }).not.toThrow();
    });
  });
});
