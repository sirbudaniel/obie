import boto3
import json


def http_response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
    }


def handler(event, context):
    try:
        docker_version = event["queryStringParameters"]["docker_version"]
    except KeyError:
        docker_version = "latest"

    client = boto3.client('ecs')

    task_definition = client.register_task_definition(
        family='obie_app',
        taskRoleArn='arn:aws:iam::404771020307:role/obie_role',
        executionRoleArn='arn:aws:iam::404771020307:role/obie_role',
        networkMode='awsvpc',
        containerDefinitions=[
            {
                'name': 'obie',
                'image': 'docker.io/sirbudaniel/obie:{tag}'.format(tag=docker_version),
                'portMappings': [
                    {
                        'containerPort': 80,
                        'hostPort': 80,
                        'protocol': 'tcp'
                    },
                ],
                'essential': True,
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': '/ecs/obie_app',
                        'awslogs-region': 'us-east-1',
                        'awslogs-stream-prefix': 'ecs'
                    }
                },
            },
        ],
        requiresCompatibilities=[
            'FARGATE',
        ],
        cpu='4096',
        memory='8192',
    )
    task_definition_name = 'obie_app:{revision}'.format(revision=task_definition['taskDefinition']['revision'])

    task = client.run_task(
        cluster='obiecluster',  # name of the cluster
        launchType='FARGATE',
        taskDefinition=task_definition_name,
        count=1,
        platformVersion='LATEST',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': [
                    'subnet-0a286c3f2aaccbeae',  # replace with your public subnet or a private with NAT
                ],
                'assignPublicIp': 'ENABLED'
            }
        })

    task_number = task['tasks'][0]['taskArn'].split('/')[-1]

    client.deregister_task_definition(
        taskDefinition=task_definition_name
    )

    return http_response({'message': 'Lambda function has executed successfully!',
                          'task_number': task_number,
                          }, 200)
