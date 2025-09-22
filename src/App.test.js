import { render, screen } from '@testing-library/react';
import App from './App';

test('renders MediChain app', () => {
  render(<App />);
  const linkElements = screen.getAllByText(/MEDICHAIN/i);
  expect(linkElements.length).toBeGreaterThan(0);
});
