import time
from flask import Response, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Prometheus Metrics Definitions
HTTP_REQUESTS_TOTAL = Counter(
    "notes_http_requests_total",
    "Total HTTP requests received by the Notes application",
    ["method", "endpoint", "status"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "notes_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

TOTAL_NOTES_GAUGE = Gauge(
    "notes_app_total_notes",
    "Current total number of notes in the system"
)

TOTAL_USERS_GAUGE = Gauge(
    "notes_app_total_users",
    "Current total number of registered users"
)

def register_metrics(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        if request.path != "/metrics":
            duration = time.time() - getattr(request, "start_time", time.time())
            endpoint = request.endpoint or "unknown"
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(
                endpoint=endpoint
            ).observe(duration)
        return response

    @app.route("/metrics")
    def metrics():
        """Prometheus metrics scrape endpoint."""
        from app.models import Note, User
        try:
            TOTAL_NOTES_GAUGE.set(Note.query.count())
            TOTAL_USERS_GAUGE.set(User.query.count())
        except Exception:
            pass
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
