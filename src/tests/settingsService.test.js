/**
 * Integration Tests for settingsService
 * Tests API calls, error handling, and response processing
 */

import settingsService from '../services/settingsService';
import axios from 'axios';

// Mock axios
jest.mock('axios');

describe('settingsService', () => {
  const mockToken = 'test-firebase-token-123';

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock localStorage
    Storage.prototype.getItem = jest.fn(() => mockToken);
  });

  // =============================================================================
  // GET NOTIFICATION PREFERENCES TESTS
  // =============================================================================

  describe('getNotificationPreferences', () => {
    test('successfully fetches notification preferences', async () => {
      const mockResponse = {
        data: {
          success: true,
          preferences: {
            email_notifications: true,
            sms_notifications: false,
            appointment_reminders: true,
            diagnosis_alerts: true
          }
        }
      };

      axios.get.mockResolvedValue(mockResponse);

      const result = await settingsService.getNotificationPreferences();

      expect(axios.get).toHaveBeenCalledWith(
        'http://localhost:5000/api/settings/notifications',
        {
          headers: {
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      expect(result).toEqual({
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

    test('handles error when fetching notification preferences', async () => {
      const mockError = {
        response: {
          data: {
            error: 'Failed to fetch preferences'
          }
        }
      };

      axios.get.mockRejectedValue(mockError);

      const result = await settingsService.getNotificationPreferences();

      expect(result).toEqual({
        success: false,
        error: 'Failed to fetch preferences'
      });
    });

    test('handles network error when fetching preferences', async () => {
      axios.get.mockRejectedValue(new Error('Network error'));

      const result = await settingsService.getNotificationPreferences();

      expect(result).toEqual({
        success: false,
        error: 'Failed to fetch notification preferences'
      });
    });

    test('returns error when no auth token available', async () => {
      Storage.prototype.getItem = jest.fn(() => null);

      const result = await settingsService.getNotificationPreferences();

      expect(result).toEqual({
        success: false,
        error: 'No authentication token available'
      });

      expect(axios.get).not.toHaveBeenCalled();
    });
  });

  // =============================================================================
  // UPDATE NOTIFICATION PREFERENCES TESTS
  // =============================================================================

  describe('updateNotificationPreferences', () => {
    test('successfully updates notification preferences', async () => {
      const preferences = {
        email_notifications: false,
        sms_notifications: true,
        appointment_reminders: false,
        diagnosis_alerts: true
      };

      const mockResponse = {
        data: {
          success: true,
          message: 'Preferences updated successfully'
        }
      };

      axios.put.mockResolvedValue(mockResponse);

      const result = await settingsService.updateNotificationPreferences(preferences);

      expect(axios.put).toHaveBeenCalledWith(
        'http://localhost:5000/api/settings/notifications',
        preferences,
        {
          headers: {
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      expect(result).toEqual({
        success: true,
        data: {
          message: 'Preferences updated successfully'
        }
      });
    });

    test('handles validation error when updating preferences', async () => {
      const mockError = {
        response: {
          status: 400,
          data: {
            error: 'Invalid preference field'
          }
        }
      };

      axios.put.mockRejectedValue(mockError);

      const result = await settingsService.updateNotificationPreferences({
        invalid_field: true
      });

      expect(result).toEqual({
        success: false,
        error: 'Invalid preference field'
      });
    });

    test('returns error when preferences object is empty', async () => {
      const result = await settingsService.updateNotificationPreferences({});

      expect(result).toEqual({
        success: false,
        error: 'No preferences provided'
      });

      expect(axios.put).not.toHaveBeenCalled();
    });
  });

  // =============================================================================
  // CHANGE PASSWORD TESTS
  // =============================================================================

  describe('changePassword', () => {
    test('successfully changes password', async () => {
      const passwordData = {
        current_password: 'OldPassword123!',
        new_password: 'NewPassword456!',
        confirm_password: 'NewPassword456!'
      };

      const mockResponse = {
        data: {
          success: true,
          message: 'Password changed successfully'
        }
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await settingsService.changePassword(passwordData);

      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:5000/api/settings/security/password',
        passwordData,
        {
          headers: {
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      expect(result).toEqual({
        success: true,
        data: {
          message: 'Password changed successfully'
        }
      });
    });

    test('handles password validation error', async () => {
      const mockError = {
        response: {
          status: 400,
          data: {
            error: 'Password must be at least 8 characters long'
          }
        }
      };

      axios.post.mockRejectedValue(mockError);

      const result = await settingsService.changePassword({
        current_password: 'old',
        new_password: 'weak',
        confirm_password: 'weak'
      });

      expect(result).toEqual({
        success: false,
        error: 'Password must be at least 8 characters long'
      });
    });

    test('handles incorrect current password error', async () => {
      const mockError = {
        response: {
          status: 401,
          data: {
            error: 'Current password is incorrect'
          }
        }
      };

      axios.post.mockRejectedValue(mockError);

      const result = await settingsService.changePassword({
        current_password: 'WrongPassword123!',
        new_password: 'NewPassword456!',
        confirm_password: 'NewPassword456!'
      });

      expect(result).toEqual({
        success: false,
        error: 'Current password is incorrect'
      });
    });

    test('returns error when required fields are missing', async () => {
      const result = await settingsService.changePassword({
        current_password: 'OldPassword123!'
      });

      expect(result).toEqual({
        success: false,
        error: 'Missing required fields'
      });

      expect(axios.post).not.toHaveBeenCalled();
    });
  });

  // =============================================================================
  // DEACTIVATE ACCOUNT TESTS
  // =============================================================================

  describe('deactivateAccount', () => {
    test('successfully deactivates account', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Account deactivated successfully'
        }
      };

      axios.post.mockResolvedValue(mockResponse);

      const result = await settingsService.deactivateAccount('TestPassword123!');

      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:5000/api/settings/security/account/deactivate',
        { password: 'TestPassword123!' },
        {
          headers: {
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          }
        }
      );

      expect(result).toEqual({
        success: true,
        data: {
          message: 'Account deactivated successfully'
        }
      });
    });

    test('handles incorrect password error', async () => {
      const mockError = {
        response: {
          status: 401,
          data: {
            error: 'Password is incorrect'
          }
        }
      };

      axios.post.mockRejectedValue(mockError);

      const result = await settingsService.deactivateAccount('WrongPassword');

      expect(result).toEqual({
        success: false,
        error: 'Password is incorrect'
      });
    });

    test('returns error when password is not provided', async () => {
      const result = await settingsService.deactivateAccount('');

      expect(result).toEqual({
        success: false,
        error: 'Password is required'
      });

      expect(axios.post).not.toHaveBeenCalled();
    });
  });

  // =============================================================================
  // DELETE ACCOUNT TESTS
  // =============================================================================

  describe('deleteAccount', () => {
    test('successfully requests account deletion', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Account deletion scheduled. You will receive a confirmation email.',
          deletion_date: '2025-11-03T00:00:00Z'
        }
      };

      axios.delete.mockResolvedValue(mockResponse);

      const result = await settingsService.deleteAccount('TestPassword123!');

      expect(axios.delete).toHaveBeenCalledWith(
        'http://localhost:5000/api/settings/security/account/delete',
        {
          headers: {
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          },
          data: {
            password: 'TestPassword123!'
          }
        }
      );

      expect(result).toEqual({
        success: true,
        data: {
          message: 'Account deletion scheduled. You will receive a confirmation email.',
          deletion_date: '2025-11-03T00:00:00Z'
        }
      });
    });

    test('successfully requests account deletion with reason', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Account deletion scheduled'
        }
      };

      axios.delete.mockResolvedValue(mockResponse);

      const result = await settingsService.deleteAccount('TestPassword123!', 'No longer needed');

      expect(axios.delete).toHaveBeenCalledWith(
        'http://localhost:5000/api/settings/security/account/delete',
        {
          headers: {
            'Authorization': `Bearer ${mockToken}`,
            'Content-Type': 'application/json'
          },
          data: {
            password: 'TestPassword123!',
            reason: 'No longer needed'
          }
        }
      );

      expect(result.success).toBe(true);
    });

    test('handles already pending deletion request', async () => {
      const mockError = {
        response: {
          status: 409,
          data: {
            error: 'Account deletion already pending'
          }
        }
      };

      axios.delete.mockRejectedValue(mockError);

      const result = await settingsService.deleteAccount('TestPassword123!');

      expect(result).toEqual({
        success: false,
        error: 'Account deletion already pending'
      });
    });

    test('returns error when password is not provided', async () => {
      const result = await settingsService.deleteAccount('');

      expect(result).toEqual({
        success: false,
        error: 'Password is required'
      });

      expect(axios.delete).not.toHaveBeenCalled();
    });
  });

  // =============================================================================
  // COMMON ERROR HANDLING TESTS
  // =============================================================================

  describe('Common Error Handling', () => {
    test('handles 401 unauthorized error', async () => {
      const mockError = {
        response: {
          status: 401,
          data: {
            error: 'Unauthorized'
          }
        }
      };

      axios.get.mockRejectedValue(mockError);

      const result = await settingsService.getNotificationPreferences();

      expect(result).toEqual({
        success: false,
        error: 'Unauthorized'
      });
    });

    test('handles 403 forbidden error', async () => {
      const mockError = {
        response: {
          status: 403,
          data: {
            error: 'Access forbidden'
          }
        }
      };

      axios.get.mockRejectedValue(mockError);

      const result = await settingsService.getNotificationPreferences();

      expect(result).toEqual({
        success: false,
        error: 'Access forbidden'
      });
    });

    test('handles 500 server error', async () => {
      const mockError = {
        response: {
          status: 500,
          data: {
            error: 'Internal server error'
          }
        }
      };

      axios.get.mockRejectedValue(mockError);

      const result = await settingsService.getNotificationPreferences();

      expect(result).toEqual({
        success: false,
        error: 'Internal server error'
      });
    });

    test('handles request timeout', async () => {
      axios.get.mockRejectedValue({
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      });

      const result = await settingsService.getNotificationPreferences();

      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });

    test('handles network error with no response', async () => {
      axios.get.mockRejectedValue({
        request: {},
        message: 'Network Error'
      });

      const result = await settingsService.getNotificationPreferences();

      expect(result.success).toBe(false);
      expect(result.error).toBeTruthy();
    });
  });

  // =============================================================================
  // TOKEN MANAGEMENT TESTS
  // =============================================================================

  describe('Token Management', () => {
    test('uses token from localStorage', async () => {
      const customToken = 'custom-token-456';
      Storage.prototype.getItem = jest.fn(() => customToken);

      axios.get.mockResolvedValue({
        data: { success: true, preferences: {} }
      });

      await settingsService.getNotificationPreferences();

      expect(axios.get).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': `Bearer ${customToken}`
          })
        })
      );
    });

    test('retrieves token using correct key', async () => {
      const getItemSpy = jest.spyOn(Storage.prototype, 'getItem');

      axios.get.mockResolvedValue({
        data: { success: true, preferences: {} }
      });

      await settingsService.getNotificationPreferences();

      expect(getItemSpy).toHaveBeenCalledWith('authToken');
    });
  });

  // =============================================================================
  // API ENDPOINT TESTS
  // =============================================================================

  describe('API Endpoint URLs', () => {
    test('uses correct base URL for all endpoints', async () => {
      const baseURL = 'http://localhost:5000/api/settings';

      axios.get.mockResolvedValue({ data: { success: true } });
      axios.put.mockResolvedValue({ data: { success: true } });
      axios.post.mockResolvedValue({ data: { success: true } });
      axios.delete.mockResolvedValue({ data: { success: true } });

      await settingsService.getNotificationPreferences();
      expect(axios.get).toHaveBeenCalledWith(
        `${baseURL}/notifications`,
        expect.any(Object)
      );

      await settingsService.updateNotificationPreferences({ email_notifications: true });
      expect(axios.put).toHaveBeenCalledWith(
        `${baseURL}/notifications`,
        expect.any(Object),
        expect.any(Object)
      );

      await settingsService.changePassword({
        current_password: 'old',
        new_password: 'NewPass123!',
        confirm_password: 'NewPass123!'
      });
      expect(axios.post).toHaveBeenCalledWith(
        `${baseURL}/security/password`,
        expect.any(Object),
        expect.any(Object)
      );

      await settingsService.deactivateAccount('password');
      expect(axios.post).toHaveBeenCalledWith(
        `${baseURL}/security/account/deactivate`,
        expect.any(Object),
        expect.any(Object)
      );

      await settingsService.deleteAccount('password');
      expect(axios.delete).toHaveBeenCalledWith(
        `${baseURL}/security/account/delete`,
        expect.any(Object)
      );
    });
  });
});
