import json

from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter
from aws_lambda_powertools.logging.types import LogRecord
from aws_lambda_powertools.utilities.typing import LambdaContext


class StandardLogger(Logger):
    def __init__(self, service: str, level: str) -> None:
        super().__init__(service=service, level=level)
        self._logger.handlers[0].setFormatter(StandardLogFormatter())

    def convert_context_to_dict(context: LambdaContext) -> dict:
        """
        Convert LambdaContext to a dictionary for logging.
        """
        return {
            "aws_request_id": context.aws_request_id,
            "log_group_name": context.log_group_name,
            "log_stream_name": context.log_stream_name,
            "function_name": context.function_name,
            "memory_limit_in_mb": context.memory_limit_in_mb,
            "function_version": context.function_version,
            "invoked_function_arn": context.invoked_function_arn,
            "remaining_time_in_millis": context.get_remaining_time_in_millis(),
        }


class StandardLogFormatter(LambdaPowertoolsFormatter):
    """
    Custom formatter for StandardLogger, designed to handle LambdaContext.
    """

    def format(self, record: LogRecord) -> str:
        message = record.__dict__.get("msg", "unknown")
        event = record.__dict__.get("event", {})

        context = record.get("context", {})
        context_dict = {}

        if hasattr(context, "aws_request_id"):
            context_dict = {
                "aws_request_id": context.aws_request_id,
                "log_group_name": context.log_group_name,
                "log_stream_name": context.log_stream_name,
                "function_name": context.function_name,
                "memory_limit_in_mb": context.memory_limit_in_mb,
                "function_version": context.function_version,
                "invoked_function_arn": context.invoked_function_arn,
                "client_context": str(context.client_context)
                if context.client_context
                else "None",
                "identity": {
                    "cognito_identity_id": context.identity.cognito_identity_id
                    if context.identity
                    else "None",
                    "cognito_identity_pool_id": context.identity.cognito_identity_pool_id
                    if context.identity
                    else "None",
                },
                "_epoch_deadline_time_in_millis": context.get_remaining_time_in_millis(),
            }
        else:
            context_dict["error"] = "context not available"

        log_record = {
            "level": record.__dict__.get("levelname", "INFO"),
            "message": message,
            "service": record.__dict__.get("name", "unknown"),
            "lambda_function": {
                "name": context_dict.get("function_name", "unknown"),
                "memory_size": context_dict.get("memory_limit_in_mb", "unknown"),
                "version": context_dict.get("function_version", "unknown"),
                "arn": context_dict.get("invoked_function_arn", "unknown"),
                "remaining_time_in_millis": context_dict.get(
                    "_epoch_deadline_time_in_millis", "unknown"
                ),
            },
            "correlation_ids": {
                "request_id": context_dict.get("aws_request_id", "unknown")
            },
            "event": event,
        }

        if record.__dict__.get("levelname", "INFO") != "INFO":
            log_record["error_message"] = record.__dict__.get(
                "error_message", "No error message provided"
            )

        if record.__dict__.get("dump", None):
            log_record["dump"] = record.__dict__.get("dump", {})

        return json.dumps(log_record, indent=2)
