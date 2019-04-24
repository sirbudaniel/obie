import os
import sys
import yaml
import json
import logging

from obie.util import CheckCluster, DependenciesGraph
from obie.config import ObieConfig
from obie.config.ConfigExceptions import ClusterConfigErrorException
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class ClusterConfig:

    cluster_config_filename = 'config.yaml'
    cluster_tfvars_global_filename = 'global.auto.tfvars'
    cluster_global_var_definition_filename = 'global.auto.variables.tf'

    tfvars_auto_filename = '{conf_name}.auto.tfvars'
    tfvars_definition_filename = '{conf_name}.auto.variables.tf'

    tfvar_templare = 'variable "{name}" {{\n  type = "{type}"\n}}\n'

    @CheckCluster(cluster_config_filename)
    def __init__(self, cluster_name, obie_config: ObieConfig):

        self.cluster_name = cluster_name
        self.obie_config = obie_config
        self.obie_work_dir = os.path.join(self.obie_config.obie_clusters_dir, self.cluster_name)
        self.cluster_config_path = os.path.join(self.obie_work_dir, self.cluster_config_filename)

        self.dependecies_graph = DependenciesGraph()
        self.__generate_terraform_config()

    def show_cluster_terraform_vars(self):
        logging.info('\n#### Terraform vars for cluster {} ####\n'.format(self.cluster_name))
        json.dump(self.cluster_config, sys.stdout, indent=2, sort_keys=True)

        logger.info('\n #### Global Terraform vars for cluster {} ####\n'.format(self.cluster_name))
        json.dump(self.terraform_config, sys.stdout, indent=2, sort_keys=True)

    def write_cluster_terraform_vars(self):
        """
            This function will write global and configuration specific terraform variables for the specified cluster.
            Variables are exported as JSON instead of HCL
        """

        with open(os.path.join(self.obie_work_dir, self.cluster_tfvars_global_filename), 'w') as tfvars_gfd:
            json.dump(self.terraform_config, tfvars_gfd, indent=2, sort_keys=True)

        with open(os.path.join(self.obie_work_dir, self.cluster_global_var_definition_filename), 'w') as tfvars_global_def_fd:
            for var_name, var_value in self.terraform_config.items():
                tfvars_global_def_fd.write(self.__get_var_type(var_name, var_value))

        for dir in self.cluster_config:
            dir_path = os.path.join(self.obie_work_dir, dir)
            tfvars_path = os.path.join(dir_path, self.tfvars_auto_filename.format(conf_name=dir))
            tfvars_definition_path = os.path.join(dir_path, self.tfvars_definition_filename.format(conf_name=dir))

            if not self.cluster_config[dir]:
                continue

            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)

            with open(tfvars_path, 'w') as tfvars_cfd:
                json.dump(self.cluster_config[dir], tfvars_cfd, indent=2, sort_keys=True)

            with open(tfvars_definition_path, 'w') as tfvars_def_fd:
                for var_name, var_value in self.cluster_config[dir].items():
                    tfvars_def_fd.write(self.__get_var_type(var_name, var_value))

            try:
                os.symlink(os.path.join(self.obie_work_dir, self.cluster_tfvars_global_filename),
                           os.path.join(dir_path, self.cluster_tfvars_global_filename))
                os.symlink(os.path.join(self.obie_work_dir, self.cluster_global_var_definition_filename),
                           os.path.join(dir_path, self.cluster_global_var_definition_filename))
                os.symlink('../../../../terraform_modules/{res}/main.tf'.format(res=dir),
                           os.path.join(dir_path, 'main.tf'))

            except FileExistsError:
                pass

    def __get_var_type(self, name, value):

        if isinstance(value, list):
            return self.tfvar_templare.format(name=name, type='list')
        elif isinstance(value, dict):
            return self.tfvar_templare.format(name=name, type='map')
        elif isinstance(value, (str, int)):
            return self.tfvar_templare.format(name=name, type='string')
        else:
            raise TypeError('Unsupported data type {} of var {}:{}'.format(type(value), name, value))

    def __generate_terraform_config(self):

        with open(self.cluster_config_path, 'r') as stream:
            cluster_config = yaml.load(stream)

        if cluster_config is None:
            raise ClusterConfigErrorException('Could not find any configuration for cluster {}. Config file {}'
                                              .format(self.cluster_name, self.cluster_config_path))

        assert 'environment_type' in cluster_config.keys(), \
            'Could not find environment type configuration for cluster {}'.format(self.cluster_name)

        assert 'terraform_vars' in cluster_config.keys(), \
            'Could not find any terraform configuration for cluster {}'.format(self.cluster_name)

        assert 'aws_account_id' in cluster_config['terraform_vars'].keys(), 'Could not find "aws_account_id" parameter!'

        assert 'configurations' in cluster_config.keys(), \
            'Could not find any infrastructure configuration for cluster {}'.format(self.cluster_name)

        self.cluster_config = cluster_config['configurations']
        self.terraform_config = cluster_config['terraform_vars']
        self.environment_type = cluster_config['environment_type']
        self.terraform_config['cluster_name'] = self.cluster_name

        for resource, res_conf in self.cluster_config.items():
            self.dependecies_graph.add_node(resource)
            if res_conf.get('depends_on') is not None:
                for depependency in res_conf.get('depends_on'):
                    self.dependecies_graph.add_dependency(resource, depependency)
        self.dependecies_graph.topological_sort()

