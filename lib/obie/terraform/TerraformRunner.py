import logging
from os import path, environ, remove
import subprocess

from obie.config.ObieConfig import ObieConfig
from obie.config.ClusterConfig import ClusterConfig
from obie.terraform.Exceptions import TerraformException, TerraformBackendException
from obie.terraform.TerraformBackend import TerraformBackend
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class TerraformRunner:

    def __init__(self, cluster_name):

        obie_config = ObieConfig()
        cluster_config = ClusterConfig(cluster_name, obie_config)

        try:
            self.terraform_backend = TerraformBackend(obie_config, cluster_config)
        except TerraformBackendException:
            return

        self.cluster_config = cluster_config
        assert isinstance(self.cluster_config.terraform_config['aws_account_id'], int), \
            "The value of 'aws_account_id' is not a number."

        # self.obie_home = obie_config.obie_home
        # self.obie_clusters_dir = obie_config.obie_clusters_dir
        # self.obie_config_file = obie_config.obie_config_abspath
        # self.s3_backend_prefix = obie_config.obie_config_params['s3_backend_prefix']
        # self.aws_id = self.cluster_config.terraform_config['aws_account_id']

        self.resources = cluster_config.dependecies_graph.sorted_nodes
        self.cluster_name = cluster_config.cluster_name
        self.obie_work_dir = cluster_config.obie_work_dir
        self.environment_type = cluster_config.environment_type
        self.output_file = 'terraform_{resource}.plan'

    @staticmethod
    def _run_command(command, resource_path):
        logger.info("running command: {command}".format(command=command))
        process = subprocess.Popen(command, shell=True, cwd=resource_path,
                                   env=environ)
        process.wait()

        if process.returncode != 0:
            raise TerraformException('{command} failed'.format(command=' '.join(command.split()[0:2])))

        logger.info('Obie: Terraform Successful command')

        return process.returncode

    def terraform_init(self, resource, resource_path, backend, force_copy=False):
        supported_backends = ['local', 's3']
        # This function will run `terraform init` command
        # If the backend is 's3' it will also configure the terrafrom backend.

        if backend not in supported_backends:
            raise TerraformException('Unsupported backend: Backend must be "local" or "s3"')

        if backend == 's3':
            s3_key = '/'.join([
                self.cluster_name,
                self.environment_type,
                resource,
                'terraform.tfstate'
            ])
            backend_file = self.terraform_backend.generate_backend_config(s3_key=s3_key)

            with open(
                    path.join(
                        self.obie_work_dir,
                        '/'.join([resource, 'terraform_backend.tf'])
                    ),
                    'w'
            ) as bf:
                bf.write(backend_file)

        return_code = self._run_command(
            command='terraform init -force-copy' if force_copy else 'terraform init',
            resource_path=resource_path,
        )

        return return_code

    def terraform_plan(self, resources=None):

        if resources is None:
            resources = self.resources

        for resource in resources:
            resource_path = path.join(self.obie_work_dir, resource)

            try:
                self.terraform_init(
                    resource=resource,
                    resource_path=resource_path,
                    backend='s3',
                    force_copy=True,
                )

                return_code = self._run_command(
                    command='terraform plan -out={plan_file}'.format(
                        plan_file=self.output_file.format(resource=resource)
                    ),
                    resource_path=resource_path
                )

            except TerraformException:
                return -1

        return return_code

    def terraform_apply(self, resources=None):

        if resources is None:
            resources = self.resources

        for resource in resources:
            resource_path = path.join(self.obie_work_dir, resource)

            if not path.isfile(path.join(resource_path, self.output_file.format(resource=resource))):
                ret_code_plan = self.terraform_plan(resources=[resource])

                if ret_code_plan != 0:
                    logger.error('Apply for {} failed'.format(resource))
                    return -1

            try:
                self._run_command(
                    command='terraform apply -auto-approve {plan_file}'.format(
                        plan_file=self.output_file.format(resource=resource)
                    ),
                    resource_path=resource_path
                )
            except TerraformException:
                pass

            try:
                remove(path.join(resource_path, self.output_file.format(resource=resource)))
            except FileNotFoundError:
                pass

    def terraform_destroy(self, resources=None):

        if resources is None:
            resources = self.resources
            resources.reverse()

        for resource in resources:
            resource_path = path.join(self.obie_work_dir, resource)

            try:
                self.terraform_init(
                    resource=resource,
                    resource_path=resource_path,
                    backend='s3',
                    force_copy=True,
                )

                self._run_command(
                    command='terraform destroy -auto-approve',
                    resource_path=resource_path
                )
            except TerraformException:
                pass

    def clean_backend(self):
        pass
