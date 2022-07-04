#!/usr/bin/python

import requests
import json
import sys
import boto3
import yaml

def lambda_handler(event, context):
    s3client = boto3.client('s3')
    s3resource = boto3.resource('s3')

    #Get the values we need from file
    with open('je.env.yml', 'r') as f:
        config = yaml.load(f)
        env = config['environment']
        reg = config['region']
        stage = config['stage']
        aID = config['accountId']
        print(f"Env: {env}, Reg: {reg}, Stage: {stage}, aID: {aID}")

    bucket_name = 'je-' + env + '-cloudfront'

    for key in s3client.list_objects(Bucket = bucket_name)['Contents']:
        if (key['Key']) == 'aws-ip-ranges.json':
            #New set pf Ips
            obj_new = s3resource.Object(bucket_name, 'aws-ip-ranges.json')
            s3_data_new = (obj_new.get()['Body'].read().decode('utf-8')) 
        
        elif (key['Key']) == 'aws-ip-ranges-old.json':
            #Old set of Ips
            obj_old = s3resource.Object(bucket_name, 'aws-ip-ranges-old.json')
            s3_data_old = (obj_old.get()['Body'].read().decode('utf-8')) 

    if s3_data_old == s3_data_new:
        print(True)
    else:
        bucket_name = 'je-' + env + '-cloudfront'
        lambda_client = boto3.client('lambda', region_name = reg)
        invoke_response = lambda_client.invoke(FunctionName='arn:aws:lambda:eu-west-1:' + aID + ':function:cloudfrontlambda-' + stage + '-cloudfrontparser', InvocationType='Event', Payload=json.dumps(s3_data_new))
        data = invoke_response['Payload'].read()
        print(False)

    return {
       'statusCode': 200,
       'body': json.dumps('Hello from Lambda!')
    }

#EOF
