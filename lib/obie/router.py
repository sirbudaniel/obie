from flask import Flask

from obie.parser.RunSubparser import RunSubparser
from obie.terraform.TerraformRunner import TerraformRunner

app = Flask(__name__)


@app.route('/')
def index():
    return 'index'


@app.route('/config/show/')
@app.route('/config/show/<cluster_name>')
def config_show(cluster_name=None):

    if cluster_name is None:
        return 'Cluster Name must be provided'
    _, cluster_config = RunSubparser.generate_configs(cluster_name)
    cluster_config.show_cluster_terraform_vars()

    return 'SUCCES'


@app.route('/config/write/')
@app.route('/config/write/<cluster_name>')
def config_write(cluster_name):
    _, cluster_config = RunSubparser.generate_configs(cluster_name)
    cluster_config.write_cluster_terraform_vars()

    return 'SUCCES'


@app.route('/terraform/plan/')
@app.route('/terraform/plan/<cluster_name>/')
@app.route('/terraform/plan/<cluster_name>/<resource>')
def terraform_plan(cluster_name=None, resource=None):

    if cluster_name is None:
        return 'Cluster Name must be provided'
    terraform_run = TerraformRunner(cluster_name)

    if resource is not None:
        terraform_run.terraform_plan([resource])
    else:
        terraform_run.terraform_plan()

    return 'SUCCES'


@app.route('/terraform/apply/')
@app.route('/terraform/apply/<cluster_name>/')
@app.route('/terraform/apply/<cluster_name>/<resource>')
def terraform_apply(cluster_name=None, resource=None):

    if cluster_name is None:
        return 'Cluster Name must be provided'
    terraform_run = TerraformRunner(cluster_name)

    if resource is not None:
        terraform_run.terraform_apply([resource])
    else:
        terraform_run.terraform_apply()

    return 'SUCCES'

