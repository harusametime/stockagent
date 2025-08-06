#!/usr/bin/env python3
"""
Test network connectivity from container to host
"""

import os
import requests
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_network_connectivity():
    """Test network connectivity to host services"""
    
    print("="*60)
    print("🌐 NETWORK CONNECTIVITY TEST")
    print("="*60)
    
    # Get configuration
    host = os.getenv('KABUSAPI_HOST', 'host.docker.internal')
    port = os.getenv('KABUSAPI_PORT', '18081')
    
    print(f"📋 Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    
    # Test 1: DNS resolution
    print(f"\n1️⃣ Testing DNS resolution...")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✅ DNS resolution successful: {host} → {ip}")
    except socket.gaierror as e:
        print(f"   ❌ DNS resolution failed: {str(e)}")
        return False
    
    # Test 2: TCP connection
    print(f"\n2️⃣ Testing TCP connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        
        if result == 0:
            print(f"   ✅ TCP connection successful: {host}:{port}")
        else:
            print(f"   ❌ TCP connection failed: {host}:{port}")
            print(f"   🔍 Error code: {result}")
            return False
    except Exception as e:
        print(f"   ❌ TCP connection error: {str(e)}")
        return False
    
    # Test 3: HTTP connection
    print(f"\n3️⃣ Testing HTTP connection...")
    try:
        url = f"http://{host}:{port}"
        response = requests.get(url, timeout=5)
        print(f"   ✅ HTTP connection successful: {url}")
        print(f"   📡 Status code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ HTTP connection failed: {str(e)}")
        print(f"   🔍 Check if KabusAPI is running on {host}:{port}")
        return False
    except Exception as e:
        print(f"   ❌ HTTP connection error: {str(e)}")
        return False

def test_api_endpoints():
    """Test specific API endpoints"""
    
    print(f"\n4️⃣ Testing API endpoints...")
    
    host = os.getenv('KABUSAPI_HOST', 'host.docker.internal')
    port = os.getenv('KABUSAPI_PORT', '18081')
    base_url = f"http://{host}:{port}/kabusapi"
    
    # Test API base endpoint
    try:
        response = requests.get(base_url, timeout=5)
        print(f"   ✅ API base endpoint accessible: {base_url}")
        print(f"   📡 Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API base endpoint error: {str(e)}")
        return False
    
    # Test token endpoint (without authentication)
    try:
        token_url = f"{base_url}/token"
        response = requests.post(token_url, 
                               json={'APIPassword': 'test'}, 
                               timeout=5)
        print(f"   ✅ Token endpoint accessible: {token_url}")
        print(f"   📡 Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"   ❌ Token endpoint error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting network connectivity test...")
    print("")
    
    # Test basic connectivity
    connectivity_ok = test_network_connectivity()
    
    if connectivity_ok:
        # Test API endpoints
        api_ok = test_api_endpoints()
        
        print("\n" + "="*60)
        if api_ok:
            print("🎉 NETWORK TEST PASSED!")
            print("✅ Container can reach host services")
            print("✅ API endpoints are accessible")
        else:
            print("⚠️ NETWORK TEST PARTIAL!")
            print("✅ Basic connectivity works")
            print("❌ API endpoints may have issues")
    else:
        print("\n" + "="*60)
        print("❌ NETWORK TEST FAILED!")
        print("🔧 Please check Docker networking configuration")
    
    print("="*60)

if __name__ == "__main__":
    main() 