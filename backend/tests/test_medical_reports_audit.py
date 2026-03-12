"""
Unit tests for Medical Reports Audit Logging
Tests that medical report creation/updates properly log to blockchain audit ledger

Note: These tests verify the audit logging implementation.
Full integration tests require proper Supabase and Firebase setup.
"""

import unittest
import inspect
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


class TestMedicalReportsAuditLogging(unittest.TestCase):
    """Test audit logging for medical reports"""
    
    def test_audit_logging_code_exists(self):
        """Test that audit logging code exists in create_medical_report function"""
        from medical_reports_routes import create_medical_report
        import medical_reports_routes
        
        # Get source code
        source = inspect.getsource(create_medical_report)
        
        # Verify audit_service is imported
        module_source = inspect.getsource(medical_reports_routes)
        self.assertIn('audit_service', module_source, "audit_service should be imported")
        
        # Verify audit logging calls exist
        self.assertIn('audit_service.log_action', source, 
                     "audit_service.log_action should be called in create_medical_report")
        
        # Verify REVIEW_DIAGNOSIS action type
        self.assertIn('REVIEW_DIAGNOSIS', source,
                     "REVIEW_DIAGNOSIS action type should be in create_medical_report")
        
        # Verify CREATE_MEDICAL_RECORD or UPDATE_MEDICAL_RECORD
        self.assertTrue(
            'CREATE_MEDICAL_RECORD' in source or 'UPDATE_MEDICAL_RECORD' in source,
            "CREATE_MEDICAL_RECORD or UPDATE_MEDICAL_RECORD should be in create_medical_report"
        )
        
        # Verify health record ID is logged
        self.assertIn('health_record_id', source,
                     "health_record_id should be logged in REVIEW_DIAGNOSIS")
        
        # Verify doctor name and patient name are logged
        self.assertIn('doctor_name', source,
                     "doctor_name should be logged in REVIEW_DIAGNOSIS")
        self.assertIn('patient_name', source,
                     "patient_name should be logged in REVIEW_DIAGNOSIS")
    
    def test_audit_logging_called_twice(self):
        """Test that audit logging is called twice (once for medical record, once for review)"""
        from medical_reports_routes import create_medical_report
        
        # Get source code
        source = inspect.getsource(create_medical_report)
        
        # Count occurrences of audit_service.log_action
        log_action_count = source.count('audit_service.log_action')
        
        # Should be called at least twice (once for medical record, once for review)
        self.assertGreaterEqual(log_action_count, 2,
                               f"audit_service.log_action should be called at least twice, found {log_action_count}")
    
    def test_review_diagnosis_data_structure(self):
        """Test that REVIEW_DIAGNOSIS includes all required fields"""
        from medical_reports_routes import create_medical_report
        
        # Get source code
        source = inspect.getsource(create_medical_report)
        
        # Verify required fields in data_after for REVIEW_DIAGNOSIS
        required_fields = [
            'health_record_id',
            'doctor_name',
            'patient_name',
            'diagnosis',
            'appointment_id',
            'review_status'
        ]
        
        for field in required_fields:
            self.assertIn(field, source,
                         f"{field} should be included in REVIEW_DIAGNOSIS data_after")
    
    def test_action_description_format(self):
        """Test that action description includes doctor and patient names"""
        from medical_reports_routes import create_medical_report
        
        # Get source code
        source = inspect.getsource(create_medical_report)
        
        # Verify description format includes key information
        self.assertIn('Dr.', source,
                     "Action description should include 'Dr.' prefix for doctor name")
        self.assertIn('reviewed diagnosis', source.lower(),
                     "Action description should mention 'reviewed diagnosis'")
        self.assertIn('Health Record ID', source,
                     "Action description should include 'Health Record ID'")


if __name__ == '__main__':
    unittest.main()
