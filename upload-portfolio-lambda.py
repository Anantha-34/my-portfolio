import boto3
import StringIO
import zipfile
from botocore.client import Config
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3',config=Config(signature_version='s3v4'))

    portfolio_bucket = s3.Bucket ('anantha.portfolio.info');
    portfoliobuild_bucket = s3.Bucket ('ananthabuild.portfolio.info');

    portfolio_zip = StringIO.StringIO()
    portfoliobuild_bucket.download_fileobj('ananthacodebuild',portfolio_zip)

    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolio_bucket.upload_fileobj(obj,nm,
            ExtraArgs={'ContentType':mimetypes.guess_type(nm)[0]})
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

    print "Job done"
    return 'Hello from Lambda'
