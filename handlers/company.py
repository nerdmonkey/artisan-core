from app.services.logging import Logger
from app.helpers.environment import env

logger = Logger()

logger.info(f"Currently in {env().APP_ENVIRONMENT} environment")
logger.info("Hello, from Spartan")
