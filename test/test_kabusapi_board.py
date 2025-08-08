#!/usr/bin/env python3
"""
Test script to debug KabusAPI board endpoint specifically
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add parent directory to path to import live_trading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from live_trading import KabusAPIClient

# Load environment variables
load_dotenv()

def test_kabusapi_board():
    """Test KabusAPI board endpoint for market prices"""
    
    print("🔍 Testing KabusAPI Board Endpoint")
    print("=" * 50)
    
    # Initialize client
    client = KabusAPIClient()
    
    print(f"🌐 API Base URL: {client.base_url}")
    print(f"🔑 Password configured: {'Yes' if client.password else 'No'}")
    print()
    
    # Step 1: Test authentication
    print("Step 1: Testing authentication...")
    auth_success = client.authenticate()
    
    if not auth_success:
        print("❌ Authentication failed. Cannot test board endpoint.")
        return
    
    print(f"✅ Authentication successful. Token: {client.token[:10] if client.token else 'None'}...")
    print()
    
    # Step 2: Test symbol conversion
    print("Step 2: Testing symbol conversion...")
    test_symbols = ['1579.T', '1360.T']
    
    for symbol in test_symbols:
        api_symbol = client.convert_symbol_to_api_format(symbol)
        print(f"  {symbol} → {api_symbol}")
    print()
    
    # Step 3: Test board endpoint directly
    print("Step 3: Testing board endpoint...")
    
    for symbol in test_symbols:
        print(f"\n📊 Testing board data for {symbol}:")
        api_symbol = client.convert_symbol_to_api_format(symbol)
        
        try:
            url = f"{client.base_url}/board/{api_symbol}"
            headers = client.get_token_header()
            
            print(f"  📡 URL: {url}")
            print(f"  📋 Headers: {headers}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"  📥 Status Code: {response.status_code}")
            print(f"  📥 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  📄 Raw Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Analyze response structure
                print(f"\n  🔍 Response Analysis:")
                print(f"    ResultCode: {result.get('ResultCode')}")
                print(f"    ResultText: {result.get('ResultText')}")
                
                if 'Board' in result:
                    board = result['Board']
                    print(f"    Board keys: {list(board.keys())}")
                    
                    # Look for price fields
                    price_fields = [
                        'CurrentPrice', 'PrevClose', 'Open', 'High', 'Low',
                        'AskPrice', 'BidPrice', 'LastPrice', 'MarketOrderAcceptableTime'
                    ]
                    
                    for field in price_fields:
                        if field in board:
                            print(f"    {field}: {board[field]}")
                else:
                    print("    No 'Board' key found in response")
                    
            else:
                print(f"  ❌ HTTP Error: {response.status_code}")
                print(f"  📄 Error Response: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            import traceback
            print(f"  🔍 Traceback: {traceback.format_exc()}")
    
    # Step 4: Test get_market_price method
    print(f"\n\nStep 4: Testing get_market_price method...")
    
    try:
        prices = client.get_market_price(['1579.T', '1360.T'])
        print(f"✅ Market prices result: {prices}")
        
        for symbol, price in prices.items():
            print(f"  {symbol}: ¥{price:,.2f}")
            
    except Exception as e:
        print(f"❌ get_market_price error: {str(e)}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_kabusapi_board()