import json
import os
import boto3
import subprocess
import tempfile

def handler(event, context):
    # Set up AWS credentials and region for GDAL vsis3
    os.environ["AWS_REGION"] = "ap-south-1"
    os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID")
    os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    try:
        s3_client = boto3.client("s3")
        bucket_name = event.get("bucket_name")
        input_s3_key = event.get("input_s3_key")
        output_s3_key = event.get("output_s3_key")

        if not bucket_name or not input_s3_key or not output_s3_key:
            raise ValueError("Missing required S3 parameters (bucket_name, input_s3_key, output_s3_key).")
        
        # Step 1: Download the input file from S3 to a temporary local file
        with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
            s3_client.download_file(bucket_name, input_s3_key, temp_input_file.name)
            temp_input_path = temp_input_file.name
            print(f"Downloaded input file to: {temp_input_path}")
        
        # Step 2: Set up the output temporary file path
        temp_output_file = tempfile.NamedTemporaryFile(delete=False)
        temp_output_path = temp_output_file.name
        temp_output_file.close()  # Close the file to ensure it can be used later

        print(f"Output file path: {temp_output_path}")
        
        # Step 3: Run the gdal_translate command on the local file
        cmd = [
            "gdal_translate",
            "-of", "COG",
            "-co", "COMPRESS=ZSTD",
            "-co", "PREDICTOR=YES",
            "-co", "NUM_THREADS=ALL_CPUS",
            "-co", "OVERVIEWS=AUTO",
            "-co", "LEVEL=22",
            "-co", "QUALITY=100",
            "-co", "BIGTIFF=IF_SAFER",
            temp_input_path, temp_output_path
        ]

        # Run the command and capture the output
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        
        # Print the subprocess output live to CloudWatch
        print(f"GDAL Output: {result.stdout}")
        print(f"GDAL Error: {result.stderr}")
        
        # Step 4: Upload the output file to S3
        s3_client.upload_file(temp_output_path, bucket_name, output_s3_key)
        print(f"Uploaded output file to S3: s3://{bucket_name}/{output_s3_key}")
        
        # Step 5: Clean up temporary files
        os.remove(temp_input_path)
        os.remove(temp_output_path)
        
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