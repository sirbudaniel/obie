import logging

from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class ObieConfigErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger.error(message)


class ClusterConfigErrorException(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger.error(message)
