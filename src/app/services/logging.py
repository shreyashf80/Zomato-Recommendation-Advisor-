from __future__ import annotations

import logging
from contextvars import ContextVar

# Global ContextVar to track correlation IDs across threads/async tasks
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="system")


class CorrelationIdFilter(logging.Filter):
    """Logging filter to inject context-scoped correlation ID into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get()
        return True


def setup_logging() -> logging.Logger:
    """Configures and returns the application logger with custom formatting."""
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [CID:%(correlation_id)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationIdFilter())
        app_logger.addHandler(handler)

    return app_logger


# Pre-initialize logger for clean imports
logger = setup_logging()
