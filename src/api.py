import json
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")

sqs = boto3.resource("sqs")
queue = sqs.Queue(SQS_QUEUE_URL)


def extract_minimal_data(telegram_update):
    """
    Extracts minimal data from a Telegram update.
    """
    # Initialize the minimal payload with update_id
    minimal_payload = {
        "update_id": telegram_update["update_id"],
        "message": {
            "message_id": telegram_update["message"]["message_id"],
            "chat": telegram_update["message"]["chat"],
            "text": telegram_update["message"]["text"],
            "date": telegram_update["message"]["date"],
        },
    }

    # Include entities in the message if they exist
    if "entities" in telegram_update["message"]:
        minimal_payload["message"]["entities"] = telegram_update["message"]["entities"]

    return minimal_payload


def lambda_handler(event, context):
    logger.info("Event: %s", json.dumps(event))
    try:
        # Assuming event['body'] is the raw Telegram update
        telegram_update = json.loads(event["body"])

        # Extract the minimal data required
        minimal_payload = extract_minimal_data(telegram_update)

        # Send the minimal data to the SQS queue
        response = queue.send_message(MessageBody=json.dumps(minimal_payload))
        logger.info("Message sent to SQS: %s", response.get("MessageId"))

        return {"statusCode": 200, "body": "Success"}

    except Exception as exc:
        logger.error("Failed to process Telegram update: %s", exc, exc_info=True)
        return {"statusCode": 500, "body": "Failure"}
