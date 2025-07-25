#!/usr/bin/env python3
"""
Test script for the HeatPumpHQ MCP Server

This script tests the MCP server functionality by calling the tools directly.
Useful for development and debugging.
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import mcp, API_BASE_URL

load_dotenv()

async def test_tools():
    """Test all MCP tools with sample data"""
    
    print(f"🔧 Testing HeatPumpHQ MCP Server")
    print(f"📡 API Base URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Test API status resource
    print("\n📊 Testing API Status Resource...")
    try:
        from server import get_api_status
        status = get_api_status()
        print(f"✅ Status: {status}")
    except Exception as e:
        print(f"❌ API Status Error: {e}")
    
    # Test endpoints resource
    print("\n📋 Testing Endpoints Resource...")
    try:
        from server import get_available_endpoints
        endpoints = get_available_endpoints()
        print(f"✅ Endpoints: {endpoints}")
    except Exception as e:
        print(f"❌ Endpoints Error: {e}")
    
    # Test Quick Sizer tool
    print("\n🏠 Testing Quick Sizer Tool...")
    try:
        result = await test_quick_sizer()
        print(f"✅ Quick Sizer Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Quick Sizer Error: {e}")
    
    # Test Bill Estimator tool (requires Quick Sizer results)
    print("\n💰 Testing Bill Estimator Tool...")
    try:
        result = await test_bill_estimator()
        print(f"✅ Bill Estimator Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Bill Estimator Error: {e}")
    
    # Test Cold Climate Checker tool
    print("\n❄️ Testing Cold Climate Checker Tool...")
    try:
        result = await test_cold_climate()
        print(f"✅ Cold Climate Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Cold Climate Error: {e}")
    
    # Test Project Cost Estimator tool
    print("\n🔧 Testing Project Cost Estimator Tool...")
    try:
        result = await test_project_cost()
        print(f"✅ Project Cost Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Project Cost Error: {e}")

async def test_quick_sizer():
    """Test the quick_sizer tool"""
    from server import quick_sizer
    return quick_sizer(
        zip_code="02101",
        square_feet=2000,
        build_year=2010
    )

async def test_bill_estimator():
    """Test the bill_estimator tool"""
    from server import bill_estimator
    return bill_estimator(
        zip_code="02101",
        square_feet=2000,
        build_year=2010,
        heat_pump_model="Mitsubishi MXZ-3C24NA",
        current_heating_fuel="gas"
    )

async def test_cold_climate():
    """Test the cold_climate_check tool"""
    from server import cold_climate_check
    return cold_climate_check(
        zip_code="02101",
        square_feet=2000,
        build_year=2010,
        heat_pump_model="Mitsubishi MXZ-3C24NA",
        existing_backup_heat="electric_strip"
    )

async def test_project_cost():
    """Test the project_cost_estimator tool"""
    from server import project_cost_estimator
    return project_cost_estimator(
        zip_code="02101",
        square_feet=2000,
        build_year=2010,
        heat_pump_model="Fujitsu AOU24RLXFZ",
        existing_heating_type="gas_furnace",
        ductwork_condition="good",
        home_stories=2,
        insulation_quality="good",
        air_sealing="good"
    )

if __name__ == "__main__":
    print("🚀 Starting HeatPumpHQ MCP Server Tests...")
    print("⚠️  Make sure the HeatPumpHQ backend API is running!")
    print("   Backend should be at:", API_BASE_URL)
    print()
    
    # Run the tests
    asyncio.run(test_tools())
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("\n💡 Next steps:")
    print("   1. Fix any failing tests")
    print("   2. Install in Claude Desktop: uv run mcp install server.py")
    print("   3. Start using the tools in Claude conversations")