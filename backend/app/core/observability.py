import threading
import time
from collections import defaultdict


_LOCK = threading.Lock()
_REQUEST_COUNT = defaultdict(int)
_REQUEST_LATENCY_SECONDS = defaultdict(float)
_ERROR_COUNT = defaultdict(int)


def observe_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    # Callers should pass route templates (for example `/risks/{risk_id}`),
    # never raw identifier-bearing paths, to avoid high-cardinality metrics.
    key = (method.upper(), path)
    with _LOCK:
        _REQUEST_COUNT[key] += 1
        _REQUEST_LATENCY_SECONDS[key] += duration_seconds
        if status_code >= 500:
            _ERROR_COUNT[key] += 1


def observe_error(method: str, path: str) -> None:
    key = (method.upper(), path)
    with _LOCK:
        _ERROR_COUNT[key] += 1


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def prometheus_text() -> str:
    lines = [
        "# HELP cybergrc_http_requests_total Total HTTP requests.",
        "# TYPE cybergrc_http_requests_total counter",
    ]
    with _LOCK:
        for (method, path), count in sorted(_REQUEST_COUNT.items()):
            labels = f'method="{_escape(method)}",path="{_escape(path)}"'
            lines.append(f"cybergrc_http_requests_total{{{labels}}} {count}")

        lines.extend([
            "# HELP cybergrc_http_request_duration_seconds_total Total observed request duration in seconds.",
            "# TYPE cybergrc_http_request_duration_seconds_total counter",
        ])
        for (method, path), total in sorted(_REQUEST_LATENCY_SECONDS.items()):
            labels = f'method="{_escape(method)}",path="{_escape(path)}"'
            lines.append(f"cybergrc_http_request_duration_seconds_total{{{labels}}} {total:.6f}")

        lines.extend([
            "# HELP cybergrc_http_errors_total Total HTTP 5xx responses.",
            "# TYPE cybergrc_http_errors_total counter",
        ])
        for (method, path), count in sorted(_ERROR_COUNT.items()):
            labels = f'method="{_escape(method)}",path="{_escape(path)}"'
            lines.append(f"cybergrc_http_errors_total{{{labels}}} {count}")

    lines.append(f"cybergrc_metrics_generated_at {time.time():.6f}")
    return "\n".join(lines) + "\n"
