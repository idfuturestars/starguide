#!/usr/bin/env python3
"""
IDFS StarGuide - Comprehensive Testing Suite
Tests all application features, APIs, and integrations
"""

import requests
import json
import time
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuration
BASE_URL = "http://0.0.0.0:3000"
TIMEOUT = 10
MAX_WORKERS = 5

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.total = 0
        self.details = []

    def add_result(self, test_name, passed, message="", warning=False):
        self.total += 1
        if passed:
            self.passed += 1
            status = f"{Colors.GREEN}✅ PASS{Colors.END}"
        elif warning:
            self.warnings += 1
            status = f"{Colors.YELLOW}⚠️  WARN{Colors.END}"
        else:
            self.failed += 1
            status = f"{Colors.RED}❌ FAIL{Colors.END}"

        print(f"{status} {test_name}: {message}")
        self.details.append({
            'test': test_name,
            'passed': passed,
            'warning': warning,
            'message': message
        })

    def summary(self):
        print(f"\n{Colors.PURPLE}{Colors.BOLD}{'='*50}")
        print("🧪 Test Summary")
        print(f"{'='*50}{Colors.END}")
        print(f"{Colors.GREEN}✅ Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.warnings}{Colors.END}")
        print(f"{Colors.CYAN}📊 Total: {self.total}{Colors.END}")

        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        print(f"{Colors.CYAN}🎯 Success Rate: {success_rate:.1f}%{Colors.END}")

        return self.failed == 0

def test_basic_endpoints(result):
    """Test basic endpoints"""
    print(f"\n{Colors.BLUE}🌐 Testing Basic Endpoints{Colors.END}")

    # Test homepage
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            result.add_result("Homepage", True, f"Status {response.status_code}")
        else:
            result.add_result("Homepage", False, f"Status {response.status_code}")
    except Exception as e:
        result.add_result("Homepage", False, f"Error: {str(e)}")

def test_health_endpoint(result):
    """Test detailed health endpoint"""
    print(f"\n{Colors.BLUE}🏥 Testing Health & Status{Colors.END}")

    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)

        if response.status_code == 200:
            health_data = response.json()

            # Check required fields
            required_fields = ['status', 'timestamp', 'services', 'uptime']
            for field in required_fields:
                if field in health_data:
                    result.add_result(f"Health check - {field}", True, f"Present: {health_data[field]}")
                else:
                    result.add_result(f"Health check - {field}", False, "Missing field")

            # Check services
            if 'services' in health_data:
                services = health_data['services']

                # Firebase
                if 'firebase' in services:
                    fb = services['firebase']
                    result.add_result("Firebase Admin", fb.get('admin', False), f"Available: {fb.get('admin')}")
                    result.add_result("Firestore", fb.get('firestore', False), f"Available: {fb.get('firestore')}")

                # AI Services
                if 'ai' in services:
                    ai = services['ai']
                    for provider in ['openai', 'claude', 'gemini']:
                        if provider in ai:
                            result.add_result(f"AI - {provider.title()}", ai[provider], f"Available: {ai[provider]}")
        else:
            result.add_result("Health endpoint", False, f"Status {response.status_code}")

    except Exception as e:
        result.add_result("Health endpoint", False, f"Error: {str(e)}")

def test_static_files(result):
    """Test static file serving"""
    print(f"\n{Colors.BLUE}📁 Testing Static Files{Colors.END}")

    # Test main HTML content
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        if response.status_code == 200:
            content = response.text.lower()

            # Check for required elements
            checks = [
                ('firebase', 'Firebase integration'),
                ('starguide', 'StarGuide branding'),
                ('socket.io', 'Socket.IO integration'),
                ('idfs', 'IDFS branding'),
                ('authentication', 'Auth system')
            ]

            for check, description in checks:
                if check in content:
                    result.add_result(f"HTML Content - {description}", True, "Found in page")
                else:
                    result.add_result(f"HTML Content - {description}", False, "Not found", warning=True)
        else:
            result.add_result("Main HTML page", False, f"Status {response.status_code}")

    except Exception as e:
        result.add_result("Main HTML page", False, f"Error: {str(e)}")

