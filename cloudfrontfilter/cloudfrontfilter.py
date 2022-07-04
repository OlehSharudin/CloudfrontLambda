#!/usr/bin/python

import requests
import json
import sys
import boto3
import yaml


def lambda_handler(event, context):
    print("Fisrt stage")
    s3client = boto3.client('s3')
    s3resource = boto3.resource('s3')

    print("1.5 Stage")
    print(s3resource)

    #Getting a list of GLOBAL CLOUDFRONT IPs from AWS
    aws_url = "http://ip-ranges.amazonaws.com/ip-ranges.json"

    #Checking connection to the AWS IPs list
    response = requests.get(aws_url)
    print("Second stage")
    print(response)

    if response.status_code != 200:
        print("Failed to get JSON from {}: {}".format(aws_url, response.status_code))
        sys.exit(1)

    json_data = json.loads(response.text)
    print(json_data)
   
    #Parsing AWS JSON file and creating a list with only Global CLOUDFRONT IPs
    aws_list = []
    for prefix in json_data['prefixes']:
        if prefix['service'] == 'CLOUDFRONT' and prefix['region'] == 'GLOBAL':
            aws_list.append(prefix['ip_prefix'])

    print(aws_list)

    #Get the environment we are operating in
    with open('je.env.yml', 'r') as f:
        config = yaml.load(f)
        env = config['environment']
        print(env)

    print("Third stage")    

    bucket_name = 'je-' + env + '-cloudfront'
    bucket_exists = False
    print(bucket_name)

    buckets_list = s3client.list_buckets()
    for bucket in buckets_list['Buckets']:
        if bucket['Name'] == bucket_name:
            bucket_exists = True

    print(buckets_list)


    if bucket_exists == False:
        try:
            s3client.create_bucket(Bucket = bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        except:
            print("Can't create bucket")


    if 'Contents' in s3client.list_objects(Bucket = bucket_name).keys():
        for key in s3client.list_objects(Bucket = bucket_name)['Contents']:
            if (key['Key']):
                print(key['Key'])
                if (key['Key']) == 'aws-ip-ranges.json':
                    s3resource.Object(bucket_name,'aws-ip-ranges-old.json').copy_from(CopySource = bucket_name + '/aws-ip-ranges.json')  


    #Uploading JSON file with the current AWS CLOUDFRONT IPs range to S3 bucket
    data = str(aws_list)
    s3resource.Object(bucket_name, 'aws-ip-ranges.json').put(Body=(bytes(json.dumps(data, indent=2).encode('UTF-8'))))
    print("\nUploading JSON file with the current AWS CLOUDFRONT IPs range")

    print(data)

    return {
       'statusCode': 200,
       'body': json.dumps('Hello from Lambda!')
    }

#EOF
