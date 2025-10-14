/**
 * Comprehensive Tests for SettingsPage Component
 * Tests UI rendering, user interactions, API integration, and error handling
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import SettingsPage from '../pages/SettingsPage';
import settingsService from '../services/settingsService';

// Mock dependencies
jest.mock('../context/AuthContext', () => ({
  useAuth: jest.fn(() => ({
    user: { uid: 'test-user-123', email: 'test@example.com' },
    logout: jest.fn()
  }))
}));

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: jest.fn()
}));

jest.mock('../pages/Header', () => {
  return function MockHeader() {
    return <div data-testid="mock-header">Header</div>;
  };
});

jest.mock('../services/settingsService');

jest.mock('lucide-react', () => ({
  Bell: () => <span>Bell Icon</span>,
  Lock: () => <span>Lock Icon</span>,
  Shield: () => <span>Shield Icon</span>,
  Trash2: () => <span>Trash Icon</span>,
  AlertCircle: () => <span>Alert Icon</span>,
  CheckCircle: () => <span>Check Icon</span>,
  Eye: () => <span>Eye Icon</span>,
  EyeOff: () => <span>EyeOff Icon</span>,
  Mail: () => <span>Mail Icon</span>,
  MessageSquare: () => <span>Message Icon</span>,
  Calendar: () => <span>Calendar Icon</span>,
  Activity: () => <span>Activity Icon</span>,
  Save: () => <span>Save Icon</span>,
  ArrowLeft: () => <span>Arrow Icon</span>,
  Power: () => <span>Power Icon</span>
}));

// Helper function to render component
const renderSettingsPage = () => {
  return render(
    <BrowserRouter>
      <SettingsPage />
    </BrowserRouter>
  );
};

describe('SettingsPage Component', () => {
  let mockNavigate;

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate = jest.fn();
    require('react-router-dom').useNavigate.mockReturnValue(mockNavigate);
    
    // Default mock implementation
    settingsService.getNotificationPreferences.mockResolvedValue({
      success: true,
      data: {
        preferences: {
          email_notifications: true,
          sms_notifications: false,
          appointment_reminders: true,
          diagnosis_alerts: true
        }
      }
    });
  });

  // =============================================================================
  // RENDERING TESTS
  // =============================================================================

  describe('Component Rendering', () => {
    test('renders loading state initially', () => {
      settingsService.getNotificationPreferences.mockImplementation(
        () => new Promise(() => {}) // Never resolves to keep loading state
      );

      renderSettingsPage();
      
      expect(screen.getByText(/loading settings/i)).toBeInTheDocument();
      expect(screen.getByTestId('mock-header')).toBeInTheDocument();
    });

    test('renders settings page after loading', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Settings')).toBeInTheDocument();
      });

      expect(screen.getByText(/manage your account preferences/i)).toBeInTheDocument();
    });

    test('renders all main sections', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Settings')).toBeInTheDocument();
      });

      expect(screen.getByText('Notification Preferences')).toBeInTheDocument();
      expect(screen.getByText('Security & Password')).toBeInTheDocument();
      expect(screen.getByText('Danger Zone')).toBeInTheDocument();
    });

    test('renders back button', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Back')).toBeInTheDocument();
      });
    });

    test('renders Header component', () => {
      renderSettingsPage();
      
      expect(screen.getByTestId('mock-header')).toBeInTheDocument();
    });
  });

  // =============================================================================
  // NOTIFICATION PREFERENCES TESTS
  // =============================================================================

  describe('Notification Preferences', () => {
    test('loads notification preferences on mount', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(settingsService.getNotificationPreferences).toHaveBeenCalledTimes(1);
      });
    });

    test('displays notification toggles', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Email Notifications')).toBeInTheDocument();
      });

      expect(screen.getByText('SMS Notifications')).toBeInTheDocument();
      expect(screen.getByText('Appointment Reminders')).toBeInTheDocument();
      expect(screen.getByText('Diagnosis Alerts')).toBeInTheDocument();
    });

    test('toggles notification switches', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Email Notifications')).toBeInTheDocument();
      });

      // Find email notification checkbox
      const emailSection = screen.getByText('Email Notifications').closest('.notification-item');
      const emailCheckbox = within(emailSection).getByRole('checkbox');

      // Initial state should be checked
      expect(emailCheckbox).toBeChecked();

      // Toggle it
      fireEvent.click(emailCheckbox);
      expect(emailCheckbox).not.toBeChecked();

      // Toggle it back
      fireEvent.click(emailCheckbox);
      expect(emailCheckbox).toBeChecked();
    });

    test('saves notification preferences successfully', async () => {
      settingsService.updateNotificationPreferences.mockResolvedValue({
        success: true,
        data: { message: 'Preferences updated' }
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Save Preferences')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save Preferences');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(settingsService.updateNotificationPreferences).toHaveBeenCalledWith({
          email_notifications: true,
          sms_notifications: false,
          appointment_reminders: true,
          diagnosis_alerts: true
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/notification preferences saved successfully/i)).toBeInTheDocument();
      });
    });

    test('handles save notification preferences error', async () => {
      settingsService.updateNotificationPreferences.mockResolvedValue({
        success: false,
        error: 'Failed to save preferences'
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Save Preferences')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save Preferences');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to save notification preferences/i)).toBeInTheDocument();
      });
    });

    test('shows loading state while saving', async () => {
      settingsService.updateNotificationPreferences.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Save Preferences')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save Preferences');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText('Saving...')).toBeInTheDocument();
      });
    });
  });

  // =============================================================================
  // PASSWORD CHANGE TESTS
  // =============================================================================

  describe('Password Change', () => {
    test('renders password change form', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Security & Password')).toBeInTheDocument();
      });

      expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/enter new password/i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/confirm new password/i)).toBeInTheDocument();
    });

    test('allows typing in password fields', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      const currentPasswordInput = screen.getByPlaceholderText(/enter current password/i);
      const newPasswordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm new password/i);

      fireEvent.change(currentPasswordInput, { target: { value: 'OldPassword123!' } });
      fireEvent.change(newPasswordInput, { target: { value: 'NewPassword456!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'NewPassword456!' } });

      expect(currentPasswordInput.value).toBe('OldPassword123!');
      expect(newPasswordInput.value).toBe('NewPassword456!');
      expect(confirmPasswordInput.value).toBe('NewPassword456!');
    });

    test('toggles password visibility', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      const currentPasswordInput = screen.getByPlaceholderText(/enter current password/i);
      
      // Initially should be password type
      expect(currentPasswordInput.type).toBe('password');

      // Find and click the visibility toggle button for current password
      const passwordSection = currentPasswordInput.closest('.form-group');
      const toggleButtons = within(passwordSection).getAllByRole('button');
      const visibilityToggle = toggleButtons[0]; // First button in the password wrapper

      fireEvent.click(visibilityToggle);

      // Should now be text type
      expect(currentPasswordInput.type).toBe('text');

      // Click again to toggle back
      fireEvent.click(visibilityToggle);
      expect(currentPasswordInput.type).toBe('password');
    });

    test('submits password change successfully', async () => {
      settingsService.changePassword.mockResolvedValue({
        success: true,
        data: { message: 'Password changed' }
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      // Fill in password form
      fireEvent.change(screen.getByPlaceholderText(/enter current password/i), {
        target: { value: 'OldPassword123!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/enter new password/i), {
        target: { value: 'NewPassword456!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/confirm new password/i), {
        target: { value: 'NewPassword456!' }
      });

      // Submit form
      const changePasswordButton = screen.getByText('Change Password');
      fireEvent.click(changePasswordButton);

      await waitFor(() => {
        expect(settingsService.changePassword).toHaveBeenCalledWith({
          current_password: 'OldPassword123!',
          new_password: 'NewPassword456!',
          confirm_password: 'NewPassword456!'
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/password changed successfully/i)).toBeInTheDocument();
      });
    });

    test('shows error when passwords do not match', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      // Fill in with mismatched passwords
      fireEvent.change(screen.getByPlaceholderText(/enter current password/i), {
        target: { value: 'OldPassword123!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/enter new password/i), {
        target: { value: 'NewPassword456!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/confirm new password/i), {
        target: { value: 'DifferentPassword789!' }
      });

      // Submit form
      const changePasswordButton = screen.getByText('Change Password');
      fireEvent.click(changePasswordButton);

      await waitFor(() => {
        expect(screen.getByText(/new passwords do not match/i)).toBeInTheDocument();
      });

      // API should not be called
      expect(settingsService.changePassword).not.toHaveBeenCalled();
    });

    test('handles password change error from API', async () => {
      settingsService.changePassword.mockResolvedValue({
        success: false,
        error: 'Current password is incorrect'
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      // Fill in password form
      fireEvent.change(screen.getByPlaceholderText(/enter current password/i), {
        target: { value: 'WrongPassword123!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/enter new password/i), {
        target: { value: 'NewPassword456!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/confirm new password/i), {
        target: { value: 'NewPassword456!' }
      });

      // Submit form
      const changePasswordButton = screen.getByText('Change Password');
      fireEvent.click(changePasswordButton);

      await waitFor(() => {
        expect(screen.getByText(/current password is incorrect/i)).toBeInTheDocument();
      });
    });

    test('clears password fields after successful change', async () => {
      settingsService.changePassword.mockResolvedValue({
        success: true,
        data: { message: 'Password changed' }
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      const currentPasswordInput = screen.getByPlaceholderText(/enter current password/i);
      const newPasswordInput = screen.getByPlaceholderText(/enter new password/i);
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm new password/i);

      // Fill in password form
      fireEvent.change(currentPasswordInput, { target: { value: 'OldPassword123!' } });
      fireEvent.change(newPasswordInput, { target: { value: 'NewPassword456!' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'NewPassword456!' } });

      // Submit form
      const changePasswordButton = screen.getByText('Change Password');
      fireEvent.click(changePasswordButton);

      await waitFor(() => {
        expect(currentPasswordInput.value).toBe('');
        expect(newPasswordInput.value).toBe('');
        expect(confirmPasswordInput.value).toBe('');
      });
    });
  });

  // =============================================================================
  // ACCOUNT DEACTIVATION TESTS
  // =============================================================================

  describe('Account Deactivation', () => {
    test('opens deactivation modal when button clicked', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Deactivate Account')).toBeInTheDocument();
      });

      const deactivateButton = screen.getByText('Deactivate Account');
      fireEvent.click(deactivateButton);

      await waitFor(() => {
        expect(screen.getByText(/your account will be temporarily disabled/i)).toBeInTheDocument();
      });
    });

    test('closes deactivation modal when cancel clicked', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Deactivate Account')).toBeInTheDocument();
      });

      // Open modal
      const deactivateButton = screen.getByText('Deactivate Account');
      fireEvent.click(deactivateButton);

      await waitFor(() => {
        expect(screen.getByText(/your account will be temporarily disabled/i)).toBeInTheDocument();
      });

      // Click cancel
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText(/your account will be temporarily disabled/i)).not.toBeInTheDocument();
      });
    });

    test('deactivates account successfully', async () => {
      const mockLogout = jest.fn();
      require('../context/AuthContext').useAuth.mockReturnValue({
        user: { uid: 'test-user-123', email: 'test@example.com' },
        logout: mockLogout
      });

      settingsService.deactivateAccount.mockResolvedValue({
        success: true,
        data: { message: 'Account deactivated' }
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Deactivate Account')).toBeInTheDocument();
      });

      // Open modal
      fireEvent.click(screen.getByText('Deactivate Account'));

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter your password to confirm/i)).toBeInTheDocument();
      });

      // Enter password
      const passwordInput = screen.getByPlaceholderText(/enter your password to confirm/i);
      fireEvent.change(passwordInput, { target: { value: 'TestPassword123!' } });

      // Confirm deactivation
      const confirmButton = screen.getByText('Deactivate');
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(settingsService.deactivateAccount).toHaveBeenCalledWith('TestPassword123!');
      });

      await waitFor(() => {
        expect(screen.getByText(/account deactivated successfully/i)).toBeInTheDocument();
      });
    });

    test('shows error when deactivation password is empty', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Deactivate Account')).toBeInTheDocument();
      });

      // Open modal
      fireEvent.click(screen.getByText('Deactivate Account'));

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter your password to confirm/i)).toBeInTheDocument();
      });

      // Don't enter password, just confirm
      const confirmButton = screen.getByText('Deactivate');
      fireEvent.click(confirmButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter your password to confirm/i)).toBeInTheDocument();
      });

      // API should not be called
      expect(settingsService.deactivateAccount).not.toHaveBeenCalled();
    });
  });

  // =============================================================================
  // ACCOUNT DELETION TESTS
  // =============================================================================

  describe('Account Deletion', () => {
    test('opens deletion modal when button clicked', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Delete Account')).toBeInTheDocument();
      });

      const deleteButton = screen.getByText('Delete Account');
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/this action is permanent and cannot be undone/i)).toBeInTheDocument();
      });
    });

    test('closes deletion modal when cancel clicked', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Delete Account')).toBeInTheDocument();
      });

      // Open modal
      const deleteButton = screen.getByText('Delete Account');
      fireEvent.click(deleteButton);

      await waitFor(() => {
        expect(screen.getByText(/this action is permanent and cannot be undone/i)).toBeInTheDocument();
      });

      // Click cancel (need to find the second Cancel button)
      const cancelButtons = screen.getAllByText('Cancel');
      fireEvent.click(cancelButtons[cancelButtons.length - 1]);

      await waitFor(() => {
        expect(screen.queryByText(/this action is permanent and cannot be undone/i)).not.toBeInTheDocument();
      });
    });

    test('deletes account successfully', async () => {
      const mockLogout = jest.fn();
      require('../context/AuthContext').useAuth.mockReturnValue({
        user: { uid: 'test-user-123', email: 'test@example.com' },
        logout: mockLogout
      });

      settingsService.deleteAccount.mockResolvedValue({
        success: true,
        data: { message: 'Account deletion scheduled' }
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Delete Account')).toBeInTheDocument();
      });

      // Open modal
      fireEvent.click(screen.getByText('Delete Account'));

      await waitFor(() => {
        const inputs = screen.getAllByPlaceholderText(/enter your password to confirm/i);
        expect(inputs.length).toBeGreaterThan(0);
      });

      // Enter password in the second modal (deletion modal)
      const passwordInputs = screen.getAllByPlaceholderText(/enter your password to confirm/i);
      const deletePasswordInput = passwordInputs[passwordInputs.length - 1];
      fireEvent.change(deletePasswordInput, { target: { value: 'TestPassword123!' } });

      // Confirm deletion
      const deleteAccountButton = screen.getByText('Delete Account', { selector: 'button' });
      fireEvent.click(deleteAccountButton);

      await waitFor(() => {
        expect(settingsService.deleteAccount).toHaveBeenCalledWith('TestPassword123!');
      });
    });
  });

  // =============================================================================
  // NAVIGATION TESTS
  // =============================================================================

  describe('Navigation', () => {
    test('navigates back when back button is clicked', async () => {
      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Back')).toBeInTheDocument();
      });

      const backButton = screen.getByText('Back');
      fireEvent.click(backButton);

      expect(mockNavigate).toHaveBeenCalledWith(-1);
    });
  });

  // =============================================================================
  // ERROR HANDLING TESTS
  // =============================================================================

  describe('Error Handling', () => {
    test('shows error when loading preferences fails', async () => {
      settingsService.getNotificationPreferences.mockResolvedValue({
        success: false,
        error: 'Failed to load preferences'
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText(/failed to load notification preferences/i)).toBeInTheDocument();
      });
    });

    test('handles API exception when loading preferences', async () => {
      settingsService.getNotificationPreferences.mockRejectedValue(
        new Error('Network error')
      );

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText(/failed to load notification preferences/i)).toBeInTheDocument();
      });
    });

    test('handles API exception when saving preferences', async () => {
      settingsService.updateNotificationPreferences.mockRejectedValue(
        new Error('Network error')
      );

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Save Preferences')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save Preferences');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to save notification preferences/i)).toBeInTheDocument();
      });
    });
  });

  // =============================================================================
  // UI STATE TESTS
  // =============================================================================

  describe('UI State Management', () => {
    test('success message disappears after 3 seconds', async () => {
      jest.useFakeTimers();

      settingsService.updateNotificationPreferences.mockResolvedValue({
        success: true,
        data: { message: 'Preferences updated' }
      });

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Save Preferences')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save Preferences');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/notification preferences saved successfully/i)).toBeInTheDocument();
      });

      // Fast-forward time
      jest.advanceTimersByTime(3000);

      await waitFor(() => {
        expect(screen.queryByText(/notification preferences saved successfully/i)).not.toBeInTheDocument();
      });

      jest.useRealTimers();
    });

    test('disables save button while saving', async () => {
      settingsService.updateNotificationPreferences.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByText('Save Preferences')).toBeInTheDocument();
      });

      const saveButton = screen.getByText('Save Preferences');
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(saveButton).toBeDisabled();
      });
    });

    test('disables change password button while changing', async () => {
      settingsService.changePassword.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
      );

      renderSettingsPage();

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/enter current password/i)).toBeInTheDocument();
      });

      // Fill in password form
      fireEvent.change(screen.getByPlaceholderText(/enter current password/i), {
        target: { value: 'OldPassword123!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/enter new password/i), {
        target: { value: 'NewPassword456!' }
      });
      fireEvent.change(screen.getByPlaceholderText(/confirm new password/i), {
        target: { value: 'NewPassword456!' }
      });

      const changePasswordButton = screen.getByText('Change Password');
      fireEvent.click(changePasswordButton);

      await waitFor(() => {
        expect(changePasswordButton).toBeDisabled();
      });
    });
  });
});
