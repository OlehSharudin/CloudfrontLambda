# CloudfrontLambda Runbook.


The feature consistes of three lambdas.

- Сloudfront Filter

- Сloudfront Сomparer

- Cloudfront Parser

--
## Observability 
All of the metrics are ready to be used as a source data for Grafana dash.

The Filter and the Parser are invoked regularly to collect and to compare the data from Cloudfront.
The Parser is only invoked if the comparer discovers that the CIDR ranges published by AWS have changed.
This change is really infrequent so don't be worried if the Parser graphs have no data.

-----


Only the parser updates the SGs in each environment (and it will create them if they don't exist)
If for some reason the SGs are missing (Human accidental deletion) then invoke the parser manually from the AWS console.

The most catastrophic failure I can imagine would take deliberate sabotage inasmuch as to completely ruin everyone's day,
one could replace the files in the S3 bucket with empty files and the parser is invoked, which will remove all of the 
ingress rules from the SGs, and then we failed over to CloudFront. If this happens, within 5 minutes the Filter will collect
the correct data from AWS, the Filter will see that the data is different, invoke the Parser and repopulate the SGs, so it's
self healing.

## Deployment
If you need to redeploy the feature for some reason, the pipeline could be found in Concourse.