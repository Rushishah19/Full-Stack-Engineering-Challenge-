import json
import boto3
import os
from botocore.exceptions import ClientError
from decimal import Decimal

# Get region from environment variable or use default
REGION = os.getenv('AWS_REGION', 'us-east-1')

# AWS clients with region specified
s3 = boto3.client('s3', region_name=REGION)
dynamodb = boto3.resource('dynamodb', region_name=REGION)
sns = boto3.client('sns', region_name=REGION)

# Environment configuration
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 'Performances')
TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:123456789012:musicFestivalStatus')

def lambda_handler(event, context=None):
    print("Lambda handler triggered.")
    table = dynamodb.Table(TABLE_NAME)

    try:
        for record in event['Records']:
            print("Processing record from SQS...")

            # Parse message from SQS
            message = json.loads(record['body'])
            s3_info = message['Records'][0]['s3']
            bucket = s3_info['bucket']['name']
            key = s3_info['object']['key']

            print(f"Reading file from S3: s3://{bucket}/{key}")

            # Fetch and parse the S3 object (JSON)
            obj = s3.get_object(Bucket=bucket, Key=key)
            data = json.loads(obj['Body'].read())

            print(f"Inserting {len(data)} records into DynamoDB table: {TABLE_NAME}")

            with table.batch_writer() as batch:
                for entry in data:
                    batch.put_item(Item={
                        'Performer': entry['Performer'],
                        'Date#StartTime': f"{entry['Date']}#{entry['Start']}",
                        'Stage': entry['Stage'],
                        'Start': entry['Start'],
                        'End': entry['End'],
                        'Date': entry['Date'],
                        'PopularityScore': Decimal(str(entry.get('PopularityScore', 0)))
                    })

        # Success notification
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="Upload Success",
            Message="Performance data successfully added to DynamoDB."
        )
        print("Upload success notification sent.")

    except Exception as e:
        # Error notification
        error_message = f"Error processing file: {str(e)}"
        print(error_message)
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject="Upload Failed",
            Message=error_message
        )
        raise

# Local testing block
if __name__ == "__main__":
    with open("event.json") as f:
        test_event = json.load(f)

    lambda_handler(test_event)