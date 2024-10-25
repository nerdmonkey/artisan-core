from aws_lambda_powertools.utilities.typing import LambdaContext

from app.services.logger import StandardLogger
from config.app import get_settings

settings = get_settings()

log_level = settings.LOG_LEVEL
logger = StandardLogger(service="sample-service-name", level=log_level)


def main(event: dict, context: LambdaContext):
    context_dict = logger.convert_context_to_dict(context)

    logger.info("Event Handling", extra={"event": event, "context": context_dict})

    logger.append_keys(dump={"firstname": "Dingdong"})

    logger.debug("Debug Data")

    try:
        raise ValueError("Something went wrong")

    except ValueError as e:
        logger.exception(
            "Error Occurred", extra={"event": event, "context": context_dict}
        )

    return {"statusCode": 200}
