import pymysql
import sys
import os

DB_HOST = os.environ.get('DB_HOST', 'ds2002.cgls84scuy1e.us-east-1.rds.amazonaws.com')
DB_USER = os.environ.get('DB_USER', 'xyb9vz')
DB_PASS = os.environ.get('DB_PASS', 'xyb9vz')
DB_NAME = os.environ.get('DB_NAME', 'team4')


def query_file(file_or_prefix):
    """Query the processing_logs table for a given filename or prefix."""
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            connect_timeout=5
        )

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT input_key, output_key, bucket_name, timestamp, status, error_message
                FROM processing_logs
                WHERE input_key LIKE %s
                ORDER BY timestamp DESC
            """, (f"%{file_or_prefix}%",))

            rows = cursor.fetchall()

        conn.close()
        return rows

    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 query.py <filename_or_prefix>")
        print("Example: python3 query.py my_data.csv")
        print("Example: python3 query.py sales_")
        sys.exit(1)

    search = sys.argv[1]
    print(f"\nSearching for: '{search}'\n")

    rows = query_file(search)

    if not rows:
        print(f"No records found for '{search}'. The file may not have been processed yet.")
        sys.exit(0)

    print(f"Found {len(rows)} result(s):\n")
    print(f"{'Input Key':<40} {'Output Key':<40} {'Bucket':<25} {'Timestamp':<22} {'Status':<10} {'Error'}")
    print("-" * 160)

    for row in rows:
        input_key, output_key, bucket_name, timestamp, status, error_message = row
        error = error_message if error_message else "None"
        print(f"{input_key:<40} {output_key:<40} {bucket_name:<25} {str(timestamp):<22} {status:<10} {error}")


if __name__ == "__main__":
    main()