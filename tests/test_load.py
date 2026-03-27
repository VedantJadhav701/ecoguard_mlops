"""
Load and stress testing for EcoGuard API
"""

import pytest
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
from typing import List

BASE_URL = "http://localhost:8000"

class LoadTestResult:
    """Store load test results"""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.errors = 0
        self.total_requests = 0
    
    def add_response(self, response_time: float, success: bool):
        if success:
            self.response_times.append(response_time)
        else:
            self.errors += 1
        self.total_requests += 1
    
    def report(self):
        if not self.response_times:
            print("No successful requests")
            return
        
        print(f"\n===== Load Test Report =====")
        print(f"Total Requests: {self.total_requests}")
        print(f"Successful: {len(self.response_times)}")
        print(f"Errors: {self.errors}")
        print(f"Success Rate: {len(self.response_times)/self.total_requests*100:.1f}%")
        print(f"Min Latency: {min(self.response_times)*1000:.2f}ms")
        print(f"Max Latency: {max(self.response_times)*1000:.2f}ms")
        print(f"Mean Latency: {statistics.mean(self.response_times)*1000:.2f}ms")
        if len(self.response_times) > 1:
            print(f"Stdev: {statistics.stdev(self.response_times)*1000:.2f}ms")
        print(f"P95 Latency: {sorted(self.response_times)[int(len(self.response_times)*0.95)]*1000:.2f}ms")
        print(f"P99 Latency: {sorted(self.response_times)[int(len(self.response_times)*0.99)]*1000:.2f}ms")

def test_root_endpoint_load():
    """Load test the root endpoint"""
    
    result = LoadTestResult()
    
    def make_request():
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/")
            elapsed = time.time() - start
            result.add_response(elapsed, response.status_code == 200)
        except Exception as e:
            result.add_response(0, False)
    
    # Run 100 concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        for future in as_completed(futures):
            future.result()
    
    result.report()
    assert result.errors < 5  # Allow max 5% error rate

def test_api_concurrent_requests():
    """Test multiple concurrent requests"""
    
    payload = {
        "weight_kg": 0.5,
        "material": "plastic"
    }
    
    result = LoadTestResult()
    
    def make_request():
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/carbon/calculate",
                json=payload
            )
            elapsed = time.time() - start
            result.add_response(elapsed, response.status_code == 200)
        except Exception as e:
            result.add_response(0, False)
    
    # Simulate 50 concurrent users
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(50)]
        for future in as_completed(futures):
            future.result()
    
    result.report()
    # Mean latency should be under 500ms
    if result.response_times:
        assert statistics.mean(result.response_times) < 0.5

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
