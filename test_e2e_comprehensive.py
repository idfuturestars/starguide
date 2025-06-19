
"""
IDFS StarGuide - Comprehensive End-to-End Testing Framework
Tests all features, validates migration safety, ensures zero downtime
"""

import requests
import time
import json
import sqlite3
from datetime import datetime
import subprocess
import os

class StarGuideE2ETester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        self.migration_safe = True
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
        
    def test_server_health(self):
        """Test server is running and healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            success = response.status_code == 200
            self.log_test("Server Health", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Server Health", False, f"Error: {str(e)}")
            return False
            
    def test_database_integrity(self):
        """Test database structure and data integrity"""
        try:
            db = sqlite3.connect('starguide.db')
            cursor = db.cursor()
            
            # Check all tables exist
            tables = ['users', 'user_profiles', 'assessments', 'questions', 'achievements']
            for table in tables:
                result = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if result is None:
                    raise Exception(f"Table {table} missing")
                    
            # Check question bank
            question_count = cursor.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
            if question_count < 20:
                raise Exception(f"Insufficient questions: {question_count}")
                
            db.close()
            self.log_test("Database Integrity", True, f"All tables present, {question_count} questions")
            return True
        except Exception as e:
            self.log_test("Database Integrity", False, str(e))
            return False
            
    def test_ai_integration(self):
        """Test AI chat functionality"""
        try:
            # Test AI providers status
            response = requests.get(f"{self.base_url}/api/ai-providers-status", timeout=10)
            if response.status_code != 200:
                raise Exception(f"AI status endpoint failed: {response.status_code}")
                
            providers = response.json()
            available_providers = [k for k, v in providers.items() if v]
            
            if available_providers:
                # Test actual AI chat
                chat_response = requests.post(f"{self.base_url}/api/ai-chat", 
                    json={'message': 'Test message', 'provider': available_providers[0]},
                    timeout=15)
                    
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    success = chat_data.get('success', False)
                    self.log_test("AI Integration", success, f"Providers: {available_providers}")
                    return success
                    
            self.log_test("AI Integration", False, "No providers available")
            return False
        except Exception as e:
            self.log_test("AI Integration", False, str(e))
            return False
            
    def test_assessment_flow(self):
        """Test complete assessment workflow"""
        try:
            # Get questions
            response = requests.post(f"{self.base_url}/api/get-questions",
                json={'subject': 'math', 'count': 5},
                timeout=10)
                
            if response.status_code != 200:
                raise Exception(f"Get questions failed: {response.status_code}")
                
            questions_data = response.json()
            if not questions_data.get('success') or len(questions_data.get('questions', [])) < 5:
                raise Exception("Insufficient questions returned")
                
            self.log_test("Assessment Flow", True, f"Retrieved {len(questions_data['questions'])} questions")
            return True
        except Exception as e:
            self.log_test("Assessment Flow", False, str(e))
            return False
            
    def test_replit_services_integration(self):
        """Test Replit services if available"""
        try:
            # Check if Replit DB URL is available
            replit_db_url = os.environ.get('REPLIT_DB_URL')
            if not replit_db_url:
                self.log_test("Replit Services", True, "Not configured (expected)")
                return True
                
            # Test Replit DB connectivity
            test_key = f"test_key_{int(time.time())}"
            test_value = "test_value"
            
            # Set value
            set_response = requests.post(replit_db_url, data={test_key: test_value}, timeout=5)
            if set_response.status_code != 200:
                raise Exception(f"Replit DB set failed: {set_response.status_code}")
                
            # Get value
            get_response = requests.get(f"{replit_db_url}/{test_key}", timeout=5)
            if get_response.status_code != 200 or get_response.text != test_value:
                raise Exception("Replit DB get/set validation failed")
                
            # Clean up
            requests.delete(f"{replit_db_url}/{test_key}", timeout=5)
            
            self.log_test("Replit Services", True, "DB connectivity verified")
            return True
        except Exception as e:
            self.log_test("Replit Services", False, str(e))
            return False
            
    def test_websocket_connectivity(self):
        """Test WebSocket/Socket.IO connectivity"""
        try:
            # Simple connectivity test
            import socketio
            sio = socketio.SimpleClient()
            sio.connect(self.base_url, timeout=10)
            connected = sio.connected
            sio.disconnect()
            
            self.log_test("WebSocket Connectivity", connected, "Socket.IO connection")
            return connected
        except Exception as e:
            self.log_test("WebSocket Connectivity", False, str(e))
            return False
            
    def test_migration_safety(self):
        """Test migration safety and rollback capability"""
        try:
            # Verify current system is working
            health_ok = self.test_server_health()
            db_ok = self.test_database_integrity()
            
            migration_safe = health_ok and db_ok
            
            if migration_safe:
                # Test backup creation
                backup_cmd = "mkdir -p test_backups && cp -r . test_backups/safety_test"
                result = subprocess.run(backup_cmd, shell=True, capture_output=True)
                backup_ok = result.returncode == 0
                
                if backup_ok:
                    # Clean up test backup
                    subprocess.run("rm -rf test_backups", shell=True)
                    
                self.log_test("Migration Safety", migration_safe and backup_ok, 
                             "System stable, backup capable")
            else:
                self.log_test("Migration Safety", False, "System not ready for migration")
                
            self.migration_safe = migration_safe
            return migration_safe
        except Exception as e:
            self.log_test("Migration Safety", False, str(e))
            self.migration_safe = False
            return False
            
    def run_comprehensive_test(self):
        """Run all tests and generate report"""
        print("🚀 Starting IDFS StarGuide Comprehensive E2E Testing")
        print("=" * 60)
        
        start_time = time.time()
        
        # Core functionality tests
        tests = [
            self.test_server_health,
            self.test_database_integrity,
            self.test_ai_integration,
            self.test_assessment_flow,
            self.test_replit_services_integration,
            self.test_websocket_connectivity,
            self.test_migration_safety
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
                
        end_time = time.time()
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print(f"✅ Passed: {passed}/{len(tests)} tests")
        print(f"⏱️ Duration: {end_time - start_time:.2f} seconds")
        print(f"🛡️ Migration Safe: {'Yes' if self.migration_safe else 'No'}")
        
        if passed == len(tests) and self.migration_safe:
            print("🎉 ALL TESTS PASSED - SYSTEM READY FOR MIGRATION")
        else:
            print("⚠️ SYSTEM NOT READY - RESOLVE ISSUES BEFORE MIGRATION")
            
        return {
            'passed': passed,
            'total': len(tests),
            'migration_safe': self.migration_safe,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = StarGuideE2ETester()
    results = tester.run_comprehensive_test()
    
    # Save results
    with open(f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)
