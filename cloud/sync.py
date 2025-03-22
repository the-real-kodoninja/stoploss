import boto3  # Example using AWS S3; requires `pip install boto3`

def upload_to_cloud(file_path, bucket="stop-loss-bucket"):
    s3 = boto3.client('s3', aws_access_key_id="YOUR_AWS_KEY", aws_secret_access_key="YOUR_AWS_SECRET")
    s3.upload_file(file_path, bucket, file_path.split('/')[-1])