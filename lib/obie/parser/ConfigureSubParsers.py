import logging
from argparse import _SubParsersAction as SubParser

from obie.parser.RunSubparser import RunSubparser
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class ConfigureSubParsers:

    def __init__(self, subparser: SubParser, subparsers_name: list = []):
        self.subparser = subparser

        configure_subparser = {
            'terraform': self.__terraform,
            'ssh': self.__ssh,
            'config': self.__config
        }
        for name in subparsers_name:
            configure_subparser[name]()

    def __terraform(self):

        terraform_parser = self.subparser.add_parser('terraform',
                                                     help='Run terraform specific commands.')
        terraform_parser.add_argument('subcommand', choices=['apply', 'plan', 'destroy'])
        terraform_parser.set_defaults(runfunc=RunSubparser.terraform)
        terraform_parser.add_argument('resource', nargs='?', help='Resource Name')


    def __ssh(self):

        ssh_parser = self.subparser.add_parser('ssh', help='Run ssh specific commands.')
        ssh_parser.add_argument('-l', help='username to use when connecting through ssh')
        ssh_parser.set_defaults(runfunc=RunSubparser.ssh)

    def __config(self):

        config_parser = self.subparser.add_parser('config', help='Get information about cluster configuration.')
        config_parser.add_argument('subcommand', choices=['write', 'show'])
        config_parser.set_defaults(runfunc=RunSubparser.config)
