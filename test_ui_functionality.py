#!/usr/bin/env python3
"""
UI Functionality Test Script
Tests routes, API endpoints, and other functionality
"""
import os
import sys
import json
import logging
import requests
from urllib.parse import urljoin
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class UITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_route(self, route, expected_status=200, method="GET", data=None):
        """Test if a route is accessible"""
        url = urljoin(self.base_url, route)
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=5)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data if data else {}, timeout=5)

            if response.status_code == expected_status:
                logger.info(f"✅ {method} {route} - Status: {response.status_code}")
                return True
            else:
                logger.error(f"❌ {method} {route} - Expected {expected_status}, got {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ {method} {route} - Error: {str(e)}")
            return False

    def test_major_routes(self):
        """Test main application routes"""
        routes = [
            "/",
            "/login",
            "/dashboard",
            "/patients",
            "/simulations",
            "/notes", 
            "/docs"
        ]

        results = []
        for route in routes:
            results.append(self.test_route(route))
        return results

    def test_static_assets(self):
        """Test if critical static assets are accessible"""
        assets = [
            "/static/css/style.css",
            "/static/js/app.js",
            "/static/js/button-fix.js",
            "/static/images/n1o1-favicon.svg"
        ]

        results = []
        for asset in assets:
            results.append(self.test_route(asset))

        return all(results)

    def test_button_functionality(self):
        """Test button endpoints"""
        api_endpoints = [
            {"route": "/api/patients", "method": "GET"},
            {"route": "/api/simulate", "method": "POST", "data": {"patient_id": 1, "days": 30}},
            {"route": "/api/assistant", "method": "POST", "data": {"query": "test question"}}
        ]

        results = []
        for endpoint in api_endpoints:
            results.append(self.test_route(
                endpoint["route"], 
                method=endpoint["method"], 
                data=endpoint.get("data")
            ))

        return results

def run_tests():
    """Run all UI tests"""
    logger.info("Starting UI functionality tests...")

    # Determine base URL
    base_url = os.environ.get("APP_URL", "http://localhost:5000")
    logger.info(f"Testing against: {base_url}")

    tester = UITester(base_url)

    # Test major application routes
    logger.info("\n--- Testing Major Routes ---")
    route_results = tester.test_major_routes()

    # Test static assets
    logger.info("\n--- Testing Static Assets ---")
    assets_ok = tester.test_static_assets()

    # Test button functionality
    logger.info("\n--- Testing Button Endpoints ---")
    button_results = tester.test_button_functionality()

    # Summary
    total_tests = len(route_results) + 1 + len(button_results)
    passed_tests = sum(1 for r in route_results if r) + (1 if assets_ok else 0) + sum(1 for r in button_results if r)

    logger.info("\n--- Test Summary ---")
    logger.info(f"Total tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")

    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_tests()
    if not success:
        logger.info("\nSome tests failed. See log above for details.")
        logger.info("Consider checking your routes, static files, and API endpoints.")
    else:
        logger.info("\nAll UI tests passed successfully!")