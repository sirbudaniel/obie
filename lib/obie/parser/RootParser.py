import logging
import argparse

from obie.parser.ConfigureSubParsers import ConfigureSubParsers
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class RootParser:

    available_subparsers = ['terraform', 'ssh', 'config']

    def __init__(self):

        self.root_parser = argparse.ArgumentParser()
        self.root_parser.add_argument('cluster_name', help='Cluster Name')

        self.__configure_subparsers()

    def __configure_subparsers(self):

        subparsers = self.root_parser.add_subparsers(dest='obie_cmd', help='sub-command help')
        subparsers.required = True
        ConfigureSubParsers(subparsers, self.available_subparsers)

    def get_arguments(self):

        args, extra_args_list = self.root_parser.parse_known_args()
        args.extra_args = extra_args_list

        return args
