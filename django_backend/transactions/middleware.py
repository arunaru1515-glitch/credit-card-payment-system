import time
import logging
from .models import APIMetricLog
from .fraud_service import extract_request_metadata

logger = logging.getLogger("system.monitoring")


class SystemMonitoringMiddleware:
    """
    Middleware that records:
    - API response time
    - Request method, endpoint, status code
    - User (if authenticated) and IP address
    - Errors and failure logging
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        error_message = None

        response = self.get_response(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Only monitor /api/ endpoints to avoid cluttering static/admin requests
        if request.path.startswith("/api/"):
            try:
                meta = extract_request_metadata(request)
                user = request.user if getattr(request, "user", None) and request.user.is_authenticated else None

                if response.status_code >= 400:
                    if hasattr(response, "data") and isinstance(response.data, dict):
                        error_message = str(response.data.get("error") or response.data.get("detail") or response.data)
                    else:
                        error_message = f"HTTP {response.status_code}"

                # Persist metric log
                APIMetricLog.objects.create(
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=duration_ms,
                    user=user,
                    ip_address=meta.get("ip_address"),
                    error_message=error_message,
                )

                # Logger info / warn
                if response.status_code >= 500:
                    logger.error(
                        f"[{request.method}] {request.path} {response.status_code} in {duration_ms}ms - Error: {error_message}"
                    )
                elif response.status_code >= 400:
                    logger.warning(
                        f"[{request.method}] {request.path} {response.status_code} in {duration_ms}ms - Client error: {error_message}"
                    )
                else:
                    logger.info(
                        f"[{request.method}] {request.path} {response.status_code} in {duration_ms}ms"
                    )

            except Exception as e:
                # Middleware must never disrupt response delivery
                logger.debug(f"Monitoring metric recording failed: {e}")

        # Add custom headers for monitoring inspection
        response["X-Response-Time-Ms"] = str(duration_ms)
        return response

    def process_exception(self, request, exception):
        logger.exception(
            f"Unhandled exception on {request.method} {request.path}: {str(exception)}"
        )
        return None
