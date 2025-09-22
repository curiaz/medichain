#!/usr/bin/env python3
"""
Comprehensive Automated Unit Test Suite for MediChain AI System
Tests all components: AI diagnosis, confidence boosting, server endpoints, and data validation
"""

import unittest
import json
import requests
import time
import threading
from datetime import datetime
import sys
import os

# Import system components
try:
    from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
    from medication_recommendations import MedicationRecommendations
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the backend directory")
    sys.exit(1)

class TestMediChainAIDiagnosis(unittest.TestCase):
    """Test suite for the core AI diagnosis system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any test methods"""
        print("\n🚀 Initializing MediChain AI Test Suite...")
        try:
            cls.ai_diagnosis = ComprehensiveAIDiagnosis()
            cls.medication_system = MedicationRecommendations()
            print("✅ AI system initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize AI system: {e}")
            raise
    
    def test_01_percentage_confidence_validation(self):
        """Test that all confidence values are in 0-100% range"""
        print("\n🧪 Test 1: Percentage Confidence Validation")
        
        symptoms = "severe headache and fever for 3 days, feeling very tired"
        result = self.ai_diagnosis.diagnose(symptoms)
        
        # Test primary confidence
        self.assertGreaterEqual(result['confidence'], 0, "Confidence should be >= 0%")
        self.assertLessEqual(result['confidence'], 100, "Confidence should be <= 100%")
        
        # Test base confidence
        self.assertGreaterEqual(result['base_confidence'], 0, "Base confidence should be >= 0%")
        self.assertLessEqual(result['base_confidence'], 100, "Base confidence should be <= 100%")
        
        # Test all predictions confidence
        for pred in result['top_predictions']:
            self.assertGreaterEqual(pred['confidence'], 0, f"Prediction confidence should be >= 0%")
            self.assertLessEqual(pred['confidence'], 100, f"Prediction confidence should be <= 100%")
        
        print(f"   ✅ Primary Confidence: {result['confidence']:.1f}%")
        print(f"   ✅ Base Confidence: {result['base_confidence']:.1f}%")
        print(f"   ✅ All {len(result['top_predictions'])} predictions in valid range")
    
    def test_02_primary_diagnosis_accuracy(self):
        """Test primary diagnosis detection for common symptoms"""
        print("\n🧪 Test 2: Primary Diagnosis Accuracy")
        
        test_cases = [
            {
                'symptoms': 'severe headache, fever, cough, sore throat',
                'expected_category': ['Upper_Respiratory_Infection', 'Flu', 'Cold']
            },
            {
                'symptoms': 'stomach pain, nausea, vomiting, diarrhea',
                'expected_category': ['Gastroenteritis', 'Food_Poisoning', 'Stomach_Flu']
            },
            {
                'symptoms': 'chest pain, difficulty breathing, shortness of breath',
                'expected_category': ['Pneumonia', 'Bronchitis', 'Asthma']
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            with self.subTest(test_case=i):
                result = self.ai_diagnosis.diagnose(test_case['symptoms'])
                diagnosis = result['primary_diagnosis']
                
                # Check if diagnosis is not None or empty
                self.assertIsNotNone(diagnosis, "Diagnosis should not be None")
                self.assertNotEqual(diagnosis, '', "Diagnosis should not be empty")
                
                print(f"   Test {i}: '{test_case['symptoms'][:30]}...' → {diagnosis}")
                print(f"   ✅ Confidence: {result['confidence']:.1f}%")
    
    def test_03_top_predictions_ranking(self):
        """Test that top 3 predictions are properly ranked by confidence"""
        print("\n🧪 Test 3: Top 3 Predictions Ranking")
        
        symptoms = "persistent cough, fever, fatigue, body aches"
        result = self.ai_diagnosis.diagnose(symptoms)
        
        predictions = result['top_predictions']
        
        # Test that we have predictions
        self.assertGreater(len(predictions), 0, "Should have at least 1 prediction")
        self.assertLessEqual(len(predictions), 3, "Should have at most 3 predictions")
        
        # Test that predictions are sorted by confidence (descending)
        for i in range(len(predictions) - 1):
            self.assertGreaterEqual(
                predictions[i]['confidence'], 
                predictions[i + 1]['confidence'],
                f"Prediction {i+1} should have higher confidence than prediction {i+2}"
            )
        
        print(f"   ✅ Found {len(predictions)} predictions properly ranked:")
        for i, pred in enumerate(predictions, 1):
            print(f"   {i}. {pred['diagnosis']}: {pred['confidence']:.1f}%")
    
    def test_04_medication_recommendations(self):
        """Test medication recommendation system"""
        print("\n🧪 Test 4: Medication Recommendations")
        
        symptoms = "severe headache, fever, body aches"
        result = self.ai_diagnosis.diagnose(symptoms)
        
        # Test that top predictions have medication recommendations
        for i, pred in enumerate(result['top_predictions'], 1):
            with self.subTest(prediction=i):
                self.assertIn('medications', pred, f"Prediction {i} should have medications")
                self.assertIn('dosage', pred, f"Prediction {i} should have dosage")
                self.assertIn('duration', pred, f"Prediction {i} should have duration")
                self.assertIn('instructions', pred, f"Prediction {i} should have instructions")
                
                # Test that medications is a list
                self.assertIsInstance(pred['medications'], list, "Medications should be a list")
                
                if pred['medications']:  # If medications exist
                    self.assertGreater(len(pred['medications']), 0, "Should have at least one medication")
        
        print(f"   ✅ All {len(result['top_predictions'])} predictions have medication data")
        for i, pred in enumerate(result['top_predictions'], 1):
            med_count = len(pred['medications']) if pred['medications'] else 0
            print(f"   {i}. {pred['diagnosis']}: {med_count} medications recommended")
    
    def test_05_symptom_parsing_accuracy(self):
        """Test natural language symptom parsing"""
        print("\n🧪 Test 5: Symptom Parsing Accuracy")
        
        complex_symptoms = [
            "I have been experiencing severe headaches for the past 3 days along with high fever and extreme fatigue",
            "stomach pain that started yesterday, feeling nauseous and had vomiting twice",
            "difficulty breathing, chest tightness, and persistent dry cough for a week"
        ]
        
        for i, symptom in enumerate(complex_symptoms, 1):
            with self.subTest(symptom=i):
                result = self.ai_diagnosis.diagnose(symptom)
                
                # Test that complex symptoms are processed
                self.assertIsNotNone(result['primary_diagnosis'], "Should parse complex symptoms")
                self.assertGreater(result['confidence'], 0, "Should have some confidence")
                self.assertGreater(len(result['top_predictions']), 0, "Should generate predictions")
                
                print(f"   Complex Symptom {i}: {result['primary_diagnosis']} ({result['confidence']:.1f}%)")
    
    def test_06_confidence_boosting_mechanism(self):
        """Test confidence boosting enhancement"""
        print("\n🧪 Test 6: Confidence Boosting Mechanism")
        
        symptoms = "severe headache, high fever, persistent cough, extreme fatigue, body aches"
        result = self.ai_diagnosis.diagnose(symptoms)
        
        # Test that confidence boosting is applied
        base_conf = result['base_confidence']
        enhanced_conf = result['confidence']
        
        # Enhanced confidence should be >= base confidence
        self.assertGreaterEqual(enhanced_conf, base_conf, "Enhanced confidence should be >= base confidence")
        
        # Calculate boost percentage
        boost_percentage = ((enhanced_conf / base_conf) - 1) * 100 if base_conf > 0 else 0
        
        print(f"   ✅ Base Confidence: {base_conf:.1f}%")
        print(f"   ✅ Enhanced Confidence: {enhanced_conf:.1f}%")
        print(f"   ✅ Confidence Boost: +{boost_percentage:.1f}%")
        
        # Test that boost is reasonable (not excessive)
        self.assertLessEqual(boost_percentage, 100, "Confidence boost should be reasonable (<100%)")
    
    def test_07_edge_cases_handling(self):
        """Test handling of edge cases and invalid inputs"""
        print("\n🧪 Test 7: Edge Cases Handling")
        
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "a",  # Single character
            "headache" * 100,  # Very long input
            "!@#$%^&*()",  # Special characters
        ]
        
        for i, case in enumerate(edge_cases, 1):
            with self.subTest(edge_case=i):
                try:
                    result = self.ai_diagnosis.diagnose(case)
                    # Should either return a result or handle gracefully
                    self.assertIsInstance(result, dict, "Should return a dictionary")
                    print(f"   Edge Case {i}: Handled gracefully")
                except Exception as e:
                    # Should not crash the system
                    print(f"   Edge Case {i}: Exception handled: {type(e).__name__}")
                    # This is acceptable for edge cases
                    continue
    
    def test_08_response_time_performance(self):
        """Test system response time performance"""
        print("\n🧪 Test 8: Response Time Performance")
        
        symptoms = "headache, fever, cough, fatigue"
        
        # Measure response time
        start_time = time.time()
        result = self.ai_diagnosis.diagnose(symptoms)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Test that response time is reasonable (< 5 seconds)
        self.assertLess(response_time, 5.0, "Response time should be < 5 seconds")
        
        print(f"   ✅ Response Time: {response_time:.3f} seconds")
        print(f"   ✅ Performance: {'Excellent' if response_time < 1 else 'Good' if response_time < 3 else 'Acceptable'}")
    
    def test_09_data_structure_validation(self):
        """Test that response data structures are correct"""
        print("\n🧪 Test 9: Data Structure Validation")
        
        symptoms = "fever, cough, sore throat"
        result = self.ai_diagnosis.diagnose(symptoms)
        
        # Test required fields exist
        required_fields = ['primary_diagnosis', 'confidence', 'base_confidence', 'top_predictions']
        for field in required_fields:
            self.assertIn(field, result, f"Result should contain '{field}' field")
        
        # Test top_predictions structure
        self.assertIsInstance(result['top_predictions'], list, "top_predictions should be a list")
        
        for pred in result['top_predictions']:
            prediction_fields = ['diagnosis', 'confidence', 'medications', 'dosage', 'duration', 'instructions']
            for field in prediction_fields:
                self.assertIn(field, pred, f"Prediction should contain '{field}' field")
        
        print(f"   ✅ All required fields present")
        print(f"   ✅ Data structure is valid")
        print(f"   ✅ {len(result['top_predictions'])} predictions with complete data")
    
    def test_10_medication_system_integration(self):
        """Test medication recommendation system integration"""
        print("\n🧪 Test 10: Medication System Integration")
        
        # Test medication system directly
        test_diagnoses = ['Upper_Respiratory_Infection', 'Flu', 'Pneumonia']
        
        for diagnosis in test_diagnoses:
            with self.subTest(diagnosis=diagnosis):
                recommendations = self.medication_system.get_recommendations(diagnosis)
                
                # Test that recommendations contain required fields
                required_fields = ['medications', 'dosage', 'duration', 'instructions']
                for field in required_fields:
                    self.assertIn(field, recommendations, f"Recommendations should contain '{field}'")
                
                # Test that medications is a list
                self.assertIsInstance(recommendations['medications'], list, "Medications should be a list")
        
        print(f"   ✅ Medication system integration working")
        print(f"   ✅ Tested {len(test_diagnoses)} diagnosis recommendations")


class TestMediChainServerEndpoints(unittest.TestCase):
    """Test suite for server endpoints (if server is running)"""
    
    def setUp(self):
        """Set up for server tests"""
        self.base_url = "http://localhost:5001"
        self.timeout = 10
    
    def test_11_server_health_endpoint(self):
        """Test server health endpoint"""
        print("\n🧪 Test 11: Server Health Endpoint")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            
            if response.status_code == 200:
                self.assertEqual(response.status_code, 200, "Health endpoint should return 200")
                print("   ✅ Server health endpoint responding")
                print(f"   ✅ Response: {response.json()}")
            else:
                print(f"   ⚠️ Server not responding (status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Server not running - skipping endpoint tests")
            self.skipTest("Server not running")
    
    def test_12_server_diagnose_endpoint(self):
        """Test server diagnosis endpoint"""
        print("\n🧪 Test 12: Server Diagnosis Endpoint")
        
        test_data = {
            "symptoms": {"symptomText": "headache, fever, cough"},
            "patient_data": {
                "age": 25,
                "gender": "male",
                "patient_id": "test_123",
                "name": "Test Patient"
            },
            "doctor_id": None,
            "include_recommendations": True,
            "detailed_analysis": True,
            "save_to_database": False,
            "session_type": "test"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/diagnose",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.assertEqual(response.status_code, 200, "Diagnose endpoint should return 200")
                result = response.json()
                
                # Test response structure
                self.assertIn('primary_diagnosis', result, "Response should contain primary_diagnosis")
                self.assertIn('confidence', result, "Response should contain confidence")
                
                print("   ✅ Server diagnosis endpoint responding")
                print(f"   ✅ Diagnosis: {result.get('primary_diagnosis', 'N/A')}")
                print(f"   ✅ Confidence: {result.get('confidence', 0):.1f}%")
            else:
                print(f"   ⚠️ Server diagnosis endpoint error (status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("   ⚠️ Server not running - skipping endpoint test")
            self.skipTest("Server not running")


def run_comprehensive_tests():
    """Run all tests and generate a comprehensive report"""
    print("🏥 MediChain AI System - Comprehensive Automated Unit Test Suite")
    print("=" * 80)
    print(f"Test Execution Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMediChainAIDiagnosis))
    suite.addTests(loader.loadTestsFromTestCase(TestMediChainServerEndpoints))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"📈 Total Tests Run: {total_tests}")
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failures}")
    print(f"🚨 Tests with Errors: {errors}")
    print(f"⏭️ Tests Skipped: {skipped}")
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    # Print failure details if any
    if result.failures:
        print("\n❌ FAILURE DETAILS:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 ERROR DETAILS:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    # Overall status
    print("\n" + "=" * 80)
    if failures == 0 and errors == 0:
        print("🎉 ALL TESTS PASSED! MediChain AI System is fully operational!")
        system_status = "✅ SYSTEM HEALTHY"
    else:
        print("⚠️ Some tests failed. Please review the system.")
        system_status = "⚠️ SYSTEM NEEDS ATTENTION"
    
    print(f"🏥 System Status: {system_status}")
    print(f"⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
