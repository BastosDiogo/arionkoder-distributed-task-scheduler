import logging

class Logging():
    """Class with base configuration logs."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def info(self, message:str):
        """Message for informations"""
        logging.info(message)

    def error(self, message:str):
        """Message for errors"""
        logging.error(message)

    def warning(self, message:str):
        """Message for warning"""
        logging.warning(message)