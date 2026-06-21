# AWS Infrastructure Setup Guide for StreamTube

This guide provides step-by-step instructions on how to set up the necessary AWS infrastructure for your project: AWS S3 (Storage), AWS CloudFront (CDN), and AWS EC2 (Hosting).

---

## 1. Create an S3 Bucket (Storage)
1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2. Search for **S3** in the services search bar.
3. Click **Create bucket**.
4. **Bucket name**: Choose a globally unique name (e.g., `streamtube-videos-sujal`).
5. **AWS Region**: Choose a region close to you.
6. **Object Ownership**: Leave as "ACLs disabled".
7. **Block Public Access settings for this bucket**: **Uncheck** "Block all public access" (you need this so CloudFront and users can read the videos). Acknowledge the warning.
8. Leave everything else as default and click **Create bucket**.
9. Once created, click on your bucket, go to the **Permissions** tab, scroll to **Bucket policy**, and click **Edit**.
10. Paste the following policy to make the files readable:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::streamtube-videos-sujal/*"
        }
    ]
}
```
11. Save changes.

---

## 2. Set Up CloudFront (CDN)
1. Search for **CloudFront** in the AWS Console.
2. Click **Create Distribution**.
3. **Origin domain**: Click the dropdown and select the S3 bucket you just created.
4. **Origin path**: Leave blank.
5. **Name**: Can be left as default.
6. Scroll down to **Default cache behavior**.
7. **Viewer protocol policy**: Select `Redirect HTTP to HTTPS`.
8. Leave everything else as default and click **Create distribution**.
9. *Note: It will take a few minutes for the status to change from "Deploying" to "Enabled".*
10. **Save your Distribution Domain Name**. It will look something like `d1234abcd.cloudfront.net`. **You need this for your `.env` file.**

---

## 3. Create IAM Credentials (API Keys)
To allow the FastAPI backend to upload files to S3, it needs security keys.
1. Search for **IAM** in the AWS Console.
2. Go to **Users** (on the left sidebar) and click **Create user**.
3. **User name**: `streamtube-backend` -> Next.
4. **Permissions options**: Select **Attach policies directly**.
5. Search for `AmazonS3FullAccess` and check the box next to it. -> Next -> Create user.
6. Click on the user you just created (`streamtube-backend`).
7. Go to the **Security credentials** tab.
8. Scroll down to **Access keys** and click **Create access key**.
9. Select **Application running outside AWS** -> Next -> Create access key.
10. **IMPORTANT: Copy your `Access key` and `Secret access key` immediately.** You will not be able to see the secret key again. **You need both of these for your `.env` file.**

---

## 4. Setup the Backend Environment Variables
Once you have completed steps 1-3, update your project's `.env` file with the keys you generated:

```env
AWS_ACCESS_KEY_ID=your_generated_access_key
AWS_SECRET_ACCESS_KEY=your_generated_secret_key
AWS_S3_BUCKET_NAME=streamtube-videos-sujal
CLOUDFRONT_DOMAIN=https://d1234abcd.cloudfront.net
```

*(Note: Ensure your `CLOUDFRONT_DOMAIN` includes the `https://` prefix without a trailing slash).*

---

## 5. Deploy on EC2 (Ubuntu Server)
Once your backend is ready and local testing is successful, you can deploy to EC2.
1. Search for **EC2** in the AWS Console.
2. Click **Launch Instance**.
3. **Name**: `StreamTube-Server`.
4. **OS Image**: Select **Ubuntu** (Ubuntu Server 22.04 LTS).
5. **Instance type**: `t2.micro` or `t3.micro` (Free Tier eligible).
6. **Key pair**: Click "Create new key pair", name it `streamtube-key`, and download the `.pem` file (you need this to SSH into the server).
7. **Network settings**: Check the boxes for:
   - Allow SSH traffic from Anywhere
   - Allow HTTPS traffic from the internet
   - Allow HTTP traffic from the internet
8. Click **Launch instance**.

### Setting up the Server (Nginx & Systemd)
1. SSH into your new EC2 instance using your terminal:
   ```bash
   ssh -i /path/to/streamtube-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
   ```
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx git
   ```
3. Clone your project and install Python requirements.
4. Set up Nginx to proxy port 80 to your FastAPI app running on 8000:
   ```bash
   sudo nano /etc/nginx/sites-available/streamtube
   ```
   *Paste the following config:*
   ```nginx
   server {
       listen 80;
       server_name YOUR_EC2_PUBLIC_IP;

       client_max_body_size 500M; # Allow large video uploads

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_addrs;
       }
   }
   ```
5. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/streamtube /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```
6. Set up a `systemd` service to keep FastAPI running 24/7. Create a file `/etc/systemd/system/streamtube.service` and configure it to run `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.
