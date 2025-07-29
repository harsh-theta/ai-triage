#!/usr/bin/env python3
"""
Debug server deployment issues for AI Triage system
"""

import requests
import sys
import time

def debug_server_issues():
    print("=== Server Deployment Debug ===\n")
    
    # Test configurations
    test_configs = [
        {
            "name": "Local Docker (Port 8010)",
            "base_url": "http://localhost:8010",
            "description": "Testing local Docker containers"
        },
        {
            "name": "Server IP (Port 8010)",
            "base_url": "http://106.201.228.100:8010",
            "description": "Testing server IP with port 8010"
        },
        {
            "name": "Domain (No Port)",
            "base_url": "http://demo.thetatechnolabs.com",
            "description": "Testing domain without port"
        },
        {
            "name": "Domain (Port 80)",
            "base_url": "http://demo.thetatechnolabs.com:80",
            "description": "Testing domain with port 80"
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"🔍 Testing: {config['name']}")
        print(f"   URL: {config['base_url']}")
        print(f"   Description: {config['description']}")
        
        # Test 1: Root path
        print("   1. Testing root path...")
        try:
            response = requests.get(f"{config['base_url']}/", allow_redirects=False, timeout=10)
            print(f"      Status: {response.status_code}")
            if response.status_code == 301:
                location = response.headers.get('Location', '')
                print(f"      Redirect: {location}")
            elif response.status_code == 200:
                print(f"      Content-Type: {response.headers.get('content-type', 'unknown')}")
            results.append((f"{config['name']} - Root", response.status_code, response.headers.get('Location', '')))
        except Exception as e:
            print(f"      Error: {e}")
            results.append((f"{config['name']} - Root", "ERROR", str(e)))
        
        # Test 2: /intelligent-triage
        print("   2. Testing /intelligent-triage...")
        try:
            response = requests.get(f"{config['base_url']}/intelligent-triage", allow_redirects=False, timeout=10)
            print(f"      Status: {response.status_code}")
            if response.status_code == 301:
                location = response.headers.get('Location', '')
                print(f"      Redirect: {location}")
            elif response.status_code == 200:
                print(f"      Content-Type: {response.headers.get('content-type', 'unknown')}")
            results.append((f"{config['name']} - /intelligent-triage", response.status_code, response.headers.get('Location', '')))
        except Exception as e:
            print(f"      Error: {e}")
            results.append((f"{config['name']} - /intelligent-triage", "ERROR", str(e)))
        
        # Test 3: /intelligent-triage/
        print("   3. Testing /intelligent-triage/...")
        try:
            response = requests.get(f"{config['base_url']}/intelligent-triage/", timeout=10)
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                print(f"      Content-Type: {response.headers.get('content-type', 'unknown')}")
                if 'text/html' in response.headers.get('content-type', ''):
                    print(f"      Content Length: {len(response.text)} characters")
            results.append((f"{config['name']} - /intelligent-triage/", response.status_code, ""))
        except Exception as e:
            print(f"      Error: {e}")
            results.append((f"{config['name']} - /intelligent-triage/", "ERROR", str(e)))
        
        # Test 4: Health check
        print("   4. Testing health check...")
        try:
            response = requests.get(f"{config['base_url']}/health", timeout=5)
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                print(f"      Response: {response.text.strip()}")
            results.append((f"{config['name']} - Health", response.status_code, ""))
        except Exception as e:
            print(f"      Error: {e}")
            results.append((f"{config['name']} - Health", "ERROR", str(e)))
        
        print()
    
    # Summary
    print("="*60)
    print("📋 DEBUG SUMMARY")
    print("="*60)
    
    for test_name, status, location in results:
        if status == "ERROR":
            print(f"❌ {test_name}: {location}")
        elif status == 200:
            print(f"✅ {test_name}: {status}")
        elif status == 301:
            print(f"🔄 {test_name}: {status} → {location}")
        else:
            print(f"⚠️  {test_name}: {status}")
    
    print("\n" + "="*60)
    print("🔧 TROUBLESHOOTING RECOMMENDATIONS")
    print("="*60)
    
    print("\n1. **Port 8010 Login Redirect Issue:**")
    print("   - The redirect to login suggests there's authentication middleware")
    print("   - Check if there's a reverse proxy or load balancer in front")
    print("   - Verify Docker containers are running on the server")
    print("   - Check server nginx configuration")
    
    print("\n2. **Too Many Redirects Issue:**")
    print("   - This usually happens when nginx configurations conflict")
    print("   - Check if server nginx is conflicting with container nginx")
    print("   - Verify the server nginx configuration matches the local one")
    print("   - Check for redirect loops in nginx config")
    
    print("\n3. **Debugging Steps:**")
    print("   - SSH into server and check Docker containers: docker ps")
    print("   - Check container logs: docker-compose logs")
    print("   - Check server nginx config: nginx -t")
    print("   - Check server nginx logs: tail -f /var/log/nginx/error.log")
    print("   - Verify ports are open: netstat -tlnp | grep :8010")
    
    print("\n4. **Quick Fixes to Try:**")
    print("   - Restart Docker containers: docker-compose restart")
    print("   - Reload nginx: sudo systemctl reload nginx")
    print("   - Check if port 8010 is blocked by firewall")
    print("   - Verify domain DNS is pointing to correct IP")

if __name__ == "__main__":
    debug_server_issues() 