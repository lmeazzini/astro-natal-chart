#!/usr/bin/env python3
"""
Quick test script to verify security headers are being added correctly.
Run this after starting the API with the new middleware.
"""

import sys

import requests


def test_security_headers(base_url: str = "http://localhost:8000") -> None:
    """Test if all required security headers are present."""
    print(f"Testing security headers for {base_url}/health...")
    print("-" * 60)

    try:
        response = requests.get(f"{base_url}/health", timeout=5)
    except requests.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        sys.exit(1)

    print(f"Status Code: {response.status_code}")
    print()

    # Expected headers
    expected_headers = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'",  # partial match
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=()",  # partial match
    }

    results = []
    for header, expected_value in expected_headers.items():
        actual_value = response.headers.get(header)

        if actual_value:
            if expected_value in actual_value:
                results.append(f"✅ {header}: {actual_value[:60]}...")
            else:
                results.append(f"⚠️  {header}: {actual_value} (expected to contain '{expected_value}')")
        else:
            results.append(f"❌ {header}: MISSING")

    # HSTS should only be in production
    hsts = response.headers.get("Strict-Transport-Security")
    if hsts:
        results.append(f"✅ Strict-Transport-Security: {hsts} (production mode)")
    else:
        results.append("ℹ️  Strict-Transport-Security: Not set (development mode - OK)")

    for result in results:
        print(result)

    print()
    print("-" * 60)

    # Count results
    passed = sum(1 for r in results if r.startswith("✅"))
    total = len(results)

    print(f"Results: {passed}/{total} headers correct")

    if passed == total:
        print("🎉 All security headers are correctly configured!")
        sys.exit(0)
    else:
        print("⚠️  Some security headers are missing or incorrect.")
        print("\nMake sure you've:")
        print("1. Restarted the API server")
        print("2. Registered SecurityHeadersMiddleware in app/main.py")
        sys.exit(1)


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_security_headers(base_url)
