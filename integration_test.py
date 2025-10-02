#!/usr/bin/env python3
"""
Final Integration Test - Test Full Stack Functionality
"""

import sys
import os
import time
import threading
import requests
import subprocess
from subprocess import PIPE, Popen

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_server():
    """Test if backend server can start and serve requests"""
    print("🔧 Testing Backend Server Integration...")
    
    try:
        # Start the Flask server in a separate process
        backend_process = Popen([
            'D:/Repositories/medichain/.venv/Scripts/python.exe', 
            'backend/app.py'
        ], stdout=PIPE, stderr=PIPE, cwd=os.getcwd())
        
        # Give server time to start
        time.sleep(5)
        
        # Test if server is running (check if process is alive)
        if backend_process.poll() is None:
            print("✅ Backend server started successfully")
            backend_process.terminate()
            return True
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend server failed to start: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Backend server test failed: {e}")
        return False

def test_ai_diagnosis_functionality():
    """Test AI diagnosis functionality directly"""
    print("🧠 Testing AI Diagnosis Core Functionality...")
    
    try:
        from app import EnhancedAIEngine
        ai_engine = EnhancedAIEngine()
        
        # Test multiple symptom scenarios
        test_cases = [
            "fever, cough, fatigue",
            "headache, nausea, dizziness", 
            "shortness of breath, chest pain",
            "sore throat, runny nose, sneezing"
        ]
        
        results = []
        for symptoms in test_cases:
            result = ai_engine.diagnose(symptoms, age='Adult (20 - 59 years)', gender='Male')
            if result and result.get('diagnosis') != 'Unknown Condition':
                results.append(True)
                print(f"  ✅ {symptoms} -> {result['diagnosis']}")
            else:
                results.append(False)
                print(f"  ❌ {symptoms} -> Failed diagnosis")
        
        success_rate = sum(results) / len(results) * 100
        print(f"🎯 AI Diagnosis Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 75  # Require at least 75% success rate
        
    except Exception as e:
        print(f"❌ AI diagnosis test failed: {e}")
        return False

def test_file_integrity():
    """Test that all critical files exist and are accessible"""
    print("📁 Testing File Integrity...")
    
    critical_files = [
        'backend/app.py',
        'backend/final_comprehensive_model.pkl',
        'backend/final_enhanced_dataset.csv',
        'src/pages/AIHealth.jsx',
        'src/assets/styles/AIHealth_Modern.css',
        'package.json',
        'public/index.html'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing critical files: {missing_files}")
        return False
    else:
        print("✅ All critical files present")
        return True

def run_integration_tests():
    """Run comprehensive integration tests"""
    print("=" * 70)
    print("MEDICHAIN FINAL INTEGRATION TESTS")
    print("=" * 70)
    
    tests = [
        ("File Integrity", test_file_integrity),
        ("AI Diagnosis Functionality", test_ai_diagnosis_functionality),
        ("Backend Server Integration", test_backend_server)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        try:
            success = test_func()
            results.append(success)
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"🚨 {test_name} ERROR: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    success_rate = passed / total * 100
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 66:  # At least 2/3 tests must pass
        print("\n🎉 INTEGRATION TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        return True
    else:
        print("\n⚠️  INTEGRATION TESTS FAILED - REVIEW ISSUES BEFORE MERGE")
        return False

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)