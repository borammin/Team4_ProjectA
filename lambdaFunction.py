import json
import csv
import io

#for dealing with S3 buckets
import boto3

#for uploading metadata to db
import pymysql
from datetime import datetime
import os

# Initialize S3 client using environment variables for security
s3 = boto3.client('s3', 
    aws_access_key_id= os.environ['AWS_ID'],
    aws_secret_access_key= os.environ['AWS_KEY'],
    region_name='us-east-1'
    )

#Fetches a CSV file from an S3 bucket and converts it into a list of dictionaries.

def extractDataFromCSV(bucket, input_key):
    """Takes the csv that was uploaded and parses it into a dict"""
    response = s3.get_object(Bucket=bucket, Key=input_key)
    csv_content = response['Body'].read().decode('utf-8')

    readData = csv.DictReader(io.StringIO(csv_content))
    data = [rowData for rowData in readData]

    return data

# Converts Python list/dictionary data into JSON format.

def convertToJSON(data):
    """Takes the rows of data and turn it into json data"""
    json_content = json.dumps(data, indent=3)

    return json_content.encode('utf-8')

# Uploads JSON content to the specified S3 output bucket.

def uploadOutput(bucket, output_key, json_content):
    """Uploads json to output bucket"""
    status = "SUCCESS"
    error_message = None

    try:
        s3.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json_content,
            ContentType='application/json'
        )
    except Exception as e:
        status = "FAILURE"
        error_message = str(e)

    return status, error_message

# Logs the processing result (success/failure) into an RDS MySQL database.

def logToDB(input_key, output_key, input_bucket, status, error_message):
    """Logs processing result to RDS MySQL"""
    try:
        conn = pymysql.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASS'],
            database=os.environ['DB_NAME'],
            connect_timeout=5
        )

        query = """
            INSERT INTO processing_logs
            (input_key, output_key, bucket_name, timestamp, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            input_key,
            output_key,
            input_bucket,        
            datetime.now(),
            status,
            error_message
        )

        with conn.cursor() as cursor:
            cursor.execute(query, values)

        conn.commit()

    except Exception as e:
        print("DB LOGGING ERROR:", str(e))

    finally:
        try:
            conn.close()
        except:
            pass

# Main AWS Lambda handler triggered by S3 upload event.
    
def lambda_handler(event, context):
    # TODO implement
            
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    output_bucket = input_bucket.replace("input", "output")
    input_key = event['Records'][0]['s3']['object']['key']
    output_key = input_key.replace(".csv", ".json")



    status = "SUCCESS"
    error_message = None
    try:
        data = extractDataFromCSV(input_bucket, input_key)
        json_content = convertToJSON(data)
        status, error_message = uploadOutput(output_bucket, output_key, json_content)
    except Exception as e:
        status = "FAILURE"
        error_message = str(e)
            

    logToDB(input_key, output_key, input_bucket, status, error_message)

    return {
        'statusCode': 200,
        'body': f'Conversion of {input_bucket}/{input_key} -----JSON TRANSFORMATION-----> {output_bucket}/{output_key}'
    }
