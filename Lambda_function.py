import boto3
import json
import urllib.parse
import uuid
from datetime import datetime

rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = "ImageAnalysisResults"

table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    print("Received event:")
    print(json.dumps(event))

    for record in event["Records"]:

        bucket_name = record["s3"]["bucket"]["name"]

        object_key = urllib.parse.unquote_plus(
            record["s3"]["object"]["key"]
        )

        print(f"Bucket: {bucket_name}")
        print(f"Image: {object_key}")

        response = rekognition.detect_labels(
            Image={
                "S3Object": {
                    "Bucket": bucket_name,
                    "Name": object_key
                }
            },
            MaxLabels=10,
            MinConfidence=80
        )

        labels = []

        for label in response["Labels"]:

            labels.append({
                "name": label["Name"],
                "confidence": round(label["Confidence"], 2)
            })

        image_id = str(uuid.uuid4())

        table.put_item(
            Item={
                "image_id": image_id,
                "image_name": object_key,
                "bucket": bucket_name,
                "labels": json.dumps(labels),
                "processed_at": datetime.utcnow().isoformat()
            }
        )

        print("Analysis result:")
        print(json.dumps(labels))

    return {
        "statusCode": 200,
        "body": json.dumps("Image analyzed successfully")
    }