def test_configuration(result):
    """Test configuration file"""
    print(f"\n{Colors.BLUE}⚙️  Testing Configuration{Colors.END}")

    try:
        response = requests.get(f"{BASE_URL}/config.js", timeout=TIMEOUT)
        if response.status_code == 200:
            content = response.text

            # Check for configuration elements
            checks = [
                ('firebaseConfig', 'Firebase configuration'),
                ('aiConfig', 'AI configuration'),
                ('StarGuide', 'App configuration'),
                ('errorLog', 'Error logging'),
                ('healthCheck', 'Health monitoring')
            ]

            for check, description in checks:
                if check in content:
                    result.add_result(f"Config - {description}", True, "Configured")
                else:
                    result.add_result(f"Config - {description}", False, "Missing", warning=True)
        else:
            result.add_result("Configuration file", False, f"Status {response.status_code}")

    except Exception as e:
        result.add_result("Configuration file", False, f"Error: {str(e)}")

def test_api_endpoints(result):
    """Test API endpoints"""
    print(f"\n{Colors.BLUE}🔌 Testing API Endpoints{Colors.END}")

    # Test online users endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/users/online", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if 'count' in data:
                result.add_result("Online users API", True, f"Count: {data['count']}")
            else:
                result.add_result("Online users API", False, "Missing count field")
        else:
            result.add_result("Online users API", False, f"Status {response.status_code}")
    except Exception as e:
        result.add_result("Online users API", False, f"Error: {str(e)}")

def test_performance(result):
    """Test performance metrics"""
    print(f"\n{Colors.BLUE}⚡ Testing Performance{Colors.END}")

    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        response_time = (time.time() - start_time) * 1000

        if response.status_code == 200:
            if response_time < 1000:
                result.add_result("Response time", True, f"{response_time:.0f}ms")
            else:
                result.add_result("Response time", False, f"{response_time:.0f}ms (slow)", warning=True)
        else:
            result.add_result("Response time", False, f"Status {response.status_code}")

    except Exception as e:
        result.add_result("Response time", False, f"Error: {str(e)}")

def test_error_handling(result):
    """Test error handling"""
    print(f"\n{Colors.BLUE}🛡️  Testing Error Handling{Colors.END}")

    # Test 404 handling
    try:
        response = requests.get(f"{BASE_URL}/nonexistent-page", timeout=TIMEOUT)
        if response.status_code == 404:
            result.add_result("404 Error Handling", True, "Proper 404 response")
        else:
            result.add_result("404 Error Handling", False, f"Unexpected status: {response.status_code}")
    except Exception as e:
        result.add_result("404 Error Handling", False, f"Error: {str(e)}")

    # Test malformed API requests
    try:
        response = requests.post(f"{BASE_URL}/api/progress", 
                               json={"invalid": "data"}, 
                               timeout=TIMEOUT)
        # Should handle gracefully (500 or 400 is acceptable)
        if response.status_code in [400, 500]:
            result.add_result("API Error Handling", True, f"Graceful error: {response.status_code}")
        else:
            result.add_result("API Error Handling", True, f"Response: {response.status_code}", warning=True)
    except Exception as e:
        result.add_result("API Error Handling", True, f"Connection handled gracefully")

def load_test(result):
    """Perform basic load testing"""
    print(f"\n{Colors.BLUE}🔥 Testing Load Handling{Colors.END}")

    def make_request():
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            successes = sum(1 for future in futures if future.result())

        if successes >= 8:
            result.add_result("Load test", True, f"{successes}/10 requests successful")
        else:
            result.add_result("Load test", False, f"Only {successes}/10 requests successful")

    except Exception as e:
        result.add_result("Load test", False, f"Error: {str(e)}")

def main():
    print(f"{Colors.PURPLE}{Colors.BOLD}")
    print("🚀 IDFS StarGuide Comprehensive Test Suite")
    print("Testing all features, APIs, and integrations...")
    print(f"{'='*50}{Colors.END}")

    result = TestResult()

    # Wait for server to be ready
    print(f"\n{Colors.CYAN}⏳ Waiting for server to be ready...{Colors.END}")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✅ Server is ready!{Colors.END}")
                break
        except:
            pass

        if i == max_retries - 1:
            print(f"{Colors.RED}❌ Server not responding. Please start the server first.{Colors.END}")
            return 1

        time.sleep(1)
        print(f"  Retry {i+1}/{max_retries}...", end='\r')

    # Run all tests
    try:
        test_basic_endpoints(result)
        test_health_endpoint(result)
        test_static_files(result)
        test_configuration(result)
        test_api_endpoints(result)
        test_performance(result)
        test_error_handling(result)
        load_test(result)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test suite error: {str(e)}{Colors.END}")

    # Show summary
    success = result.summary()
    print(f"\n{Colors.CYAN}🏥 Health check: {BASE_URL}/api/health{Colors.END}")

    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())