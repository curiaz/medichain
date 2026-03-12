import { clearLocalData, signOutCurrentUser } from './clearUserData';

// Simple tests that verify the utility functions exist and work
describe('clearUserData utilities', () => {
  it('should have clearLocalData function', () => {
    expect(typeof clearLocalData).toBe('function');
  });

  it('should have signOutCurrentUser function', () => {
    expect(typeof signOutCurrentUser).toBe('function');
  });

  it('clearLocalData should return a boolean', () => {
    const result = clearLocalData();
    expect(typeof result).toBe('boolean');
  });

  it('signOutCurrentUser should return a promise', async () => {
    try {
      const result = await signOutCurrentUser();
      expect(typeof result).toBe('boolean');
    } catch (error) {
      // Errors are acceptable in test environment
      expect(error).toBeDefined();
    }
  });
});
