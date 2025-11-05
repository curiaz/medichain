import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PatientList from '../pages/PatientList';
import DatabaseService from '../services/databaseService';

// Mock the DatabaseService
jest.mock('../services/databaseService', () => ({
  getAllPatients: jest.fn()
}));

// Mock the AuthContext with a doctor user
const mockUser = {
  uid: 'test-doctor-uid',
  email: 'doctor@test.com',
  profile: {
    id: 'doctor-profile-id',
    first_name: 'John',
    last_name: 'Doctor',
    role: 'doctor'
  }
};

jest.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: true,
    loading: false
  }),
  AuthProvider: ({ children }) => children
}));

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('PatientList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders patient list page title', async () => {
    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: []
    });

    renderWithProviders(<PatientList />);
    
    expect(screen.getByText('PATIENT LIST')).toBeInTheDocument();
  });

  it('displays loading state initially', async () => {
    DatabaseService.getAllPatients.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ success: true, data: [] }), 100))
    );

    renderWithProviders(<PatientList />);
    
    expect(screen.getByText('Loading patients...')).toBeInTheDocument();
  });

  it('displays patient cards when data is loaded', async () => {
    const mockPatients = [
      {
        id: 'patient1',
        name: 'John Doe',
        email: 'john.doe@example.com',
        joined: '2024-01-15T10:30:00Z',
        avatar_url: null
      },
      {
        id: 'patient2',
        name: 'Jane Smith', 
        email: 'jane.smith@example.com',
        joined: '2024-02-20T14:45:00Z',
        avatar_url: null
      }
    ];

    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: mockPatients
    });

    renderWithProviders(<PatientList />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('john.doe@example.com')).toBeInTheDocument();
      expect(screen.getByText('jane.smith@example.com')).toBeInTheDocument();
    });
  });

  it('filters patients based on search input', async () => {
    const mockPatients = [
      {
        id: 'patient1',
        name: 'John Doe',
        email: 'john.doe@example.com',
        joined: '2024-01-15T10:30:00Z',
        avatar_url: null
      },
      {
        id: 'patient2',
        name: 'Jane Smith',
        email: 'jane.smith@example.com', 
        joined: '2024-02-20T14:45:00Z',
        avatar_url: null
      }
    ];

    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: mockPatients
    });

    renderWithProviders(<PatientList />);

    // Wait for patients to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    // Test search functionality
    const searchInput = screen.getByPlaceholderText('Search patients by name or email...');
    fireEvent.change(searchInput, { target: { value: 'John' } });

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('displays search stats correctly', async () => {
    const mockPatients = [
      {
        id: 'patient1',
        name: 'John Doe', 
        email: 'john.doe@example.com',
        joined: '2024-01-15T10:30:00Z',
        avatar_url: null
      },
      {
        id: 'patient2',
        name: 'Jane Smith',
        email: 'jane.smith@example.com',
        joined: '2024-02-20T14:45:00Z', 
        avatar_url: null
      }
    ];

    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: mockPatients
    });

    renderWithProviders(<PatientList />);

    await waitFor(() => {
      expect(screen.getByText('Managing 2 patients')).toBeInTheDocument();
    });
  });

  it('displays empty state when no patients found', async () => {
    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: []
    });

    renderWithProviders(<PatientList />);

    await waitFor(() => {
      expect(screen.getByText('No patients found')).toBeInTheDocument();
    });
  });

  it('displays error message when database fails', async () => {
    DatabaseService.getAllPatients.mockResolvedValue({
      success: false,
      error: 'Database connection failed'
    });

    renderWithProviders(<PatientList />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load patient list')).toBeInTheDocument();
    });
  });

  it('shows patient initials when no avatar is provided', async () => {
    const mockPatients = [
      {
        id: 'patient1',
        name: 'John Doe',
        email: 'john.doe@example.com', 
        joined: '2024-01-15T10:30:00Z',
        avatar_url: null
      }
    ];

    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: mockPatients
    });

    renderWithProviders(<PatientList />);

    await waitFor(() => {
      expect(screen.getByText('JD')).toBeInTheDocument(); // Initials for John Doe
    });
  });

  it('handles refresh button click', async () => {
    DatabaseService.getAllPatients.mockResolvedValue({
      success: true,
      data: []
    });

    renderWithProviders(<PatientList />);

    await waitFor(() => {
      expect(screen.getByText('Refresh')).toBeInTheDocument();
    });

    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    // DatabaseService.getAllPatients should be called again
    expect(DatabaseService.getAllPatients).toHaveBeenCalledTimes(2);
  });
});