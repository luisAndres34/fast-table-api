import logging
import sys

# Configure the standard format for all logs in the application
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create the logger object that we will import in other files
logger = logging.getLogger("api_boilerplate")
