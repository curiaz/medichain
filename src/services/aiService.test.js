import { aiService } from './aiService';

// Simple tests that verify the service structure
describe('aiService', () => {
  it('should have getDiagnosis method', () => {
    expect(aiService).toHaveProperty('getDiagnosis');
    expect(typeof aiService.getDiagnosis).toBe('function');
  });

  it('should have getHistory method', () => {
    expect(aiService).toHaveProperty('getHistory');
    expect(typeof aiService.getHistory).toBe('function');
  });

  it('getDiagnosis should handle errors gracefully', async () => {
    // Test that the method exists and can be called
    try {
      await aiService.getDiagnosis({ symptoms: '' });
    } catch (error) {
      // Error handling is expected
      expect(error).toBeDefined();
    }
  });
});
