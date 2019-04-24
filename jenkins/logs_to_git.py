import boto3
import json
import requests
import os
import botocore
import time

session = boto3.Session(profile_name='tt-dev',
                        region_name='us-east-1'
                        )
logs_client = session.client('logs')

ecs_client = session.client('ecs')

task = os.environ['task_number']
commit = os.environ['obie_commit']

try:
    waiter = ecs_client.get_waiter('tasks_running')
    waiter.wait(cluster='obiecluster',
                tasks=[task],
                WaiterConfig={
                    'Delay': 15,
                    'MaxAttempts': 120,
                }
                )
except botocore.exceptions.WaiterError:
    pass

time.sleep(5)
response = logs_client.get_log_events(logGroupName='/ecs/obie_app',
                                      logStreamName='ecs/obie/{task_number}'.format(task_number=task)
                                      )

commit_comment = ''

for event in response['events']:
    commit_comment = ''.join([commit_comment,
                              '\n',
                              event['message']
                              ])

endpoint = 'https://git.corp.adobe.com/api/v3/repos/dsirbu/tt_infra/commits/{commit_hash}/comments'.format(
    commit_hash=commit)
headers = {'Authorization': 'token {token}'.format(token='0f2561352222adea293f502e64b84c7f54cad3e5')}
data = {'body': commit_comment}

response = requests.post(url=endpoint, data=json.dumps(data), headers=headers)

print(commit_comment)
