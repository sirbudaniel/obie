import boto3
import logging
from urllib.request import urlopen
from urllib.error import URLError

from botocore.client import ClientError

from obie.config.ClusterConfig import ClusterConfig
from obie.config.ObieConfig import ObieConfig
from obie.terraform.Exceptions import TerraformBackendException
from obie.util import consoleHandler

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class TerraformBackend:

    S3_BACKEND_CONFIG_TEMPLATE = """terraform {{
      backend "s3" {{
        bucket = "{s3_bucket_name}"
        region = "{aws_region}"
        profile = "{aws_profile}"
        key = "{s3_key}"
        dynamodb_table = "{dynamodb_table_name}"
      }}
    }}"""

    def __init__(self, obie_config: ObieConfig, cluster_config: ClusterConfig):

        self.config = cluster_config.terraform_config

        meta = 'http://169.254.170.2/v2/metadata'

        try:
            urlopen(meta).read()
            logger.info('I am running in AWS')

            self.session = boto3.Session()

        except URLError:
            logger.info('No metadata, not in AWS')

            try:
                self.session = boto3.Session(profile_name=self.config['aws_profile'],
                                             region_name=self.config['aws_region'])
            except KeyError:
                raise TerraformBackendException("aws_profile must be provided")

        self.bucket_name = ''.join([
            obie_config.obie_config_params['s3_backend_prefix'],
            '-obie-remote-tfstate-',
            str(self.config['aws_account_id']),
        ])

        self.s3 = self.session.client('s3')
        self.dynamo_db = self.session.client('dynamodb')

        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.s3.create_bucket(
                Bucket=self.bucket_name,
                ObjectLockEnabledForBucket=True,
            )

        try:
            self.dynamo_db.describe_table(TableName=self.bucket_name)

        except self.dynamo_db.exceptions.ResourceNotFoundException:

            try:
                table = self.dynamo_db.create_table(
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'LockID',
                            'AttributeType': 'S'
                        }
                    ],
                    TableName=self.bucket_name,
                    KeySchema=[
                        {
                            'AttributeName': 'LockID',
                            'KeyType': 'HASH'
                        }
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 30,
                        'WriteCapacityUnits': 30,
                    },
                )

                waiter = self.dynamo_db.get_waiter('table_exists')
                waiter.wait(TableName=self.bucket_name)

            except self.dynamo_db.exceptions.ResourceInUseException:
                logger.info("Error creating DynamoDB")

    def generate_backend_config(self, s3_key):

        return TerraformBackend.S3_BACKEND_CONFIG_TEMPLATE.format(s3_bucket_name=self.bucket_name,
                                                                  aws_region=self.config['aws_region'],
                                                                  aws_profile=self.config['aws_profile'],
                                                                  s3_key=s3_key,
                                                                  dynamodb_table_name=self.bucket_name)
