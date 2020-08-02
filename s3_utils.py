import boto3
from botocore.exceptions import ClientError
import logging
import os


def upload_file(file_name, file):
    """Upload a file to an S3 bucket"""

    s3 = boto3.client('s3')
    try:
        bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
        s3.upload_fileobj(file, bucket_name, file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def create_presigned_url(object_name, expiration=3600):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response
