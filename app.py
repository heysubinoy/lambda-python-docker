import json
import os
import boto3
import subprocess

def handler(event, context):
    # Set up AWS credentials and region for GDAL vsis3
    os.environ["AWS_REGION"] = "ap-south-1"
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    try:
        # s3_client = boto3.client("s3")
        # bucket_name = event.get("bucket_name")
        # input_s3_key = event.get("input_s3_key")
        # output_s3_key = event.get("output_s3_key")

        # if not bucket_name or not input_s3_key or not output_s3_key:
        #     raise ValueError("Missing required S3 parameters (bucket_name, input_s3_key, output_s3_key).")
        
        # input_s3_path = f"/vsis3/{bucket_name}/{input_s3_key}"
        # output_s3_path = f"/vsis3/{bucket_name}/{output_s3_key}"

        # # Check if the input file exists
        # try:
        #     s3_client.head_object(Bucket=bucket_name, Key=input_s3_key)
        # except Exception as e:
        #     raise FileNotFoundError(f"Input file not found in S3: {e}")
        input_s3_path = f"L1CSGPSWIR.tif"
        output_s3_path = f"output.tif"

        cmd = [
            "/root/miniconda3/bin/gdal_translate",
            "-of", "COG",
            "-co", "COMPRESS=ZSTD",
            "-co", "PREDICTOR=YES",
            "-co", "NUM_THREADS=ALL_CPUS",
            "-co", "OVERVIEWS=AUTO",
            "-co", "LEVEL=22",
            "-co", "QUALITY=100",
            "-co", "BIGTIFF=IF_SAFER",
            input_s3_path, output_s3_path
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Print the subprocess output live to CloudWatch
        print(f"GDAL Output: {result.stdout}")
        print(f"GDAL Error: {result.stderr}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Conversion to COG successful and saved to S3!"}),
        }

    except Exception as e:
        print(f"Error during COG conversion: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error during conversion: {e}"}),
        }
