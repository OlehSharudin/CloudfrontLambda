#!/usr/bin/python

import requests
import json
import sys
import boto3
import yaml
from botocore.config import Config
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    print("Running now")

    event = event.replace("[", "")
    event = event.replace("]", "")
    event = event.replace("'", "")
    event = event.replace(",", "")
    event = event.replace('"', "")

    rangeList = event.split(" ")
    numRanges = len(rangeList)

    print("Number of CIDR Ranges: " + str(numRanges))

    ec2 = boto3.client('ec2')
    filters = [{
        'Name': 'tag:je:service',
        'Values': ['cloudfront']
    }]
    group_ids_list = []
    reservations = ec2.describe_security_groups(Filters=filters)
    for id in reservations['SecurityGroups']:
        group_ids_list.append(id['GroupId'])
    
    print(group_ids_list)

    config = Config(
        retries = dict(
            max_attempts = 20
        )
    )
    ec2Res = boto3.resource('ec2', config=config)

    # get the environment we are deploying to
    with open('je.env.yml', 'r') as f:
        config = yaml.load(f)
        env = config['environment']
        print(env)
    

# We assume we need 3 SGs max - count to three and check that the SGs exist, if not create them
    #extract group names from list of groups that matched the tag filter and append them to a new list
    group_names_list = list()
    for sg in group_ids_list:
        security_group = ec2Res.SecurityGroup(sg)
        group_names_list.append(security_group.group_name)

    print(group_names_list)

    #compare the list of names against the expected names, if an expected group does not exist, create it
    for n in range(1, 4):
        SGName = f"cloudfront_sg_{env}_all_{n}a"
        if SGName in group_names_list:
            print(SGName + " exists")
        else:
            print(SGName + " doesn't exist - creating...")
            #get VPC ID for SG creation by environment name
            response = ec2.describe_vpcs(
                Filters=[{'Name':'tag:Name', 'Values':[f'{env}']}]
            )
            vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

            try:
                response = ec2.create_security_group(GroupName=SGName, Description='cloudfront CIDR ranges', VpcId=vpc_id)
                #security groups do not support tagging on creation so we'll tag the new group now.
                security_group_id = response['GroupId']
                ec2.create_tags(Resources=[security_group_id], Tags=[{'Key': 'je:feature', 'Value': 'haproxy'},{'Key': 'je:service', 'Value': 'cloudfront'}])
                print("created " +  security_group_id)
                #Add the new group Id and Name to the Ids and Names lists
                group_ids_list.append(security_group_id)
                group_names_list.append(SGName)
            except ClientError as e:
                print(e)
    
    # Let's empty the SGs
    for groupId in group_ids_list:
        print("emptying " + groupId)
        sg = ec2Res.SecurityGroup(groupId)
        if sg.ip_permissions:
            sg.revoke_ingress(IpPermissions=sg.ip_permissions)


    # If there are more than 30 ranges we're goint to have to split them up - however we can probably just loop through the ranges and switch SGs when one is full.
    for RangeIndex, ipAddressRange in enumerate(rangeList, start=0):
        ipAddressRange = ipAddressRange.strip()
        groupName = group_names_list[0]
        groupId = group_ids_list[0]
        if RangeIndex > 28:
            groupName = group_names_list[1]
            groupId = group_ids_list[1]
        if RangeIndex > 58:
            groupName = group_names_list[2] 
            groupId = group_ids_list[2]       
        print(str(RangeIndex) + " : " + ipAddressRange + " : " + groupName + " : " + str(groupId))
        sg = ec2Res.SecurityGroup(groupId)
        sg.authorize_ingress(IpProtocol="tcp",CidrIp=ipAddressRange,FromPort=80,ToPort=80)
        sg.authorize_ingress(IpProtocol="tcp",CidrIp=ipAddressRange,FromPort=443,ToPort=443)

 
    return {
   		'statusCode': 200,
		'body': json.dumps('Hello from Lambda!')
	}
	   
#EOF
