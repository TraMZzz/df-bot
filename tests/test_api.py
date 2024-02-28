import json
import logging
import unittest
from unittest.mock import patch, MagicMock

from src import api


class TestApiLambda(unittest.TestCase):
    def setUp(self):
        self.mock_sqs_resource = MagicMock()
        self.telegram_update = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "chat": {"id": 123, "type": "private"},
                "text": "Hello, world!",
                "date": 1609459200,
                "entities": [],
                "explanation": "This is a test update",
            },
        }
        self.expected_minimal_data = {
            "update_id": 123456,
            "message": {
                "message_id": 1,
                "chat": {"id": 123, "type": "private"},
                "text": "Hello, world!",
                "date": 1609459200,
                "entities": [],
            },
        }

    @patch("src.api.queue.send_message")
    def test_lambda_handler_success(self, mock_send_message):
        mock_send_message.return_value = {"MessageId": "some-message-id"}
        event = {"body": json.dumps(self.telegram_update)}
        result = api.lambda_handler(event, None)
        self.assertEqual(result, {"statusCode": 200, "body": "Success"})
        mock_send_message.assert_called_once()

    def test_lambda_handler_failure(self):
        logging.getLogger().setLevel(logging.CRITICAL + 1)
        event = {"body": ""}
        result = api.lambda_handler(event, None)
        self.assertEqual(result, {"statusCode": 500, "body": "Failure"})

    def test_extract_minimal_data(self):
        result = api.extract_minimal_data(self.telegram_update)
        self.assertEqual(result, self.expected_minimal_data)


if __name__ == "__main__":
    unittest.main()
