import json
import logging
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON for centralized logging."""
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "status_code"):
            log_obj["status_code"] = record.status_code
        if hasattr(record, "method"):
            log_obj["method"] = record.method
        if hasattr(record, "path"):
            log_obj["path"] = record.path
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    app.logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for h in list(app.logger.handlers):
        app.logger.removeHandler(h)
    app.logger.addHandler(handler)
    
    # Mute noisy internal loggers in production
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
