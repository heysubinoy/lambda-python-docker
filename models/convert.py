import subprocess

def convert_to_cog(input_s3_path, output_s3_path):
    """Convert an S3-based input file to a COG and save directly back to S3."""

    # GDAL translation command to convert input to Cloud Optimized GeoTIFF
    cmd = [
        "gdal_translate",
        "-of",
        "COG",  # Output format is Cloud Optimized GeoTIFF
        "-co",
        "COMPRESS=ZSTD",  # Compression method
        "-co",
        "PREDICTOR=YES",  # Use floating point predictor
        "-co",
        "NUM_THREADS=ALL_CPUS",
        "-co",
        "OVERVIEWS=AUTO",
        "-co",
        "LEVEL=22",
        "-co",
        "QUALITY=100",
        "-co",
        "BIGTIFF=IF_SAFER",
        input_s3_path,  # Input file in S3
        output_s3_path,  # Output file path in S3
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        # Run the GDAL command as a subprocess
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"GDAL Output: {result.stdout}")
        print(f"Conversion to COG successful and saved to {output_s3_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error in conversion: {e}")
        print(f"Error Output: {e.stderr}")
    except Exception as e:
        print(f"Unexpected error: {e}")
