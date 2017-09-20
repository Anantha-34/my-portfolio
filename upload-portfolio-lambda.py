import boto3
import StringIO
import zipfile
from botocore.client import Config
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:781061244632:deploynoti')

    location = {
        "bucketName": 'ananthabuild.portfolio.info',
        "objectKey": 'ananthacodebuild'
    }

    try:
        job = event.get("CodePipeline.job");

        if job:
            for artifact in job ["data"] ["inputArtifacts"]:
                if artifact["name"] == "myAppBuild":

                    location = artifact["location"] ["s3location"]

        s3 = boto3.resource('s3',config=Config(signature_version='s3v4'))

        print "Building portfolio from" + str (location)

        portfolio_bucket = s3.Bucket ('anantha.portfolio.info');
        portfoliobuild_bucket = s3.Bucket (location["bucketName"]);

        portfolio_zip = StringIO.StringIO()
        portfoliobuild_bucket.download_fileobj(location["objectKey"],portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm,
                ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

            print "Job done"
            topic.publish(Subject="portfolio deployed",Message="Portfolio deployment was  succecssful")

            if job:
                codepipeline = boto3.client('codepipeline')
                codepipeline.put_job_success_result(jobId=job["id"])

    except:
        topic.publish(Subject="portfolio deploy failure",Message="Portfolio deployment was not  succecssful")
        raise

    return 'Hello from Lambda'
