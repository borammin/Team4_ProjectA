import json

#for dealing with S3 buckets
import boto3

#for uploading metadata to db
import pymysql
from datetime import datetime
import os

s3 = boto3.client('s3', region_name="us-east-1")



def convertToJSON(data):
    """Takes the rows of data and turn it into json data"""
    json_content = json.dumps(data, indent=3)

    return json_content.encode('utf-8')


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




def logToDB(input_key, output_key, bucket_name, status, error_message):
    """logs the file conversion attempt in the database"""

    query = """INSERT INTO processing_logs 
    (input_key, output_key, bucket_name, datetime, status, error_message) 
    VALUES (%s, %s, %s, %s, %s, %s)"""
    values = (input_key, output_key, bucket_name, datetime.now(), status, error_message)
    
    DB_HOST= os.environ['DB_HOST']
    DB_USER= os.environ['DB_USER']
    DB_PASS= os.environ['DB_PASS']
    DB_NAME= os.environ['DB_NAME']

    conn = pymysql.connect(
        host=DB_HOST, 
        user=DB_USER, 
        password=DB_PASS, 
        database=DB_NAME
        )
    with conn.cursor() as cursor:
        cursor.execute(query, values)
    conn.commit()
    conn.close()

def lambda_handler(event, context):
    # TODO implement
            
    #TODO get the bucket name, input_key, and make output_key based on input_key from the event handler

    #TODO read in the csv and extract the row data, extractCSV_Data(bucket, input_key)

    json_content = convertToJSON(data)

    status, error_message = uploadOutput(bucket, output_key, json_content)

    logToDB(input_key, output_key, bucket, status, error_message)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
