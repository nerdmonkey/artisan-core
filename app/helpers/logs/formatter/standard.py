from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter


class StandardLogFormatter(LambdaPowertoolsFormatter):
    """
    StandardLogFormatter is a custom log formatter that extends the LambdaPowertoolsFormatter.

    This formatter is used to format log records in a standard way by leveraging the
    formatting capabilities of the LambdaPowertoolsFormatter.

    Methods:
        format(record):
            Formats the specified log record as text.
            Args:
                record (logging.LogRecord): The log record to be formatted.
            Returns:
                str: The formatted log record as a string.
    """
    def format(self, record):
        return super().format(record)
