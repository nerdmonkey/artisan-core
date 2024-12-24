from unittest.mock import patch
import pytest
from app.services.logging import StandardLoggerService

logger = StandardLoggerService()


@pytest.fixture
def mock_env():
    """Fixture to mock the `env` function."""
    class MockEnv:
        APP_ENVIRONMENT = "test"

    with patch("app.helpers.environment.env", return_value=MockEnv()):
        yield MockEnv()


def test_logger_configuration(mock_env, caplog):
    """
    Test if the logger configuration is set correctly and logs
    the expected messages.
    """
    # Trigger logging messages
    with caplog.at_level("INFO"):
        logger.info(f"Currently in {mock_env.APP_ENVIRONMENT} environment")
        logger.info("Hello, from Spartan")

    # Verify captured logs
    assert len(caplog.records) >= 2, "Expected at least two log entries"
    assert caplog.records[0].levelname == "INFO"
    assert "Currently in test environment" in caplog.text
    assert "Hello, from Spartan" in caplog.text
