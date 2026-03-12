import { patientService } from './patientService';

// Simple tests that verify the service structure
describe('patientService', () => {
  it('should have getAllPatients method', () => {
    expect(patientService).toHaveProperty('getAllPatients');
    expect(typeof patientService.getAllPatients).toBe('function');
  });

  it('should have getPatientById method', () => {
    expect(patientService).toHaveProperty('getPatientById');
    expect(typeof patientService.getPatientById).toBe('function');
  });

  it('should have createPatient method', () => {
    expect(patientService).toHaveProperty('createPatient');
    expect(typeof patientService.createPatient).toBe('function');
  });

  it('should have updatePatient method', () => {
    expect(patientService).toHaveProperty('updatePatient');
    expect(typeof patientService.updatePatient).toBe('function');
  });

  it('should have deletePatient method', () => {
    expect(patientService).toHaveProperty('deletePatient');
    expect(typeof patientService.deletePatient).toBe('function');
  });
});
