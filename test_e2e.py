#!/usr/bin/env python3
"""
Comprehensive E2E Test Suite for HeatPumpHQ MCP Server

This test suite validates the MCP server against both local and production backends.
It includes proper error handling, performance testing, and comprehensive validation.
"""

import asyncio
import json
import os
import sys
import time
import pytest
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import requests

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test configuration
TEST_TIMEOUT = 60  # seconds
PERFORMANCE_THRESHOLD = 5.0  # seconds

class MCPServerTestSuite:
    """Comprehensive test suite for MCP server"""
    
    def __init__(self, env_mode: str = "default"):
        """Initialize test suite with specific environment"""
        # Set environment mode for server.py to pick up
        os.environ['ENV_MODE'] = env_mode
        
        # Load environment for this test
        if env_mode == "production" and os.path.exists('.env.production'):
            load_dotenv('.env.production')
        elif env_mode == "local" and os.path.exists('.env.local'):
            load_dotenv('.env.local')
        elif os.path.exists('.env.local'):
            load_dotenv('.env.local')
        else:
            load_dotenv()
        
        # Import server after environment is loaded
        from server import mcp, API_BASE_URL, API_TIMEOUT
        self.mcp = mcp
        self.api_base_url = API_BASE_URL
        self.api_timeout = API_TIMEOUT
        
        print(f"🔧 Initialized test suite")
        print(f"📡 API Base URL: {self.api_base_url}")
        print(f"⏱️  Timeout: {self.api_timeout}s")
        print("=" * 60)
    
    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test basic API connectivity and health"""
        test_name = "API Connectivity"
        start_time = time.time()
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.api_base_url}/health", timeout=self.api_timeout)
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": "API health check successful"
                }
            else:
                return {
                    "test": test_name,
                    "status": "❌ FAIL",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Health check returned {response.status_code}"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Connection failed: {str(e)}"
            }
    
    async def test_mcp_resources(self) -> Dict[str, Any]:
        """Test MCP resource endpoints"""
        test_name = "MCP Resources"
        start_time = time.time()
        
        try:
            # Test API status resource
            status_response = await self.mcp.read_resource("heatpump://api-status")
            status = status_response[0].content if status_response else ""
            
            # Test endpoints resource
            endpoints_response = await self.mcp.read_resource("heatpump://endpoints")
            endpoints = endpoints_response[0].content if endpoints_response else ""
            
            elapsed_time = time.time() - start_time
            
            if ("✅" in status or "healthy" in status) and "Available HeatPumpHQ tools" in endpoints:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": "Both resources working correctly"
                }
            else:
                return {
                    "test": test_name,
                    "status": "❌ FAIL",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": "Resource responses invalid"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Resource error: {str(e)}"
            }
    
    async def test_quick_sizer_tool(self) -> Dict[str, Any]:
        """Test Quick Sizer tool with validation"""
        test_name = "Quick Sizer Tool"
        start_time = time.time()
        
        try:
            from server import quick_sizer
            
            # Test with valid NYC ZIP code
            result = quick_sizer(
                zip_code="10001",
                square_feet=2000,
                build_year=2010
            )
            
            elapsed_time = time.time() - start_time
            
            # Validate response structure (updated for new API)
            required_fields = ["climate_zone"]
            expected_fields = ["required_btu", "btu_range_min", "btu_range_max", "recommended_models", "is_multi_zone"]
            
            has_required = all(field in result for field in required_fields)
            has_expected = any(field in result for field in expected_fields)
            
            if has_required and has_expected:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Valid response with {len(result)} fields"
                }
            else:
                return {
                    "test": test_name,
                    "status": "❌ FAIL",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Missing required fields. Got: {list(result.keys())}"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Tool error: {str(e)}"
            }
    
    async def test_bill_estimator_tool(self) -> Dict[str, Any]:
        """Test Bill Estimator tool with validation"""
        test_name = "Bill Estimator Tool"
        start_time = time.time()
        
        try:
            from server import bill_estimator
            
            result = bill_estimator(
                zip_code="10001",
                square_feet=2000,
                build_year=2010,
                heat_pump_model="Mitsubishi MXZ-3C24NA",
                current_heating_fuel="gas"
            )
            
            elapsed_time = time.time() - start_time
            
            # Validate response structure (updated for new API)
            required_fields = ["annual_summary", "monthly_breakdown"]
            expected_fields = ["break_even_year", "total_10yr_savings", "avg_monthly_savings"]
            
            has_required = all(field in result for field in required_fields)
            has_expected = any(field in result for field in expected_fields)
            
            if has_required and has_expected:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Valid response with {len(result)} fields"
                }
            else:
                return {
                    "test": test_name,
                    "status": "❌ FAIL",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Missing required fields. Got: {list(result.keys())}"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Tool error: {str(e)}"
            }
    
    async def test_cold_climate_tool(self) -> Dict[str, Any]:
        """Test Cold Climate tool with validation"""
        test_name = "Cold Climate Tool"
        start_time = time.time()
        
        try:
            from server import cold_climate_check
            
            result = cold_climate_check(
                zip_code="10001",
                square_feet=2000,
                build_year=2010,
                heat_pump_model="Mitsubishi MXZ-3C24NA",
                existing_backup_heat="electric_strip"
            )
            
            elapsed_time = time.time() - start_time
            
            # Validate response structure (updated for new API)
            required_fields = ["performance_analysis", "capacity_curve"]
            expected_fields = ["backup_heat_recommendation", "temperature_range_analysis", "key_findings"]
            
            has_required = all(field in result for field in required_fields)
            has_expected = any(field in result for field in expected_fields)
            
            if has_required and has_expected:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Valid response with {len(result)} fields"
                }
            else:
                return {
                    "test": test_name,
                    "status": "❌ FAIL",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Missing required fields. Got: {list(result.keys())}"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Tool error: {str(e)}"
            }
    
    async def test_project_cost_tool(self) -> Dict[str, Any]:
        """Test Project Cost tool with validation"""
        test_name = "Project Cost Tool"
        start_time = time.time()
        
        try:
            from server import project_cost_estimator
            
            result = project_cost_estimator(
                zip_code="10001",
                square_feet=2000,
                build_year=2010,
                heat_pump_model="Fujitsu AOU24RLXFZ",
                existing_heating_type="gas_furnace",
                ductwork_condition="good",
                home_stories=1,
                insulation_quality="fair",
                air_sealing="poor"
            )
            
            elapsed_time = time.time() - start_time
            
            # Validate response structure (updated for new API)
            required_fields = ["total_cost", "cost_breakdown"]
            expected_fields = ["input_summary", "confidence_level", "financing_options"]
            
            has_required = all(field in result for field in required_fields)
            has_expected = any(field in result for field in expected_fields)
            
            if has_required and has_expected:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Valid response with {len(result)} fields"
                }
            else:
                return {
                    "test": test_name,
                    "status": "❌ FAIL",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Missing required fields. Got: {list(result.keys())}"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Tool error: {str(e)}"
            }
    
    async def test_performance(self) -> Dict[str, Any]:
        """Test performance across all tools"""
        test_name = "Performance Test"
        start_time = time.time()
        
        try:
            # Run all tools and measure total time
            from server import quick_sizer, bill_estimator, cold_climate_check, project_cost_estimator
            
            # Run quick sizer first
            qs_result = quick_sizer("10001", 2000, 2010)
            
            # Use updated parameters for other tools
            be_result = bill_estimator(
                "10001", 
                2000,
                2010,
                "Mitsubishi MXZ-3C24NA",
                "gas"
            )
            
            cc_result = cold_climate_check("10001", 2000, 2010, "Mitsubishi MXZ-3C24NA", "electric_strip")
            pc_result = project_cost_estimator("10001", 2000, 2010, "Fujitsu AOU24RLXFZ", "gas_furnace", "good", 1, "fair", "poor")
            
            elapsed_time = time.time() - start_time
            
            if elapsed_time <= PERFORMANCE_THRESHOLD:
                return {
                    "test": test_name,
                    "status": "✅ PASS",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"All 4 tools completed in {elapsed_time:.2f}s (threshold: {PERFORMANCE_THRESHOLD}s)"
                }
            else:
                return {
                    "test": test_name,
                    "status": "⚠️ SLOW",
                    "response_time": f"{elapsed_time:.2f}s",
                    "details": f"Performance slower than threshold ({PERFORMANCE_THRESHOLD}s)"
                }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                "test": test_name,
                "status": "❌ FAIL",
                "response_time": f"{elapsed_time:.2f}s",
                "details": f"Performance test error: {str(e)}"
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return summary"""
        print(f"🚀 Starting comprehensive E2E test suite...")
        print(f"📡 Testing against: {self.api_base_url}")
        print("=" * 60)
        
        tests = [
            self.test_api_connectivity(),
            self.test_mcp_resources(),
            self.test_quick_sizer_tool(),
            self.test_bill_estimator_tool(),
            self.test_cold_climate_tool(),
            self.test_project_cost_tool(),
            self.test_performance()
        ]
        
        results = []
        for test in tests:
            result = await test
            results.append(result)
            status_emoji = "✅" if "✅" in result["status"] else "⚠️" if "⚠️" in result["status"] else "❌"
            print(f"{status_emoji} {result['test']}: {result['status']} ({result['response_time']})")
            if "❌" in result["status"] or "⚠️" in result["status"]:
                print(f"   Details: {result['details']}")
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = len([r for r in results if "✅" in r["status"]])
        failed_tests = len([r for r in results if "❌" in r["status"]])
        slow_tests = len([r for r in results if "⚠️" in r["status"]])
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "slow": slow_tests,
            "success_rate": f"{(passed_tests/total_tests)*100:.1f}%",
            "api_url": self.api_base_url,
            "results": results
        }
        
        print("\n" + "=" * 60)
        print(f"📊 Test Summary:")
        print(f"   Total: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests} | Slow: {slow_tests}")
        print(f"   Success Rate: {summary['success_rate']}")
        
        if failed_tests == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {failed_tests} test(s) failed - check details above")
        
        return summary


async def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run HeatPumpHQ MCP Server E2E Tests")
    parser.add_argument("--env", choices=["local", "production"], default="production",
                       help="Environment to test against")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    # Run tests
    test_suite = MCPServerTestSuite(args.env)
    results = await test_suite.run_all_tests()
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {args.output}")
    
    # Exit with appropriate code
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())