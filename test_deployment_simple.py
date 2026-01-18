#!/usr/bin/env python3
"""
Simple deployment test - checks if the app is working
"""

import requests
import sys
import time

def test_deployment(url):
    """Test basic deployment functionality"""
    url = url.rstrip('/')
    
    print(f"🧪 Testing deployment: {url}")
    print("=" * 50)
    
    tests = [
        ("Basic connectivity", f"{url}/"),
        ("Health check", f"{url}/health"),
        ("Dashboard", f"{url}/dashboard")
    ]
    
    results = []
    
    for test_name, test_url in tests:
        print(f"Testing {test_name}...")
        try:
            start_time = time.time()
            response = requests.get(test_url, timeout=30)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"  ✅ {test_name}: OK ({response_time:.2f}s)")
                results.append(True)
            else:
                print(f"  ❌ {test_name}: HTTP {response.status_code}")
                results.append(False)
                
        except requests.exceptions.Timeout:
            print(f"  ❌ {test_name}: Timeout (>30s)")
            results.append(False)
        except requests.exceptions.ConnectionError:
            print(f"  ❌ {test_name}: Connection failed")
            results.append(False)
        except Exception as e:
            print(f"  ❌ {test_name}: Error - {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("🎉 All tests passed! Your deployment is working!")
        print(f"✅ App URL: {url}")
        print(f"✅ Dashboard: {url}/dashboard")
        return True
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count}/{len(results)} tests failed")
        print("\n🔧 Troubleshooting:")
        print("1. Wait 2-3 minutes for app to fully start")
        print("2. Check deployment logs in Railway/Render")
        print("3. Verify environment variables are set")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_deployment_simple.py <your-app-url>")
        print("Example: python test_deployment_simple.py https://your-app.up.railway.app")
        sys.exit(1)
    
    url = sys.argv[1]
    success = test_deployment(url)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()