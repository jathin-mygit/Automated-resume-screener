#!/usr/bin/env python3
"""
Quick health check test for Railway deployment
"""

import requests
import sys
import time

def test_health_endpoint(url):
    """Test the health endpoint"""
    print(f"🏥 Testing health endpoint: {url}/health")
    
    try:
        start_time = time.time()
        response = requests.get(f"{url}/health", timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"Response time: {response_time:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"Status: {data.get('status')}")
            print(f"NLP loaded: {data.get('nlp_loaded')}")
            print(f"Vectorizer loaded: {data.get('vectorizer_loaded')}")
            print(f"Config: {data.get('config')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Health check timed out (>30 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the application")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_health.py <your-railway-url>")
        print("Example: python test_health.py https://your-app.up.railway.app")
        sys.exit(1)
    
    url = sys.argv[1].rstrip('/')
    
    print("🚂 Railway Health Check Test")
    print("=" * 40)
    
    success = test_health_endpoint(url)
    
    if success:
        print("\n🎉 Your Railway deployment is working!")
        print(f"✅ App URL: {url}")
        print(f"✅ Dashboard: {url}/dashboard")
    else:
        print("\n❌ Health check failed. Try these steps:")
        print("1. Wait 2-3 minutes for the app to fully start")
        print("2. Check Railway deployment logs")
        print("3. Verify environment variables are set")
        print("4. See RAILWAY_TROUBLESHOOTING.md for detailed help")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)