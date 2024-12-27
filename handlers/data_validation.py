from app.helpers.environment import env
from app.services.logging import StandardLoggerService


def main():
    logger = StandardLoggerService()
    logger.info(f"Currently in {env().APP_ENVIRONMENT} environment")
    logger.info("Hello, from Spartan")

    return {
        "logger": logger,
    }


if __name__ == "__main__":
    main()
