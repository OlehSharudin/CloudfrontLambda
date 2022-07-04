# CloudfrontLambda
Unified repo with all cloudfront-CDN-related lambdas and single config files to be deployed as a single entity.

### Deployment
Currently being used by Smart Pipeline



## Functionality 

The current requirement of the CDN failover is to create permanent ingress rules on the HAPROXY ELBs or Smart Gateway ALBs for all global cloudfront IP ranges.

This reduces complexity in the script and increases security. Currently when we failover we add a rule in the script that allows all traffic on port 443 and port 80 (0.0.0.0/0)

Amazon publish their ipranges at https://ip-ranges.amazonaws.com/ip-ranges.json

We know the current global cloudfront ranges, but would like to monitor this for changes (new ranges added / current ranges removed) and get alerted when changes occur so that we can update our ingress rules accordingly.


All of the process of keeping Cloudfront IP list up to date automatically consists of 3 Python lambdas:

- Сloudfront Filter

- Сloudfront Сomparer

- Cloudfront Parser 


Cloudfront needs to be able to reach HAProxy and HAproxyAPI via the ELB, this requires that Cloudfront SGs are created and permanently attached to the ELBs and these need to be updated on the fly with information from AWS (update HAproxy Security groups with Cloudfront CIDR IP Ranges).

Python lambdas has AMI roles attached with the needed access level so it can update the SGs.
It able to work in all environments and It was deployable via smart pipeline.


### Cloudfront Filter

First lambda (Сloudfront Filter) is getting a list of CLOUDFRONT IPs from AWS JSON file - "http://ip-ranges.amazonaws.com/ip-ranges.json", parsing it and creating a list with only Global CLOUDFRONT IPs. After that it's uploading a JSON file with the current IPs range (aws-ip-ranges.json) to S3 bucket (each environment has its own bucket). Format of the bucket name is - "je-environment-cloudfront".

After that it's creating a copy of that JSON file (aws-ip-ranges.json) with the IPs for further comparison in next lambda. 

Copy of the file will be saved under 'aws-ip-ranges-old.json'.


### Cloudfront Comparer

Second lambda (Сloudfront Сomparer) is reading two JSON files ( 'aws-ip-ranges-old.json' and 'aws-ip-ranges.json') with the IPs from S3 buckets and doing a comparison between them.

As soon as inconsistency will be detected between 2 lists of IPs it automatically will invoke third lambda (Cloudfront Parser) and will send IPs difference (newly added or deleted by AWS) in Payload to it.



### Cloudfront Parser

Third lambda (Cloudfront Parser) is reading CIDR Ranges, which were sent in Payload by second lambda (Сloudfront Сomparer) and creating SGs rules with them.

We assume we need 3 SGs max - count to three and check that the SGs exist, if not create them, extract group names from list of groups that matched the tag filter and append them to a new list. If there are more than 30 ranges we're going to have to split them up - however we can probably just loop through the ranges and switch SGs when one is full.
