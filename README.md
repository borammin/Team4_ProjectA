# Team4_ProjectA: Project A: File Converter
**Team Name:** TuffCloud
**Team Members:** Boram Min, Ryan Kim, Hayden Robinette, Nimisha Vadlamudi
**Course:** DS2002

## Project Overview
* This project implements an event-driven data pipeline that automatically converts uploaded CSV files into JSON format using AWS services. When a file is uploaded to a specific S3 input folder, it automatically triggers a cloud function that processes the conversion, stores the output, and logs the metadata in a relational database.
---

## Installation/building

### 1. Storage Configuration 
Create an S3 bucket with the following directory structure:
* `s3://ds2002-team4-project/input/`
* `s3://ds2002-team4-project/output/`

### 2. Database Initialization 
Connect to your RDS instance and run the following SQL script to initialize the logging table:
```sql
CREATE TABLE processing_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_key VARCHAR(255),
    output_key VARCHAR(255),
    bucket_name VARCHAR(100),
    timestamp DATETIME,
    status VARCHAR(20),
    error_message TEXT
);
```

### 3. Compute Environment 
* IAM Role: Create a role for Lambda with permissions for S3:GetObject, S3:PutObject, and RDS:ExecuteStatement.
* Trigger: Add an S3 Event Notification to the bucket. Set the event type to All object create events and the prefix to input/.
* Environment: Ensure the Lambda has access to the pymysql library.

## Usage
### Running the Pipeline -
* Upload any .csv file to the input/ prefix of your S3 bucket.
``` aws s3 cp my_data.csv s3://your-bucket-name/input/ ```
### Querying Results - To check if a specific file has been processed and find its output location
``` python3 query.py my_data.csv ```

## Notes 

### Architecture
* **Storage:** AWS S3 
* **Compute:** AWS Lambda (event-driven compute)
* **Database:** AWS RDS MySQL
  
### Pipeline Logic
1. Extract: Lambda is triggered by the S3 event, capturing the bucket name and object key. It downloads the CSV content into memory.
2. Transform: Uses the csv.DictReader pattern to parse the CSV rows into a list of Python dictionaries.
3. Load: Uploads the serialized JSON data to the output/ prefix in S3.
  * Uses pymysql to insert a record into the RDS processing_logs table including the timestamp and     status.

### Key Design Choices
* Event-driven architecture: By using S3 triggers and Lambda, the system only consumes compute resources when a file is actually present
* Relational logging: Enables easy querying and tracking

### Algorithms / Logic
- Uses Python csv.DictReader to parse CSV into dictionaries
- Converts list of dictionaries into JSON format
- Maps filenames from input/ to output/ automatically

### Goals
- Fully automated file processing pipeline
- Reliable logging of success/failure states
- Easy querying of processed files

### TODO / Improvements
- Add error logging to database 
- Add support for additional formats
