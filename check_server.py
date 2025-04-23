
#!/usr/bin/env python
"""
Check if the Flask server is running and responsive
"""
import os
import sys
import time
import requests
import socket

def check_server_running(host='0.0.0.0', port=None, max_retries=5, retry_delay=2):
    """Check if server is running on the specified port"""
    if port is None:
        port = int(os.environ.get('PORT', 5000))
    
    print(f"Checking if server is running on {host}:{port}...")
    
    # Try socket connection
    for i in range(max_retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Server is listening on port {port}")
                break
            else:
                print(f"⏳ Attempt {i+1}/{max_retries}: Server not responding yet")
                time.sleep(retry_delay)
        except Exception as e:
            print(f"⚠️ Socket error: {str(e)}")
            time.sleep(retry_delay)
    else:
        print(f"❌ Server did not respond after {max_retries} attempts")
        return False
    
    # Try HTTP request
    for i in range(max_retries):
        try:
            response = requests.get(f"http://{host}:{port}/ping", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server ping successful: {response.text}")
                return True
            else:
                print(f"⚠️ Server responded with status code {response.status_code}")
                time.sleep(retry_delay)
        except requests.RequestException as e:
            print(f"⏳ Attempt {i+1}/{max_retries}: HTTP request failed: {str(e)}")
            time.sleep(retry_delay)
    
    print("❌ Server is not responding to HTTP requests")
    return False

if __name__ == "__main__":
    # Get port from command line or environment
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get('PORT', 5000))
    
    if check_server_running(port=port):
        print("✅ Server is up and running!")
        sys.exit(0)
    else:
        print("❌ Server check failed")
        sys.exit(1)
