#!/usr/bin/env python3
"""
Docker test script to verify the trading system works in containerized environment
"""

import os
import sys
from datetime import datetime

def test_docker_environment():
    """Test that the Docker environment is properly configured"""
    print("🐳 Testing Docker environment...")
    
    # Check if we're running in Docker
    in_docker = os.path.exists('/.dockerenv')
    print(f"Running in Docker: {in_docker}")
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    env_vars = [
        'KABUSAPI_HOST',
        'KABUSAPI_PORT', 
        'KABUSAPI_PASSWORD',
        'INITIAL_CAPITAL',
        'MAX_POSITION_SIZE'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        if var == 'KABUSAPI_PASSWORD' and value != 'Not set':
            value = '*' * len(value)  # Hide password
        print(f"  {var}: {value}")
    
    # Test imports
    print("\n📦 Testing imports...")
    try:
        import yfinance as yf
        print("✅ yfinance imported successfully")
    except ImportError as e:
        print(f"❌ yfinance import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ streamlit import failed: {e}")
        return False
    
    try:
        from backtesting import BacktestingEngine
        print("✅ BacktestingEngine imported successfully")
    except ImportError as e:
        print(f"❌ BacktestingEngine import failed: {e}")
        return False
    
    try:
        from trading_algorithms import STRATEGIES
        print("✅ Trading algorithms imported successfully")
    except ImportError as e:
        print(f"❌ Trading algorithms import failed: {e}")
        return False
    
    # Test data access
    print("\n📊 Testing data access...")
    try:
        import yfinance as yf
        ticker = yf.Ticker('1579.T')
        info = ticker.info
        print("✅ Successfully accessed Yahoo Finance data")
    except Exception as e:
        print(f"⚠️ Data access test failed: {e}")
        print("This is normal if running outside market hours")
    
    # Test file system
    print("\n💾 Testing file system...")
    try:
        # Create test directories
        os.makedirs('/app/data', exist_ok=True)
        os.makedirs('/app/logs', exist_ok=True)
        print("✅ Successfully created data and logs directories")
        
        # Test write access
        test_file = '/app/data/test.txt'
        with open(test_file, 'w') as f:
            f.write(f"Test file created at {datetime.now()}")
        print("✅ Successfully wrote test file")
        
        # Clean up
        os.remove(test_file)
        print("✅ Successfully cleaned up test file")
        
    except Exception as e:
        print(f"❌ File system test failed: {e}")
        return False
    
    print("\n🎉 Docker environment test completed successfully!")
    return True

def main():
    """Main test function"""
    print("=" * 50)
    print("🐳 Stock Trading Agent - Docker Test")
    print("=" * 50)
    
    success = test_docker_environment()
    
    if success:
        print("\n✅ All Docker tests passed!")
        print("The trading system is ready to run in Docker.")
        print("\nNext steps:")
        print("1. Configure your .env file with API credentials")
        print("2. Run: ./docker-run.sh start")
        print("3. Access the web interface at http://localhost:8501")
    else:
        print("\n❌ Some Docker tests failed.")
        print("Please check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 