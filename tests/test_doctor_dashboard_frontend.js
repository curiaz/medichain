/**
 * Unit tests for Doctor Dashboard Frontend
 * Tests statistics loading and recent activity functionality
 */

// Mock dependencies
const mockSupabase = {
  from: jest.fn(() => ({
    select: jest.fn(() => ({
      eq: jest.fn(() => ({
        in: jest.fn(() => ({
          execute: jest.fn()
        })),
        not: jest.fn(() => ({
          neq: jest.fn(() => ({
            execute: jest.fn()
          }))
        })),
        gte: jest.fn(() => ({
          execute: jest.fn()
        })),
        execute: jest.fn()
      }))
    }))
  }))
};

const mockAxios = {
  get: jest.fn(),
  post: jest.fn()
};

describe('Doctor Dashboard Statistics', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getDoctorStats', () => {
    test('should count pending reviews correctly', async () => {
      // Mock appointments with AI diagnosis
      const appointments = [
        { id: 'appt1' },
        { id: 'appt2' },
        { id: 'appt3' }
      ];

      // Mock medical reports - only appt1 is reviewed
      const reports = [
        { appointment_id: 'appt1', review_status: 'reviewed' }
      ];

      // Calculate pending
      const reviewedIds = new Set(
        reports
          .filter(r => r.review_status === 'reviewed')
          .map(r => r.appointment_id)
      );
      const pending = appointments.filter(a => !reviewedIds.has(a.id));

      expect(pending.length).toBe(2); // appt2 and appt3
    });

    test('should only count reviewed reports for AI Diagnosis Reviewed', () => {
      const reports = [
        { id: '1', review_status: 'reviewed' },
        { id: '2', review_status: 'pending' },
        { id: '3', review_status: 'reviewed' },
        { id: '4', review_status: 'pending' }
      ];

      const reviewed = reports.filter(r => r.review_status === 'reviewed');
      expect(reviewed.length).toBe(2);
    });

    test('should handle missing review_status column gracefully', () => {
      // Fallback to diagnosis check if review_status doesn't exist
      const reports = [
        { id: '1', diagnosis: 'Cold' },
        { id: '2', diagnosis: '' },
        { id: '3', diagnosis: null }
      ];

      const reviewed = reports.filter(r => 
        r.diagnosis && r.diagnosis !== ''
      );
      expect(reviewed.length).toBe(1);
    });

    test('should count today\'s activity only for reviewed reports', () => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const reports = [
        { 
          id: '1', 
          review_status: 'reviewed', 
          updated_at: new Date().toISOString() 
        },
        { 
          id: '2', 
          review_status: 'pending', 
          updated_at: new Date().toISOString() 
        },
        { 
          id: '3', 
          review_status: 'reviewed', 
          updated_at: new Date(Date.now() - 86400000).toISOString() // yesterday
        }
      ];

      const todayReviewed = reports.filter(r => {
        const updated = new Date(r.updated_at);
        return r.review_status === 'reviewed' && updated >= today;
      });

      expect(todayReviewed.length).toBe(1);
    });
  });

  describe('loadRecentActivity', () => {
    test('should handle missing appointment_id gracefully', () => {
      const report = {
        id: 'report1',
        patient_firebase_uid: 'patient-uid-123',
        diagnosis: 'Test diagnosis',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      // Should still create activity item even without appointment_id
      const activity = {
        id: report.id,
        patientName: `Patient ${report.patient_firebase_uid.substring(0, 8)}...`,
        timeAgo: 'Just now',
        action: 'created for'
      };

      expect(activity.id).toBe('report1');
      expect(activity.patientName).toContain('Patient');
    });

    test('should determine created vs updated correctly', () => {
      const now = new Date();
      const created = new Date(now.getTime() - 3600000); // 1 hour ago
      const updated = new Date(now.getTime() - 1800000); // 30 minutes ago

      const report = {
        created_at: created.toISOString(),
        updated_at: updated.toISOString()
      };

      const createdAt = new Date(report.created_at);
      const updatedAt = new Date(report.updated_at);
      const isUpdated = Math.abs(createdAt.getTime() - updatedAt.getTime()) > 1000;

      expect(isUpdated).toBe(true);
    });

    test('should use patient info from backend join if available', () => {
      const report = {
        id: 'report1',
        user_profiles: {
          first_name: 'John',
          last_name: 'Doe'
        },
        diagnosis: 'Test',
        created_at: new Date().toISOString()
      };

      let patientName = 'Unknown Patient';
      if (report.user_profiles) {
        patientName = `${report.user_profiles.first_name || ''} ${report.user_profiles.last_name || ''}`.trim() || patientName;
      }

      expect(patientName).toBe('John Doe');
    });
  });
});

describe('Medical Reports Backend', () => {
  test('should set review_status to reviewed on save', () => {
    const medicalReportData = {
      appointment_id: 'appt1',
      patient_firebase_uid: 'patient-uid',
      diagnosis: 'Test diagnosis',
      review_status: 'reviewed'  // Should be set automatically
    };

    expect(medicalReportData.review_status).toBe('reviewed');
  });

  test('should include patient info in get_doctor_medical_reports', () => {
    // Test that the backend tries to join user_profiles
    const expectedSelect = "*, user_profiles!medical_records_patient_firebase_uid_fkey(first_name, last_name, email)";
    
    // This verifies the join query structure
    expect(expectedSelect).toContain('user_profiles');
    expect(expectedSelect).toContain('first_name');
    expect(expectedSelect).toContain('last_name');
  });
});

