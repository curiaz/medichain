#!/usr/bin/env python3
"""
MediChain AI System - Master Test Runner
Executes all automated tests and generates comprehensive reports
"""

import os
import sys
import subprocess
import time
from datetime import datetime
import json

class MediChainTestRunner:
    """Master test runner for MediChain AI System"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_python_script(self, script_name, description):
        """Run a Python test script and capture results"""
        print(f"\n🧪 {description}")
        print("-" * 60)
        
        if not os.path.exists(script_name):
            print(f"   ❌ Test script not found: {script_name}")
            return False
        
        try:
            start_time = time.time()
            result = subprocess.run([sys.executable, script_name], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=120)
            end_time = time.time()
            
            success = result.returncode == 0
            
            self.test_results[script_name] = {
                'description': description,
                'success': success,
                'returncode': result.returncode,
                'duration': end_time - start_time,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            # Print script output
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and not success:
                print(f"❌ Errors:\n{result.stderr}")
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\n{status} - {description} ({end_time - start_time:.2f}s)")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Test timed out after 120 seconds")
            self.test_results[script_name] = {
                'description': description,
                'success': False,
                'error': 'Timeout',
                'duration': 120
            }
            return False
        except Exception as e:
            print(f"   🚨 Exception: {e}")
            self.test_results[script_name] = {
                'description': description,
                'success': False,
                'error': str(e),
                'duration': 0
            }
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 MEDICHAIN AI SYSTEM - COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"⏰ Test Session Duration: {self.end_time - self.start_time:.2f} seconds")
        print(f"📈 Total Test Suites: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        print(f"\n📋 Test Suite Results:")
        print("-" * 50)
        
        for script, result in self.test_results.items():
            status_icon = "✅" if result['success'] else "❌"
            duration = result.get('duration', 0)
            print(f"{status_icon} {result['description']}")
            print(f"   Script: {script}")
            print(f"   Duration: {duration:.2f}s")
            if not result['success']:
                error = result.get('error', result.get('stderr', 'Unknown error'))
                print(f"   Error: {error[:100]}...")
            print()
        
        # Overall system status
        print("=" * 80)
        if passed_tests == total_tests:
            print("🎉 SYSTEM STATUS: ALL TESTS PASSED!")
            print("✅ MediChain AI System is fully operational and ready for production")
            system_status = "HEALTHY"
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("⚠️ SYSTEM STATUS: MOSTLY OPERATIONAL")
            print("🔧 Some tests failed but core functionality appears intact")
            system_status = "NEEDS_ATTENTION"
        else:
            print("🚨 SYSTEM STATUS: CRITICAL ISSUES DETECTED")
            print("❌ Multiple test failures - system may not be ready for use")
            system_status = "CRITICAL"
        
        print(f"🏥 Final Assessment: {system_status}")
        print("=" * 80)
        
        return passed_tests == total_tests
    
    def save_report_json(self):
        """Save detailed test report as JSON"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'duration': self.end_time - self.start_time if self.end_time and self.start_time else 0,
            'total_suites': len(self.test_results),
            'passed_suites': sum(1 for r in self.test_results.values() if r['success']),
            'test_results': self.test_results
        }
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"📄 Detailed report saved: {report_file}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")
    
    def run_all_tests(self):
        """Run all available test suites"""
        print("🏥 MediChain AI System - Master Test Execution")
        print(f"🗓️ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # Define all test suites
        test_suites = [
            ("test_percentage_confidence.py", "Percentage Confidence Validation"),
            ("test_quick_runner.py", "Quick System Validation"),
            ("test_suite_automated.py", "Comprehensive Unit Testing"),
            ("test_server_endpoints.py", "Server Endpoint Testing")
        ]
        
        # Check which test files exist
        available_tests = []
        for script, description in test_suites:
            if os.path.exists(script):
                available_tests.append((script, description))
            else:
                print(f"⚠️ Test file not found: {script}")
        
        if not available_tests:
            print("❌ No test files found! Cannot proceed.")
            return False
        
        print(f"🎯 Found {len(available_tests)} test suites to execute:")
        for script, description in available_tests:
            print(f"   • {description} ({script})")
        
        # Execute all available tests
        all_passed = True
        for script, description in available_tests:
            success = self.run_python_script(script, description)
            if not success:
                all_passed = False
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        final_success = self.generate_test_report()
        
        # Save JSON report
        self.save_report_json()
        
        return final_success
    
    def run_essential_tests_only(self):
        """Run only essential tests for quick validation"""
        print("⚡ MediChain AI System - Essential Tests Only")
        print(f"🗓️ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.start_time = time.time()
        
        # Essential tests only
        essential_tests = [
            ("test_percentage_confidence.py", "Your Percentage Confidence Test"),
            ("test_quick_runner.py", "Quick System Validation")
        ]
        
        all_passed = True
        for script, description in essential_tests:
            if os.path.exists(script):
                success = self.run_python_script(script, description)
                if not success:
                    all_passed = False
            else:
                print(f"⚠️ Essential test not found: {script}")
                all_passed = False
        
        self.end_time = time.time()
        
        print(f"\n⚡ Essential Tests Summary:")
        print(f"   Duration: {self.end_time - self.start_time:.2f}s")
        print(f"   Status: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        return all_passed

def main():
    """Main execution with command line options"""
    runner = MediChainTestRunner()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = runner.run_essential_tests_only()
    else:
        success = runner.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
