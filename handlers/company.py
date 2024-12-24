import logging

from app.helpers.environment import env

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logging.info(f"{env().APP_ENVIRONMENT}")
logging.info("Hello, from Spartan")
