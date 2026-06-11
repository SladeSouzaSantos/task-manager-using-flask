import logging
import pytest
from todo_project import logger as task_logger

class DummyHandler(logging.Handler):
    """A simple logging handler that stores emitted records in a list."""
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)

# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def dummy_handler(monkeypatch):
    """Replace the existing handlers of ``task_logger`` with a dummy handler.
    The original handlers are restored after the test.
    """
    dummy = DummyHandler()
    # Preserve original handlers to restore later
    original_handlers = list(task_logger.handlers)
    # Clear existing handlers and add dummy
    task_logger.handlers = []
    task_logger.addHandler(dummy)
    yield dummy
    # Restore original handlers
    task_logger.handlers = original_handlers

# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
def test_logger_has_info_level():
    """The logger should be configured with INFO level by default."""
    assert task_logger.level == logging.INFO

def test_logger_emits_message(dummy_handler):
    """When ``logger.info`` is called, the dummy handler should receive a record."""
    test_msg = "Teste de mensagem de log"
    task_logger.info(test_msg)
    # Ensure at least one record was captured
    assert dummy_handler.records, "No log records captured"
    # The last record should contain our message
    last_record = dummy_handler.records[-1]
    assert last_record.getMessage() == test_msg
    assert last_record.levelno == logging.INFO
