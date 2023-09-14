import subprocess
import enum
import datetime
import base64
import hmac
import hashlib
import os
import requests
import boto3

class Acl(enum.Enum):
    PublicAccess = 'public-read'


def UploadToS3(bucket_name, local_file_path, s3_object_name, acl):
    aws_cli_command = f'aws s3 cp {local_file_path} s3://{bucket_name}/{s3_object_name} --acl {acl}'

    try:
        subprocess.run(aws_cli_command, shell =True, check = True)
        print('Success')
    except subprocess.CalledProcessError as e:
        print(f'Failed to upload thi file. Error: {e}')

def UploadToS3_Rest(bucket_name, object_key, local_file_path,content_type, acl):
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')

    s3_endpoint = f'https://{bucket_name}.s3.amazonaws.com'
    
    cur_datetime = datetime.datetime.utcnow()
    formatted_date = cur_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')

    string_to_sign = f'PUT\n\n{content_type}\n{formatted_date}\n/{bucket_name}/{object_key}'
    signature = base64.b64encode(
        hmac.new(aws_secret_key.encode("UTF-8"), string_to_sign.encode("UTF-8"), hashlib.sha1).digest()
    )

    headers = AWSRequestHeader(formatted_date, aws_access_key, signature, content_type, acl)

    with open(local_file_path, 'rb') as file:
        response = requests.put(
            f'{s3_endpoint}/{object_key}',
            data = file,
            headers = headers
        )

    if response.status_code == 200:
        print('File uploaded successfully')
    else:
        print('File upload failed with status code:', response.status_code, response.content)

def UploadToS3_Boto(bucket_name, local_file_path, object_key, acl):
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')

    # Create an S3 client
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )
    s3 = session.client('s3')

    # Upload the PNG file to S3
    try:
        s3.upload_file(local_file_path, bucket_name, object_key, ExtraArgs={'ACL': acl})
        print('PNG file uploaded successfully')
    except Exception as e:
        print('Error uploading PNG file:', str(e))


def DownloadFromS3(bucket_name, local_file_path, s3_object_name):
    aws_cli_command = f'aws s3 cp s3://{bucket_name}/{s3_object_name} {local_file_path} '

    try:
        subprocess.run(aws_cli_command, shell =True, check = True)
        print('Success')
    except subprocess.CalledProcessError as e:
        print(f'Failed to upload thi file. Error: {e}')


def DownloadFromS3_Boto3(bucket_name, local_file_path, s3_object_name):
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')

    # Create an S3 client
    session = boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
    )
    s3 = session.client('s3')

    # Download the PNG file to S3
    try:
        s3.download_file(bucket_name, s3_object_name, local_file_path)
        print('PNG file download successfully')
    except Exception as e:
        print('Error downloads PNG file:', str(e))

def AWSRequestHeader(date, aws_access_key, signature, content_type, acl):
    authorization = f'AWS {aws_access_key}:{signature}'
    headers = {
        'Content-Type':f'{content_type}',
        'x-amz-date': f'{date}',
        'x-amz-acl': f'{acl}',  # Optional: Set ACL permissions as needed
        'Authorization': f'{authorization}',
    }
    print(headers)
    return headers

#Testing
#UploadToS3('chi-public-bucket', '/Users/chain-mac/Downloads/AAAA.png', 'BBBBB.png', Acl.PublicAccess.value)
#DownloadFromS3('chi-public-bucket','/Users/chain-mac/Downloads/BBB.png', 'BBBBB.png')
#UploadToS3_Rest('chi-public-bucket', 'BBBBB.png', '/Users/chain-mac/Downloads/AAAA.png', 'image/png', Acl.PublicAccess.value)
#UploadToS3_Boto('chi-public-bucket', '/Users/chain-mac/Downloads/AAAA.png', 'BBBBB.png', Acl.PublicAccess.value)
DownloadFromS3_Boto3('chi-public-bucket', '/Users/chain-mac/Downloads/OOO.png', 'BBBBB.png')