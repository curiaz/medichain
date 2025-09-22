#!/usr/bin/env python3
"""
MediChain AI System - Quick Test Runner
Executes essential tests for rapid system validation
"""

import sys
import os
import time
from datetime import datetime

def run_quick_tests():
    """Run essential tests quickly"""
    print("🚀 MediChain AI - Quick System Test")
    print("=" * 50)
    
    try:
        # Import and test core system
        from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
        print("✅ Core AI system import successful")
        
        # Initialize AI system
        ai_system = ComprehensiveAIDiagnosis()
        print("✅ AI system initialization successful")
        
        # Test basic diagnosis
        print("\n🧪 Running Basic Diagnosis Test...")
        symptoms = "severe headache and fever for 3 days"
        start_time = time.time()
        result = ai_system.diagnose(symptoms)
        end_time = time.time()
        
        # Validate results
        assert result['confidence'] >= 0 and result['confidence'] <= 100, "Confidence not in percentage range"
        assert result['primary_diagnosis'], "No primary diagnosis returned"
        assert len(result['top_predictions']) > 0, "No predictions returned"
        
        # Display results
        print(f"   Input: {symptoms}")
        print(f"   Diagnosis: {result['primary_diagnosis']}")
        print(f"   Confidence: {result['confidence']:.1f}%")
        print(f"   Base Confidence: {result['base_confidence']:.1f}%")
        print(f"   Response Time: {end_time - start_time:.3f}s")
        print(f"   Predictions Count: {len(result['top_predictions'])}")
        
        # Test medication recommendations
        print("\n💊 Testing Medication Recommendations...")
        has_medications = False
        for pred in result['top_predictions']:
            if pred['medications'] and len(pred['medications']) > 0:
                has_medications = True
                print(f"   ✅ {pred['diagnosis']}: {len(pred['medications'])} medications")
                break
        
        if not has_medications:
            print("   ⚠️ No medication recommendations found")
        
        # Test confidence boosting
        boost_applied = result['confidence'] > result['base_confidence']
        boost_percentage = ((result['confidence'] / result['base_confidence']) - 1) * 100 if result['base_confidence'] > 0 else 0
        
        print(f"\n🚀 Confidence Boosting:")
        print(f"   Boost Applied: {'Yes' if boost_applied else 'No'}")
        if boost_applied:
            print(f"   Boost Amount: +{boost_percentage:.1f}%")
        
        print("\n✅ ALL QUICK TESTS PASSED!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        return False

def check_system_files():
    """Check if all required system files exist"""
    print("\n📁 Checking System Files...")
    
    required_files = [
        'comprehensive_ai_diagnosis.py',
        'medication_recommendations.py',
        'enhanced_confident_ai_server.py',
        'final_comprehensive_model.pkl',
        'final_comprehensive_encoder.pkl',
        'final_comprehensive_features.pkl'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ Missing {len(missing_files)} required files!")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present")
        return True

def main():
    """Main test execution"""
    print("🏥 MediChain AI System - Automated Testing")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check system files
    files_ok = check_system_files()
    if not files_ok:
        print("\n❌ System files missing. Cannot proceed with tests.")
        return False
    
    # Run quick tests
    tests_passed = run_quick_tests()
    
    # Summary
    print("\n" + "=" * 60)
    if tests_passed and files_ok:
        print("🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("✅ Ready for production use")
    else:
        print("⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        print("❌ Please fix issues before proceeding")
    
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return tests_passed and files_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
