import logging

from obie.config.ObieConfig import ObieConfig
from obie.config.ClusterConfig import ClusterConfig
from obie.terraform.TerraformRunner import TerraformRunner
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class RunSubparser:

    @staticmethod
    def generate_configs(cluster_name):
        obie_config = ObieConfig()
        cluster_config = ClusterConfig(cluster_name, obie_config)

        return obie_config, cluster_config

    @classmethod
    def terraform(cls, args):

        logger.info('Run terraform subparser specific commands')

        terraform_run = TerraformRunner(args.cluster_name)

        subcommands = {
            'plan': terraform_run.terraform_plan,
            'apply': terraform_run.terraform_apply,
            'destroy': terraform_run.terraform_destroy,
        }

        if args.resource is not None:
            subcommands[args.subcommand]([args.resource])
        else:
            subcommands[args.subcommand]()

    @classmethod
    def ssh(cls, args):

        obie_config, cluster_config = cls.generate_configs(args.cluster_name)
        logger.info('Run ssh subparser specific commands')
        logger.info(obie_config)
        logger.info(args)
        logger.info('SSH extra args: {}'.format(args.extra_args))

    @classmethod
    def config(cls, args):

        obie_config, cluster_config = cls.generate_configs(args.cluster_name)

        logger.info('Run config subparser specific commands')

        subcommands = {
            'show': cluster_config.show_cluster_terraform_vars,
            'write': cluster_config.write_cluster_terraform_vars
        }

        subcommands[args.subcommand]()
