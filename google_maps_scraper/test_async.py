#!/usr/bin/env python3
"""
Test script for async scraping functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_async_endpoint(base_url="http://localhost:5000"):
    """Test the async scraping endpoint"""
    
    print("🧪 Testing Async Scraping Endpoint")
    print("=" * 50)
    
    # Test data
    test_job = {
        "job_id": 999,
        "area_id": 1,
        "area_name": "Test Area, Test City, Test Country",
        "keyword": "restaurant",
        "search_term": "restaurant",
        "completion_webhook": "https://webhook.site/test",  # Use webhook.site for testing
        "max_results": 10
    }
    
    print(f"\n📤 Sending test job request:")
    print(json.dumps(test_job, indent=2))
    
    try:
        # Send async job request
        response = requests.post(
            f"{base_url}/scrape-job-async",
            json=test_job,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ Async job started successfully!")
            print("Check your webhook URL for completion notification")
            print("Note: The job will run in the background")
        else:
            print("\n❌ Failed to start async job")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
def test_health_check(base_url="http://localhost:5000"):
    """Test the health check endpoint"""
    
    print("\n🏥 Testing Health Check Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"\n📥 Response Status: {response.status_code}")
        print(f"📥 Response Body:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

def main():
    """Main test function"""
    
    print("🚀 Google Maps Scraper Async Test")
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    print(f"🌐 Testing server at: {base_url}")
    
    # Run tests
    test_health_check(base_url)
    time.sleep(1)
    test_async_endpoint(base_url)
    
    print("\n" + "=" * 50)
    print("✅ Tests completed!")
    print("\n💡 Tips:")
    print("1. Check server logs for processing details")
    print("2. Visit webhook.site to create a test webhook URL")
    print("3. Monitor Supabase for job status updates")
    print("4. Check businesses table for inserted records")

if __name__ == "__main__":
    main()