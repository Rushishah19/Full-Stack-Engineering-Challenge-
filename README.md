# Music Festival Lineup Backend Service

## Overview
This backend service processes JSON uploads of music festival performance data. It uses AWS S3, SQS, Lambda, DynamoDB, and SNS to build a secure, scalable, and serverless solution.

## Architecture
```
S3 (file upload)
  └──> SQS Queue (event trigger)
        └──> Lambda (process file & save to DynamoDB)
               └──> SNS (send notification)
```

## Components
- **S3 Bucket**: Accepts performance data files in JSON format.
- **SQS Queue**: Decouples Lambda from S3 events.
- **Lambda**: Parses JSON and inserts data into DynamoDB.
- **DynamoDB**: Stores performance data.
- **SNS**: Sends email notifications for success/failure.

## DynamoDB Schema
- **Table Name**: `Performances`
- **Primary Key**: 
  - Partition Key: `Performer`
  - Sort Key: `Date#StartTime`
- **GSI 1**: `Stage-Date-Start`
  - Partition Key: `Stage`
  - Sort Key: `Date#StartTime`
- **GSI 2**: `Date-Time`
  - Partition Key: `Date`
  - Sort Key: `Start`

## Supported Queries
- All performances by a performer
- Performances on a stage within a time range
- Performances on a given date/time

## Assumptions
- Input JSON is well-formed and trusted.
- No overlap/time validation logic needed.

## Cost & Scalability Analysis
| Records/Day | Approx Data | Monthly Cost Estimate |
|-------------|--------------|------------------------|
| 1,000       | ~50KB/day    | ≈ Free Tier          |
| 10,000      | ~500KB/day   | < $1 (mainly Lambda + Dynamo) |
| 100,000     | ~5MB/day     | ≈ $3-5, optimize with batch writes |

## Security & IAM
- Lambda Role:
  - Read from S3
  - Write to DynamoDB
  - Publish to SNS
- S3:
  - Event triggers only for `ObjectCreated`
- SNS:
  - Accepts messages only from Lambda

## Popularity Score Bonus
If `PopularityScore` is added, you can:
- Use `Scan + FilterExpression` (if volume is low)
- Or add another GSI: 
  - PK: `Date`, SK: `PopularityScore`

```python
response = table.scan(FilterExpression=Attr('PopularityScore').gt(80))
```

## Setup Instructions
1. Deploy the infrastructure using CloudFormation (see template).
2. Upload JSON to S3.
3. Watch logs and check email for notifications.

---

## Project Structure
```
/
├── lambda_function.py
├── README.md
└── template.yaml
```
