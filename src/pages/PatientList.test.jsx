import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PatientList from './PatientList';

const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('PatientList Component', () => {
  describe('Component Structure', () => {
    it('renders without crashing', () => {
      const { container } = render(
        <TestWrapper>
          <PatientList />
        </TestWrapper>
      );
      
      expect(container).toBeTruthy();
    });

    it('handles missing props gracefully', () => {
      expect(() => {
        render(
          <TestWrapper>
            <PatientList />
          </TestWrapper>
        );
      }).not.toThrow();
    });

    it('component exists and can be rendered', () => {
      const { container } = render(
        <TestWrapper>
          <PatientList />
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
            <PatientList />
          </TestWrapper>
        );
      }).not.toThrow();
    });
  });
});
