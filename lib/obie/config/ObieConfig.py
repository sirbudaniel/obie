import os
import yaml
import logging

from obie.config.ConfigExceptions import ObieConfigErrorException
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class ObieConfig:

    obie_home_env_name = 'OBIE_HOME'
    obie_conf = '.obie/config.yaml'
    mandatory_parameters = ['s3_backend_prefix']

    def __init__(self):

        self.obie_home = os.getenv(self.obie_home_env_name, 'None')

        if not os.path.isabs(self.obie_home):
            raise ObieConfigErrorException('Environment variable {} must be set to an existing absolute path! '
                                           'Current value: "{}" '.format(self.obie_home_env_name, self.obie_home))

        self.obie_clusters_dir = os.path.join(self.obie_home, 'clusters')
        self.obie_config_abspath = os.path.join(self.obie_clusters_dir, self.obie_conf)

        self._get_obie_config()

    def _get_obie_config(self):

        if not os.path.isfile(self.obie_config_abspath):
            raise FileNotFoundError('Obie configuration file {} does not exists!'.format(self.obie_config_abspath))

        self.obie_config_params = {}
        with open(self.obie_config_abspath, 'r') as f:
            self.obie_config_params = yaml.load(f)

        self._check_mandatory_parameters()

    def _check_mandatory_parameters(self):
        for param in self.mandatory_parameters:
            if param not in self.obie_config_params:
                raise ObieConfigErrorException('Manadatory parameter "{}" does not exist!'.format(param))

