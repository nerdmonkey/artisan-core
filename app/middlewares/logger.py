from app.services.logger import StandardLoggerService

standard_logger = StandardLoggerService()


def standard_logger_middleware(handler):
    def wrapper(event, context):
        standard_logger.info("Incoming event", event=event, context=context)

        response = handler(event, context)

        standard_logger.info("Response", response=response)

        return response

    return wrapper
