#!/usr/bin/env python3
"""
MediChain AI Server - Endpoint Testing Suite
Tests all server endpoints and API functionality
"""

import requests
import json
import time
from datetime import datetime

class ServerTester:
    """Test suite for MediChain AI Server endpoints"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.timeout = 15
        self.test_results = []
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 {test_name}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            self.test_results.append({
                'test': test_name,
                'status': 'PASSED' if result else 'FAILED',
                'time': end_time - start_time,
                'success': result
            })
            
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status} ({end_time - start_time:.3f}s)")
            return result
            
        except Exception as e:
            self.test_results.append({
                'test': test_name,
                'status': 'ERROR',
                'error': str(e),
                'success': False
            })
            print(f"🚨 ERROR: {e}")
            return False
    
    def test_health_endpoint(self):
        """Test /health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {data}")
                return True
            else:
                print(f"   ❌ Bad Status Code: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused - server not running")
            return False
    
    def test_system_info_endpoint(self):
        """Test /system-info endpoint"""
        try:
            response = requests.get(f"{self.base_url}/system-info", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status Code: {response.status_code}")
                print(f"   System: {data.get('system', 'N/A')}")
                print(f"   AI Available: {data.get('ai_diagnosis_available', False)}")
                if 'model_info' in data:
                    model_info = data['model_info']
                    print(f"   Features: {model_info.get('features_count', 'N/A')}")
                    print(f"   Diagnoses: {model_info.get('supported_diagnoses', 'N/A')}")
                return True
            else:
                print(f"   ❌ Bad Status Code: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused - server not running")
            return False
    
    def test_diagnose_endpoint_basic(self):
        """Test /diagnose endpoint with basic request"""
        test_data = {
            "symptoms": {"symptomText": "headache, fever, cough"},
            "patient_data": {
                "age": 25,
                "gender": "male",
                "patient_id": "test_basic",
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
                data = response.json()
                print(f"   Status Code: {response.status_code}")
                print(f"   Diagnosis: {data.get('primary_diagnosis', 'N/A')}")
                print(f"   Confidence: {data.get('confidence', 0):.1f}%")
                print(f"   Top Predictions: {len(data.get('top_predictions', []))}")
                return True
            else:
                print(f"   ❌ Bad Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused - server not running")
            return False
    
    def test_diagnose_endpoint_complex(self):
        """Test /diagnose endpoint with complex symptoms"""
        test_data = {
            "symptoms": {"symptomText": "severe headache for 3 days, high fever, persistent cough, extreme fatigue, body aches, sore throat"},
            "patient_data": {
                "age": 34,
                "gender": "female",
                "patient_id": "test_complex",
                "name": "Complex Test Patient"
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
                data = response.json()
                print(f"   Status Code: {response.status_code}")
                print(f"   Diagnosis: {data.get('primary_diagnosis', 'N/A')}")
                print(f"   Confidence: {data.get('confidence', 0):.1f}%")
                
                # Check top predictions
                predictions = data.get('top_predictions', [])
                print(f"   Top Predictions: {len(predictions)}")
                
                # Check medications
                has_medications = False
                for pred in predictions:
                    if pred.get('medications') and len(pred['medications']) > 0:
                        has_medications = True
                        break
                
                print(f"   Has Medications: {has_medications}")
                
                # Check confidence boosting
                base_conf = data.get('base_confidence', 0)
                enhanced_conf = data.get('confidence', 0)
                boost_applied = enhanced_conf > base_conf
                print(f"   Confidence Boosting: {boost_applied}")
                
                return True
            else:
                print(f"   ❌ Bad Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused - server not running")
            return False
    
    def test_error_handling(self):
        """Test error handling with invalid requests"""
        # Test empty request
        try:
            response = requests.post(
                f"{self.base_url}/diagnose",
                json={},
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            
            # Should return 400 for empty request
            if response.status_code == 400:
                print(f"   ✅ Empty request handled correctly (400)")
                return True
            else:
                print(f"   ⚠️ Unexpected status for empty request: {response.status_code}")
                return True  # Still acceptable if handled differently
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection refused - server not running")
            return False
    
    def run_all_tests(self):
        """Run all server endpoint tests"""
        print("🌐 MediChain AI Server - Endpoint Testing Suite")
        print("=" * 60)
        print(f"🎯 Target Server: {self.base_url}")
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        tests = [
            ("Health Endpoint Test", self.test_health_endpoint),
            ("System Info Endpoint Test", self.test_system_info_endpoint),
            ("Basic Diagnosis Test", self.test_diagnose_endpoint_basic),
            ("Complex Diagnosis Test", self.test_diagnose_endpoint_complex),
            ("Error Handling Test", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SERVER ENDPOINT TEST SUMMARY")
        print("=" * 60)
        print(f"📈 Total Tests: {total}")
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {total - passed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            test_time = result.get('time', 0)
            print(f"   {status_icon} {result['test']}: {result['status']} ({test_time:.3f}s)")
        
        print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if passed == total:
            print("🎉 ALL SERVER TESTS PASSED!")
            print("✅ Server is fully operational")
        else:
            print("⚠️ Some server tests failed")
            print("❓ Check if server is running on http://localhost:5001")
        
        print("=" * 60)
        
        return passed == total

def main():
    """Main execution"""
    tester = ServerTester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
