#!/usr/bin/env python3
"""
Test script for KabusAPI connection with detailed error reporting
"""

import os
import sys
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test KabusAPI connection with detailed error reporting"""
    
    print("="*60)
    print("🔍 KABUSAPI CONNECTION TEST")
    print("="*60)
    
    # Get configuration
    host = os.getenv('KABUSAPI_HOST', 'localhost')
    port = os.getenv('KABUSAPI_PORT', '18081')
    password = os.getenv('KABUSAPI_PASSWORD', '')
    
    print(f"📋 Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
    
    base_url = f"http://{host}:{port}/kabusapi"
    token_url = f"{base_url}/token"
    
    print(f"\n🔗 Testing connection to: {token_url}")
    
    # Test 1: Basic connectivity
    print(f"\n1️⃣ Testing basic connectivity...")
    try:
        response = requests.get(f"http://{host}:{port}", timeout=5)
        print(f"   ✅ Server is reachable (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - server may not be running")
        print(f"   🔍 Check if KabusAPI is running on {host}:{port}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        return False
    
    # Test 2: API endpoint accessibility
    print(f"\n2️⃣ Testing API endpoint...")
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   ✅ API endpoint accessible (Status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ API endpoint error: {str(e)}")
        return False
    
    # Test 3: Authentication
    print(f"\n3️⃣ Testing authentication...")
    try:
        headers = {'Content-Type': 'application/json'}
        data = {'APIPassword': password}
        
        print(f"   📤 Sending request to: {token_url}")
        print(f"   📋 Request data: {data}")
        
        response = requests.post(token_url, headers=headers, json=data, timeout=10)
        
        print(f"   📡 Response status: {response.status_code}")
        print(f"   📡 Response headers: {dict(response.headers)}")
        
        # Try to read response content
        try:
            response_text = response.text
            print(f"   📡 Response content: {response_text}")
        except Exception as e:
            print(f"   ❌ Error reading response: {str(e)}")
        
        response.raise_for_status()
        
        # Parse JSON response
        try:
            result = response.json()
            print(f"   📊 Parsed response: {result}")
            
            if result.get('ResultCode') == 0:
                token = result.get('Token')
                print(f"   ✅ Authentication successful!")
                print(f"   🔑 Token: {token[:10]}..." if token else "   🔑 Token: None")
                return True
            else:
                error_msg = result.get('ResultText', 'Unknown error')
                print(f"   ❌ Authentication failed: {error_msg}")
                print(f"   ❌ Result code: {result.get('ResultCode')}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON decode error: {str(e)}")
            print(f"   📡 Raw response: {response_text}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {str(e)}")
        print(f"   🔍 Check if KabusAPI is running on {host}:{port}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Timeout error: {str(e)}")
        print(f"   🔍 API server may be slow or unresponsive")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ HTTP error: {str(e)}")
        print(f"   📡 Status code: {e.response.status_code if hasattr(e, 'response') else 'Unknown'}")
        try:
            error_content = e.response.text if hasattr(e, 'response') else 'No content'
            print(f"   📡 Error content: {error_content}")
        except:
            print("   📡 Could not read error content")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {str(e)}")
        print(f"   🔍 Error type: {type(e).__name__}")
        import traceback
        print(f"   🔍 Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Main function"""
    print("🚀 Starting KabusAPI connection test...")
    print("")
    
    success = test_api_connection()
    
    print("\n" + "="*60)
    if success:
        print("🎉 CONNECTION TEST PASSED!")
        print("✅ Your KabusAPI is working correctly")
    else:
        print("❌ CONNECTION TEST FAILED!")
        print("🔧 Please check your configuration and try again")
    print("="*60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 