import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import DoctorSchedule from './DoctorSchedule';

const TestWrapper = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('DoctorSchedule Component', () => {
  describe('Component Structure', () => {
    it('renders without crashing', () => {
      const { container } = render(
        <TestWrapper>
          <DoctorSchedule />
        </TestWrapper>
      );
      
      expect(container).toBeTruthy();
    });

    it('handles missing props gracefully', () => {
      expect(() => {
        render(
          <TestWrapper>
            <DoctorSchedule />
          </TestWrapper>
        );
      }).not.toThrow();
    });

    it('component exists and can be rendered', () => {
      const { container } = render(
        <TestWrapper>
          <DoctorSchedule />
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
            <DoctorSchedule />
          </TestWrapper>
        );
      }).not.toThrow();
    });
  });
});
