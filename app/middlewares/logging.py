from app.services.logging import StandardLoggerService


def standard_logging_middleware(handler, logger=None):
    """
    Middleware for standard logging of AWS Lambda function input and output data.

    Args:
        handler (function): The AWS Lambda function handler to be wrapped.
        logger (object, optional): Logger instance to be used for logging. Defaults to StandardLoggerService().

    Returns:
        function: Wrapped handler function with logging.

    The wrapped handler logs the following information:
        - Input data size and details.
        - Lambda function metadata (name, version, ARN, memory size, AWS request ID).
        - Output data size and details.
        - Any exceptions raised during the execution of the handler.
    """
    logger = logger or StandardLoggerService()

    def wrapped_handler(event, context):
        try:
            input_data_size = len(str(event).encode("utf-8"))
            lambda_function = {
                "name": context.function_name,
                "version": context.function_version,
                "arn": context.invoked_function_arn,
                "memory_size": context.memory_limit_in_mb,
                "aws_request_id": context.aws_request_id,
            }
            logger.info(
                "Input Data",
                input_data=event,
                lambda_function=lambda_function,
                input_data_size=input_data_size,
            )

            response = handler(event, context)

            output_data_size = len(str(response).encode("utf-8"))
            logger.info(
                "Output Data",
                output_data=response,
                output_data_size=output_data_size,
            )
            return response

        except Exception as e:
            logger.error("Error in Lambda function", error=str(e))
            raise

    return wrapped_handler


def task_logging_middleware(handler, logger=None):
    """
    Middleware to log input and output data sizes for a given task handler.

    Args:
        handler (callable): The task handler function to be wrapped.
        logger (Optional[Logger]): Logger instance to use for logging. If not provided, a default StandardLoggerService will be used.

    Returns:
        callable: Wrapped handler function with logging.

    Logs:
        - Input data size before calling the handler.
        - Output data size after calling the handler.
        - Any exceptions raised by the handler.
    """
    logger = logger or StandardLoggerService()

    def wrapped_handler(**kwargs):
        try:
            input_data_size = len(str(**kwargs).encode("utf-8"))
            input_data = {
                "input_data_size": input_data_size,
            }

            logger.info("Input Data", input_data=input_data)

            response = handler(**kwargs)

            output_data_size = len(str(response).encode("utf-8"))
            logger.info(
                "Output Data",
                output_data=response,
                output_data_size=output_data_size,
            )
            return response

        except Exception as e:
            logger.error("Error in Task function", error=str(e))
            raise

    return wrapped_handler
