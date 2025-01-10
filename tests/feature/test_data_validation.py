import pytest
from unittest.mock import patch
from handlers.data_validation import main

@patch('handlers.data_validation.env')
@patch('handlers.data_validation.logger')
def test_main(mock_logger, mock_env):
    mock_env().APP_ENVIRONMENT = 'test'
    result = main()
    mock_logger.info.assert_any_call('Currently in test environment')
    mock_logger.info.assert_any_call("Hello, from Spartan")

    assert (
        mock_logger.info.call_count == 2
    ), "Unexpected number of logger.info calls."

    assert result["status_code"] == 200, "Unexpected status code."

@patch('handlers.data_validation.env')
@patch('handlers.data_validation.logger')
def test_main_different_environment(mock_logger, mock_env):
    mock_env().APP_ENVIRONMENT = 'production'
    result = main()
    mock_logger.info.assert_any_call('Currently in production environment')
    mock_logger.info.assert_any_call("Hello, from Spartan")

    assert (
        mock_logger.info.call_count == 2
    ), "Unexpected number of logger.info calls."

    assert result["status_code"] == 200, "Unexpected status code."
