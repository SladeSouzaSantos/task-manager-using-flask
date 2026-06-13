"""Prometheus metrics integration for the Flask application.

This module defines a simple request counter and exposes a ``/metrics``
endpoint that Prometheus can scrape. It is deliberately lightweight – the
application only needs to import ``register_metrics`` and call it with the
Flask ``app`` instance.

Usage:
    from .metrics import register_metrics
    register_metrics(app)

The ``register_metrics`` function adds a ``before_request`` hook that
increments a ``Counter`` for every HTTP request and registers the ``/metrics``
route which returns the Prometheus exposition format.
"""

from flask import request, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# Counter for total HTTP requests, labelled by method and endpoint path.
# ---------------------------------------------------------------------------
# Core HTTP request metrics (generic)
# ---------------------------------------------------------------------------
REQUEST_COUNT = Counter(
    "flask_http_requests_total",
    "Total number of HTTP requests handled by the Flask app",
    ["method", "endpoint"],
)

# Counter for HTTP status codes per request (useful for error rate monitoring)
REQUEST_STATUS = Counter(
    "flask_http_requests_status_total",
    "HTTP request count labeled by status code",
    ["method", "endpoint", "status"],
)

# Histogram for request latency (seconds)
REQUEST_LATENCY = Histogram(
    "flask_http_request_duration_seconds",
    "Latency of HTTP requests in seconds",
    ["method", "endpoint"],
)

# ---------------------------------------------------------------------------
# Application‑specific business metrics
# ---------------------------------------------------------------------------
USERS_REGISTERED = Counter(
    "users_registered_total",
    "Total number of users that have registered",
)

TASKS_CREATED = Counter(
    "tasks_created_total",
    "Total number of tasks created",
    ["user_id"],
)

TASKS_COMPLETED = Counter(
    "tasks_completed_total",
    "Total number of tasks marked as completed",
    ["user_id"],
)

# Gauge representing the current number of active (not completed) tasks
TASKS_ACTIVE = Gauge(
    "tasks_active",
    "Current number of active tasks",
    ["user_id"],
)

# ---------------------------------------------------------------------------
# Helper to initialise business‑level metrics from the existing database state.
# This function is called once, during application start‑up, after the Flask
# app and the SQLAlchemy ``db`` object have been created.
# ---------------------------------------------------------------------------
def init_business_metrics():
        """Populate counters/gauges with the current contents of the DB.

        * ``users_registered_total`` – incremented once for each user already
            present.
        * ``tasks_created_total`` – incremented once for each task already
            present (so the historical count is reflected).
        * ``tasks_active`` – set to the number of tasks that belong to each user.

        The function imports the models lazily to avoid circular import issues.
        """
        from .models import User, Task
        from collections import defaultdict

        # ---- Users -------------------------------------------------
        existing_users = User.query.count()
        for _ in range(existing_users):
                USERS_REGISTERED.inc()

        # ---- Tasks -------------------------------------------------
        # Build a dict of active task counts per user
        tasks_by_user = defaultdict(int)
        for task in Task.query.all():
                tasks_by_user[task.user_id] += 1
                # Increment the creation counter for each historic task
                TASKS_CREATED.labels(user_id=str(task.user_id)).inc()

        # Populate the gauge with the current active counts
        for user_id, qty in tasks_by_user.items():
                TASKS_ACTIVE.labels(user_id=str(user_id)).set(qty)


def _increment_counter():
    """Increment the request counter for the current request.

    This function is intended to be used as a ``before_request`` handler.
    It also stores the start time for latency measurement.
    """
    REQUEST_COUNT.labels(method=request.method, endpoint=request.path).inc()
    # Store start time on the request object for later latency calculation
    request.start_time = request.environ.get("werkzeug.request_start_time") or request.environ.get("REQUEST_TIME") or None
    # Fallback: use time.time() if not provided by the server
    if request.start_time is None:
        import time

        request.start_time = time.time()


def register_metrics(app):
    """Register Prometheus metrics endpoint and request counter.

    Args:
        app: The Flask application instance.
    """
    # Increment the counter before each request.
    app.before_request(_increment_counter)

    @app.route("/metrics")
    def metrics():  # pragma: no cover – exercised by Prometheus scrapes
        """Expose Prometheus metrics.

        Returns the latest metrics in the text format expected by Prometheus.
        """
        data = generate_latest()
        return Response(data, mimetype=CONTENT_TYPE_LATEST)

    # ---------------------------------------------------------------------
    # After request: record latency and status code
    # ---------------------------------------------------------------------
    @app.after_request
    def _record_metrics(response):
        # Record latency
        import time

        elapsed = time.time() - getattr(request, "start_time", time.time())
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.path).observe(elapsed)
        # Record status code
        REQUEST_STATUS.labels(
            method=request.method,
            endpoint=request.path,
            status=str(response.status_code),
        ).inc()
        return response
