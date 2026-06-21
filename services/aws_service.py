import os
import boto3
from fastapi import UploadFile
from botocore.exceptions import NoCredentialsError, ClientError

# Initialize the S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
CLOUDFRONT_DOMAIN = os.getenv('CLOUDFRONT_DOMAIN')

async def upload_file_to_s3(file_obj: UploadFile, s3_key: str) -> str:
    """
    Uploads a file object to AWS S3 and returns the CloudFront URL.
    """
    try:
        # Check if AWS credentials are provided (skip if running purely locally without `.env` config)
        if not S3_BUCKET_NAME or not os.getenv('AWS_ACCESS_KEY_ID'):
            print(f"AWS Credentials missing! Mocking upload for {s3_key}")
            # Fallback to local upload logic if no AWS keys exist yet
            local_dir = "uploads/thumbnails" if "thumbnails" in s3_key else "uploads/videos"
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, os.path.basename(s3_key))
            with open(local_path, "wb") as buffer:
                buffer.write(await file_obj.read())
            # Reset file pointer if needed
            await file_obj.seek(0)
            return f"/{local_path}"

        # Upload to S3
        # file_obj.file is a SpooledTemporaryFile which can be directly read by boto3
        s3_client.upload_fileobj(
            file_obj.file,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": file_obj.content_type
            }
        )

        # Construct the CDN URL
        cloudfront_url = f"{CLOUDFRONT_DOMAIN}/{s3_key}"
        return cloudfront_url

    except NoCredentialsError:
        print("Credentials not available")
        return None
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None

def delete_file_from_s3(s3_key: str):
    """
    Deletes a file object from AWS S3.
    """
    if not S3_BUCKET_NAME or not os.getenv('AWS_ACCESS_KEY_ID'):
        # Mock deletion if not using AWS
        local_dir = "uploads/thumbnails" if "thumbnails" in s3_key else "uploads/videos"
        local_path = os.path.join(local_dir, os.path.basename(s3_key))
        if os.path.exists(local_path):
            os.remove(local_path)
        return

    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
    except Exception as e:
        print(f"Error deleting from S3: {e}")
