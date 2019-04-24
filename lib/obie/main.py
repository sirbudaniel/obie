import logging

from obie.parser.RootParser import RootParser
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


def run():

    logger.info('This is the main entry point!')
    parser = RootParser()

    args = parser.get_arguments()

    logger.info(args)
    args.runfunc(args)
