from app.helpers.environment import env
from app.services.logging import StandardLoggerService

logger = StandardLoggerService()

logger.info(f"Currently in {env().APP_ENVIRONMENT} environment")
logger.info("Hello, from Spartan")
