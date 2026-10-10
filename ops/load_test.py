#!/usr/bin/env python3
"""Small dependency-free HTTP load smoke test for Phase 70.4."""

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen


def one_request(url: str, timeout: float) -> tuple[int, float]:
    started = time.perf_counter()
    try:
        request = Request(url, method="GET")
        with urlopen(request, timeout=timeout) as response:
            response.read(1024)
            return response.status, time.perf_counter() - started
    except Exception:
        return 599, time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000/api/v1/health")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()

    if args.requests <= 0 or args.concurrency <= 0:
        raise SystemExit("requests and concurrency must be positive")

    started = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [
            executor.submit(one_request, args.url, args.timeout)
            for _ in range(args.requests)
        ]
        for future in as_completed(futures):
            results.append(future.result())

    elapsed = time.perf_counter() - started
    statuses = [status for status, _ in results]
    latencies = [latency for _, latency in results]
    successful = [latency for status, latency in results if 200 <= status < 300]

    print(f"requests={len(results)} elapsed_seconds={elapsed:.3f}")
    print(f"success={len(successful)} errors={len(results)-len(successful)}")
    print(f"requests_per_second={len(results)/elapsed:.2f}")
    if successful:
        print(f"p50_ms={statistics.median(successful)*1000:.2f}")
        print(f"max_ms={max(successful)*1000:.2f}")
    print(f"status_codes={sorted(set(statuses))}")


if __name__ == "__main__":
    main()
