#!/usr/bin/env python3
"""
Test script for TUK-ConvoSearch
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing TUK-ConvoSearch API Endpoints...")
    
    try:
        # Test 1: System Info
        print("\n1. Testing system-info endpoint...")
        response = requests.get(f"{BASE_URL}/api/system-info")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        
        # Test 2: Upload documents
        print("\n2. Testing document upload...")
        response = requests.post(f"{BASE_URL}/api/upload")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Wait for processing
        time.sleep(2)
        
        # Test 3: Sample queries
        print("\n3. Testing sample queries...")
        
        test_queries = [
            "What are the admission requirements for undergraduate programs?",
            "When are the main examinations held?",
            "What is the fee for Computer Science?",
            "How do I pay my fees?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: {query}")
            response = requests.post(
                f"{BASE_URL}/api/query",
                json={"question": query, "user_id": "tester"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {response.status_code}")
                print(f"   Confidence: {data.get('confidence', 0):.2f}")
                print(f"   Answer: {data.get('answer', '')[:100]}...")
            else:
                print(f"   Error: {response.status_code}")
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Is the application running?")
        print("   Run: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()