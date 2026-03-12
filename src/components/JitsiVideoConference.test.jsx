import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JitsiVideoConference from './JitsiVideoConference';

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('JitsiVideoConference Component', () => {
  describe('Component Structure', () => {
    it('renders without crashing', () => {
      const { container } = render(
        <TestWrapper>
          <JitsiVideoConference />
        </TestWrapper>
      );
      
      expect(container).toBeTruthy();
    });

    it('handles missing props gracefully', () => {
      expect(() => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      }).not.toThrow();
    });

    it('component exists and can be rendered', () => {
      const { container } = render(
        <TestWrapper>
          <JitsiVideoConference />
        </TestWrapper>
      );
      
      expect(container).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('handles component mount without errors', () => {
      expect(() => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      }).not.toThrow();
    });

    it('handles missing URL parameters', () => {
      expect(() => {
        render(
          <TestWrapper>
            <JitsiVideoConference />
          </TestWrapper>
        );
      }).not.toThrow();
    });
  });
});
