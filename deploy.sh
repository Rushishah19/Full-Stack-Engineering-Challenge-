#!/bin/bash

# Deployment script for CloudFormation template

STACK_NAME="MusicFestivalBackend"
TEMPLATE_FILE="template.yaml"
REGION="us-east-1"

echo "Packaging and deploying CloudFormation stack..."

aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --template-file $TEMPLATE_FILE \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION

echo "Deployment complete."
