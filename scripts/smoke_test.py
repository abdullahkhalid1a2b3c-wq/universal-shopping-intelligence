#!/usr/bin/env python3
"""FitSense Production Deployment Smoke Test Suite.

Automated verification of deployed API and Web services:
1. API Health Check (GET /health)
2. Product Lookup by Normalized URL (GET /v1/products/lookup)
3. Guest Recommendation (POST /v1/recommend)
4. Web Frontend Home Status (GET /)
5. CORS Header Verification (OPTIONS preflight matching Web Origin)

Usage:
    python scripts/smoke_test.py --api-url https://fitsense-api.onrender.com --web-url https://fitsense.vercel.app
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple


def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 25,
) -> Tuple[int, Dict[str, str], bytes]:
    """Execute an HTTP request and return (status_code, response_headers, body_bytes)."""
    headers = headers or {}
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_headers = {k.lower(): v for k, v in resp.getheaders()}
            return resp.status, resp_headers, resp.read()
    except urllib.error.HTTPError as exc:
        resp_headers = {k.lower(): v for k, v in exc.headers.items()}
        return exc.code, resp_headers, exc.read()
    except Exception as exc:
        raise RuntimeError(f"Network error connecting to {url}: {exc}") from exc


def run_smoke_tests(api_url: str, web_url: str) -> bool:
    api_url = api_url.rstrip("/")
    web_url = web_url.rstrip("/")

    print("================================================================")
    print("🧪 FitSense Production Smoke Test Suite")
    print(f"Target API : {api_url}")
    print(f"Target Web : {web_url}")
    print("================================================================\n")

    results = []

    # ------------------------------------------------------------------
    # Check 1: API Health
    # ------------------------------------------------------------------
    print("[1/5] Checking API Health (/health)...", end=" ", flush=True)
    t0 = time.time()
    try:
        status, _, body = make_request(f"{api_url}/health")
        duration = round((time.time() - t0) * 1000)
        data = json.loads(body.decode("utf-8")) if body else {}
        if status == 200 and data.get("status") == "ok":
            print(f"PASS ({duration}ms) [version: {data.get('version', 'unknown')}]")
            results.append(("API Health", True, f"HTTP {status} ok ({duration}ms)"))
        else:
            print(f"FAIL (HTTP {status}) - Response: {data}")
            results.append(("API Health", False, f"HTTP {status}"))
    except Exception as exc:
        print(f"ERROR: {exc}")
        results.append(("API Health", False, str(exc)))

    # ------------------------------------------------------------------
    # Check 2: Product Lookup
    # ------------------------------------------------------------------
    test_product_url = "https://outfitters.com.pk/products/classic-tee"
    encoded_url = urllib.parse.quote(test_product_url, safe="")
    print("[2/5] Checking Product Lookup (/v1/products/lookup)...", end=" ", flush=True)
    t0 = time.time()
    try:
        status, _, body = make_request(f"{api_url}/v1/products/lookup?url={encoded_url}")
        duration = round((time.time() - t0) * 1000)
        data = json.loads(body.decode("utf-8")) if body else {}
        if status == 200:
            covered = data.get("covered", False)
            print(f"PASS ({duration}ms) [covered: {covered}]")
            results.append(("Product Lookup", True, f"HTTP 200 covered={covered} ({duration}ms)"))
        else:
            print(f"FAIL (HTTP {status}) - {data}")
            results.append(("Product Lookup", False, f"HTTP {status}"))
    except Exception as exc:
        print(f"ERROR: {exc}")
        results.append(("Product Lookup", False, str(exc)))

    # ------------------------------------------------------------------
    # Check 3: Guest Sizing Recommendation
    # ------------------------------------------------------------------
    print("[3/5] Testing Guest Sizing Recommendation (/v1/recommend)...", end=" ", flush=True)
    t0 = time.time()
    rec_payload = {
        "product_url": "https://outfitters.com.pk/products/classic-tee",
        "chest_cm": 100.0,
        "unit": "cm",
    }
    try:
        status, _, body = make_request(
            f"{api_url}/v1/recommend",
            method="POST",
            data=rec_payload,
        )
        duration = round((time.time() - t0) * 1000)
        data = json.loads(body.decode("utf-8")) if body else {}
        # Returns 200 with recommendation or unmapped product info
        if status == 200 and ("recommended_size" in data or "covered" in data or "status" in data):
            rec_size = data.get("recommended_size", "uncovered/demo")
            print(f"PASS ({duration}ms) [result: {rec_size}]")
            results.append(("Guest Recommendation", True, f"HTTP 200 size={rec_size} ({duration}ms)"))
        else:
            print(f"FAIL (HTTP {status}) - {data}")
            results.append(("Guest Recommendation", False, f"HTTP {status}"))
    except Exception as exc:
        print(f"ERROR: {exc}")
        results.append(("Guest Recommendation", False, str(exc)))

    # ------------------------------------------------------------------
    # Check 4: Web Frontend Home
    # ------------------------------------------------------------------
    print("[4/5] Checking Web Application Home Page...", end=" ", flush=True)
    t0 = time.time()
    try:
        status, _, _ = make_request(f"{web_url}/", method="GET")
        duration = round((time.time() - t0) * 1000)
        if status in (200, 301, 302, 307, 308):
            print(f"PASS ({duration}ms) [HTTP {status}]")
            results.append(("Web Frontend", True, f"HTTP {status} ({duration}ms)"))
        else:
            print(f"FAIL (HTTP {status})")
            results.append(("Web Frontend", False, f"HTTP {status}"))
    except Exception as exc:
        print(f"ERROR: {exc}")
        results.append(("Web Frontend", False, str(exc)))

    # ------------------------------------------------------------------
    # Check 5: CORS Configuration for Web Origin
    # ------------------------------------------------------------------
    print(f"[5/5] Verifying CORS Preflight for Origin '{web_url}'...", end=" ", flush=True)
    t0 = time.time()
    cors_headers = {
        "Origin": web_url,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type",
    }
    try:
        status, resp_headers, _ = make_request(
            f"{api_url}/v1/recommend",
            method="OPTIONS",
            headers=cors_headers,
        )
        duration = round((time.time() - t0) * 1000)
        allow_origin = resp_headers.get("access-control-allow-origin", "")
        origin_allowed = allow_origin == "*" or web_url in allow_origin
        if status in (200, 204) and origin_allowed:
            print(f"PASS ({duration}ms) [Allow-Origin: {allow_origin}]")
            results.append(("CORS Origin", True, f"HTTP {status} allowed={allow_origin} ({duration}ms)"))
        else:
            print(f"FAIL (HTTP {status}) [Allow-Origin header: '{allow_origin}']")
            results.append(("CORS Origin", False, f"HTTP {status} header={allow_origin}"))
    except Exception as exc:
        print(f"ERROR: {exc}")
        results.append(("CORS Origin", False, str(exc)))

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n================================================================")
    print("📊 Smoke Test Results Summary")
    print("================================================================")
    all_passed = True
    for name, passed, detail in results:
        mark = "✓ PASS" if passed else "❌ FAIL"
        print(f"[{mark}] {name:25}: {detail}")
        if not passed:
            all_passed = False

    print("================================================================")
    if all_passed:
        print("🎉 ALL SMOKE TESTS PASSED! Deployment is healthy and operational.")
        return True
    else:
        print("⚠️ ONE OR MORE CHECKS FAILED. Review errors above.")
        return False


def main():
    parser = argparse.ArgumentParser(description="FitSense Production Smoke Test")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--web-url", default="http://localhost:3000", help="Web frontend base URL")
    args = parser.parse_args()

    success = run_smoke_tests(args.api_url, args.web_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

