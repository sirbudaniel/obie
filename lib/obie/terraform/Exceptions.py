import logging

from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class TerraformException(Exception):

    def __init__(self, message):
        super().__init__(message)
        logger.error(message)


class TerraformBackendException(Exception):

    def __init__(self, message):
        super().__init__(message)
        logger.error(message)
