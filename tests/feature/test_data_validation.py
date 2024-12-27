from unittest.mock import MagicMock, patch

import pytest

from handlers.data_validation import main


@pytest.fixture
def mock_env():
    """
    Fixture to mock the `env` function.
    """
    with patch("handlers.data_validation.env") as mock_env_function:
        mock_env_instance = MagicMock()
        mock_env_instance.APP_ENVIRONMENT = "test"
        mock_env_function.return_value = mock_env_instance
        yield mock_env_function


@pytest.fixture
def mock_logger():
    """
    Fixture to mock the `StandardLoggerService`.
    """
    with patch(
        "handlers.data_validation.StandardLoggerService", autospec=True
    ) as mock_logger_class:
        mock_logger_instance = mock_logger_class.return_value
        yield mock_logger_instance


def test_main(mock_env, mock_logger):
    """
    Test the `main` function to ensure it logs the correct information and returns the expected output.
    """
    result = main()

    mock_env.assert_called_once()

    mock_logger.info.assert_any_call("Currently in test environment")
    mock_logger.info.assert_any_call("Hello, from Spartan")

    assert (
        mock_logger.info.call_count == 2
    ), "Unexpected number of logger.info calls."

    assert "logger" in result, "Return value does not contain 'logger'."
    assert (
        result["logger"] == mock_logger
    ), "Returned logger does not match the mocked logger."


def test_main_different_environment():
    """
    Test the `main` function with a different environment.
    """
    with patch("handlers.data_validation.env") as mock_env_function:
        mock_env_instance = MagicMock()
        mock_env_instance.APP_ENVIRONMENT = "production"
        mock_env_function.return_value = mock_env_instance

        with patch(
            "handlers.data_validation.StandardLoggerService", autospec=True
        ) as mock_logger_class:
            mock_logger_instance = mock_logger_class.return_value

            result = main()

            mock_env_function.assert_called_once()

            mock_logger_instance.info.assert_any_call(
                "Currently in production environment"
            )
            mock_logger_instance.info.assert_any_call("Hello, from Spartan")

            assert (
                mock_logger_instance.info.call_count == 2
            ), "Unexpected number of logger.info calls."

            assert "logger" in result, "Return value does not contain 'logger'."
            assert (
                result["logger"] == mock_logger_instance
            ), "Returned logger does not match the mocked logger."
