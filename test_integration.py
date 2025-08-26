#!/usr/bin/env python3
"""
Integration test script for Python API and Node-RED endpoints
Run this script to test the complete integration between your Python API and Node-RED
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Configuration
PYTHON_API_URL = "http://localhost:8000"
NODE_RED_URL = "http://localhost:1880"

class IntegrationTester:
    def __init__(self):
        self.python_api_url = PYTHON_API_URL
        self.node_red_url = NODE_RED_URL
        self.test_results = []
    
    async def test_endpoint(self, session, name, method, url, data=None):
        """Test a single endpoint and record results"""
        try:
            if method.upper() == "GET":
                async with session.get(url) as response:
                    result = await self._process_response(name, response)
            elif method.upper() == "POST":
                async with session.post(url, json=data) as response:
                    result = await self._process_response(name, response)
            else:
                result = {"name": name, "status": "ERROR", "message": f"Unsupported method: {method}"}
            
            self.test_results.append(result)
            return result
        
        except Exception as e:
            result = {"name": name, "status": "ERROR", "message": str(e)}
            self.test_results.append(result)
            return result
    
    async def _process_response(self, name, response):
        """Process HTTP response and return test result"""
        try:
            if response.status == 200 or response.status == 201:
                data = await response.json()
                return {
                    "name": name,
                    "status": "PASS",
                    "status_code": response.status,
                    "message": "Success",
                    "data_keys": list(data.keys()) if isinstance(data, dict) else "Non-dict response"
                }
            else:
                text = await response.text()
                return {
                    "name": name,
                    "status": "FAIL",
                    "status_code": response.status,
                    "message": f"HTTP {response.status}: {text[:100]}"
                }
        except Exception as e:
            return {
                "name": name,
                "status": "ERROR",
                "message": f"Response processing error: {str(e)}"
            }
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Integration Tests...")
        print(f"⏰ Test started at: {datetime.now().isoformat()}")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Test Python API endpoints
            print("\\n🐍 Testing Python API Endpoints:")
            await self.test_endpoint(session, "Python API Health", "GET", f"{self.python_api_url}/")
            await self.test_endpoint(session, "Python API Health Check", "GET", f"{self.python_api_url}/api/health")
            await self.test_endpoint(session, "Python API Sensors", "GET", f"{self.python_api_url}/api/sensors")
            await self.test_endpoint(session, "Python API Devices", "GET", f"{self.python_api_url}/api/devices")
            
            # Test Python API control endpoint
            control_data = {"device": "light_living_room", "action": "toggle"}
            await self.test_endpoint(session, "Python API Control", "POST", f"{self.python_api_url}/api/data/control", control_data)
            
            # Test Node-RED direct endpoints
            print("\\n🔴 Testing Node-RED Direct Endpoints:")
            await self.test_endpoint(session, "Node-RED Sensors", "GET", f"{self.node_red_url}/sensors")
            await self.test_endpoint(session, "Node-RED Devices", "GET", f"{self.node_red_url}/devices")
            await self.test_endpoint(session, "Node-RED Status", "GET", f"{self.node_red_url}/status")
            await self.test_endpoint(session, "Node-RED Data", "GET", f"{self.node_red_url}/data")
            
            # Test Node-RED control endpoint
            await self.test_endpoint(session, "Node-RED Control", "POST", f"{self.node_red_url}/control", control_data)
        
        # Print results
        self.print_results()
        return self.get_summary()
    
    def print_results(self):
        """Print formatted test results"""
        print("\\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_icon} {result['name']:<30} | {result['status']:<6} | {result.get('message', 'N/A')}")
            
            if result["status"] == "PASS" and "data_keys" in result:
                print(f"   └─ Response keys: {result['data_keys']}")
    
    def get_summary(self):
        """Get test summary statistics"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        errors = sum(1 for r in self.test_results if r["status"] == "ERROR")
        
        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": round((passed / total) * 100, 1) if total > 0 else 0
        }
        
        print("\\n" + "=" * 60)
        print("📈 SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Errors: {errors}")
        print(f"📊 Success Rate: {summary['success_rate']}%")
        
        if summary['success_rate'] == 100:
            print("🎉 All tests passed! Your integration is working perfectly!")
        elif summary['success_rate'] >= 80:
            print("✨ Most tests passed! Minor issues to resolve.")
        else:
            print("🔧 Several issues found. Check your setup.")
        
        return summary

async def main():
    """Main test function"""
    print("🚀 Python API + Node-RED Integration Test")
    print("This script will test the communication between your Python API and Node-RED")
    print("Make sure both services are running before proceeding.\\n")
    
    tester = IntegrationTester()
    
    try:
        summary = await tester.run_all_tests()
        
        # Exit with appropriate code
        if summary['success_rate'] == 100:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Some failures
            
    except KeyboardInterrupt:
        print("\\n⏹️ Tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\\n💥 Unexpected error: {e}")
        sys.exit(3)

if __name__ == "__main__":
    # Check if required packages are available
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp is required for this test script.")
        print("Install it with: pip3 install aiohttp")
        sys.exit(4)
    
    asyncio.run(main())
