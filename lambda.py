# Lambda Function 1: serializeImageData.py

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    print("Event:", event)
    
    # Get the s3 address from the Step Function event input
    key = event["s3_key"]
    bucket = event["s3_bucket"]
    
    # Download the data from s3 to /tmp/image.png
    boto3.resource('s3').Bucket(bucket).download_file(key, "/tmp/image.png")
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

#######################################################

# Lambda Function 2: classifyImages.py

import os

import boto3
import json
import base64
import io

# Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2024-08-12-13-18-35-092"  ## TODO: fill in

runtime = boto3.Session().client('sagemaker-runtime')

def lambda_handler(event, context):

    image = base64.b64decode(event["body"]["image_data"])
    
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT, 
        ContentType='application/x-image', 
        Body=image
    )
    
    inferences = response["Body"].read().decode('utf-8')
    
    event["inferences"] = inferences

    return {
        'statusCode': 200,
        'body': {
            "inferences": json.loads(inferences)    
        }
    }

#######################################################

# Lambda Function 3: filterInferences.py

import json


THRESHOLD = .70


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event['body']["inferences"]  ## TODO: fill in
    
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = max(inferences) > THRESHOLD    ## TODO: fill in
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }