#!/usr/bin/env python3
"""
Post-deployment verification script
Tests the deployed application to ensure everything works correctly
"""

import requests
import sys
import time
from urllib.parse import urljoin

def test_url_accessibility(base_url):
    """Test if the application is accessible"""
    print(f"🌐 Testing URL accessibility: {base_url}")
    
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Application is accessible")
            return True
        else:
            print(f"❌ Application returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect: {e}")
        return False

def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    print(f"\n❤️ Testing health endpoint...")
    
    health_url = urljoin(base_url, '/health')
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  NLP loaded: {data.get('nlp_loaded', False)}")
            print(f"  Vectorizer loaded: {data.get('vectorizer_loaded', False)}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_dashboard_page(base_url):
    """Test if the dashboard page loads"""
    print(f"\n📊 Testing dashboard page...")
    
    dashboard_url = urljoin(base_url, '/dashboard')
    try:
        response = requests.get(dashboard_url, timeout=10)
        if response.status_code == 200:
            content = response.text
            if 'HR Dashboard' in content and 'Job description' in content:
                print("✅ Dashboard page loads correctly")
                return True
            else:
                print("❌ Dashboard page content seems incorrect")
                return False
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard page error: {e}")
        return False

def test_static_files(base_url):
    """Test if static files are served correctly"""
    print(f"\n🎨 Testing static files...")
    
    css_url = urljoin(base_url, '/static/styles.css')
    try:
        response = requests.get(css_url, timeout=10)
        if response.status_code == 200:
            print("✅ CSS files loading correctly")
            return True
        else:
            print(f"⚠️ CSS files may not be loading: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Static files test failed: {e}")
        return False

def test_api_endpoints(base_url):
    """Test API endpoints (without actual file upload)"""
    print(f"\n🔌 Testing API endpoints...")
    
    # Test analytics endpoint with empty request (should return error but not crash)
    analytics_url = urljoin(base_url, '/api/analytics')
    try:
        response = requests.post(analytics_url, data={}, timeout=10)
        # We expect this to fail with 400 (missing job description)
        if response.status_code == 400:
            print("✅ Analytics endpoint responding correctly")
            return True
        else:
            print(f"⚠️ Analytics endpoint unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analytics endpoint error: {e}")
        return False

def performance_test(base_url):
    """Basic performance test"""
    print(f"\n⚡ Running performance test...")
    
    start_time = time.time()
    try:
        response = requests.get(base_url, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"  Response time: {response_time:.2f} seconds")
        
        if response_time < 5:
            print("✅ Good response time")
            return True
        elif response_time < 10:
            print("⚠️ Acceptable response time")
            return True
        else:
            print("❌ Slow response time")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def generate_test_report(results, base_url):
    """Generate a test report"""
    print(f"\n📋 Deployment Verification Report")
    print("=" * 50)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"Application URL: {base_url}")
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 All tests passed! Your deployment is working perfectly!")
        print(f"\n🚀 Ready to use:")
        print(f"  • Main app: {base_url}")
        print(f"  • HR Dashboard: {urljoin(base_url, '/dashboard')}")
        print(f"  • Health check: {urljoin(base_url, '/health')}")
    else:
        print(f"\n⚠️ Some tests failed. Check the issues above.")
        print(f"Common solutions:")
        print(f"  • Wait a few minutes for the app to fully start")
        print(f"  • Check environment variables are set correctly")
        print(f"  • Verify the deployment completed successfully")
    
    return passed_tests == total_tests

def main():
    """Main verification function"""
    print("🧪 Automated Resume Screener - Deployment Verification")
    print("=" * 60)
    
    # Get URL from user
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = input("Enter your deployed application URL: ").strip()
    
    # Ensure URL has protocol
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    print(f"\n🎯 Testing deployment at: {base_url}")
    print("This may take a minute...\n")
    
    # Run all tests
    results = {}
    
    results['URL Accessibility'] = test_url_accessibility(base_url)
    results['Health Endpoint'] = test_health_endpoint(base_url)
    results['Dashboard Page'] = test_dashboard_page(base_url)
    results['Static Files'] = test_static_files(base_url)
    results['API Endpoints'] = test_api_endpoints(base_url)
    results['Performance'] = performance_test(base_url)
    
    # Generate report
    success = generate_test_report(results, base_url)
    
    # Additional recommendations
    print(f"\n💡 Next Steps:")
    if success:
        print("1. Share the URL with your HR team")
        print("2. Test with real resumes and job descriptions")
        print("3. Set up monitoring (optional)")
        print("4. Consider custom domain (optional)")
    else:
        print("1. Check deployment logs for errors")
        print("2. Verify environment variables")
        print("3. Wait for deployment to complete")
        print("4. Re-run this test: python verify_deployment.py <url>")
    
    print(f"\n📚 Documentation:")
    print("• FREE_DEPLOYMENT_GUIDE.md - Deployment instructions")
    print("• DEPLOYMENT.md - Advanced deployment options")
    print("• README.md - Complete project documentation")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)