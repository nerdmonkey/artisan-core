from app.helpers.environment import env
from app.services.logging import StandardLoggerService

logger = StandardLoggerService()


def main():
    logger.info(f"Currently in {env().APP_ENVIRONMENT} environment")
    logger.info("Hello, from Spartan")

    return {
        "status_code": 200,
    }


if __name__ == "__main__":
    result = main()

    logger.info("response", result=result)
