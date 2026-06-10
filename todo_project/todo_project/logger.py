"""Central logging configuration for the Task Manager application.

The logger sends log records to the local syslog service (UDP port 514).
It is used throughout the application to record important events such as
login attempts, user registration, CRUD operations on tasks, and account
updates. The logger is deliberately lightweight – it does not interfere
with the normal Flask request handling.

If a syslog server is not reachable, the handler will silently drop the
message to avoid breaking the application. Adjust the ``address`` tuple
if your syslog daemon listens on a different host/port.
"""

import logging
from logging.handlers import SysLogHandler

logger = logging.getLogger("task_manager")
logger.setLevel(logging.INFO)

syslog_handler = SysLogHandler(address=("localhost", 514))
syslog_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
syslog_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(syslog_handler)

__all__ = ["logger"]