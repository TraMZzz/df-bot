import json
import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

from src import sqs


class TestSqsLambda(unittest.TestCase):

    def setUp(self):
        self.event = {
            "Records": [
                {
                    "body": json.dumps(
                        {
                            "update_id": 123456,
                            "message": {"text": "/hello", "chat": {"id": 123}},
                        }
                    )
                }
            ]
        }
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def run_async(self, coro):
        return self.loop.run_until_complete(coro)

    @patch("src.sqs.ApplicationBuilder")
    @patch("src.sqs.asyncio")
    def test_lambda_handler(self, mock_asyncio, mock_ApplicationBuilder):
        # Prepare the mock for ApplicationBuilder and its chain of method calls
        mock_application_instance = MagicMock()
        mock_ApplicationBuilder.return_value.token.return_value.build.return_value = (
            mock_application_instance
        )

        # Mock the asyncio.get_event_loop().run_until_complete() call
        mock_loop = MagicMock()
        mock_asyncio.get_event_loop.return_value = mock_loop

        # Execute the lambda_handler
        sqs.lambda_handler(self.event, None)

        # Assertions to ensure the flow of execution as expected
        mock_ApplicationBuilder.return_value.token.assert_called_once_with("")
        mock_loop.run_until_complete.assert_called()

    @patch("src.sqs.ContextTypes.DEFAULT_TYPE")
    @patch("src.sqs.Update")
    def test_handle_command(self, mock_update, mock_context):
        # Mocking context.bot.send_message to be an AsyncMock
        mock_context.bot.send_message = MagicMock(return_value=asyncio.Future())
        mock_context.bot.send_message.return_value.set_result(True)

        # Call the async handle_command function
        self.run_async(sqs.handle_command(mock_update, mock_context))

        # Assert send_message was called with expected parameters
        mock_context.bot.send_message.assert_called_with(
            chat_id=mock_update.effective_chat.id, text="I don't understand."
        )

        # Reset the mock to simulate a different command
        mock_update.message.text = "/hello"

        # Call the async handle_command function
        self.run_async(sqs.handle_command(mock_update, mock_context))

        # Assert send_message was called with expected parameters
        mock_context.bot.send_message.assert_called_with(
            chat_id=mock_update.effective_chat.id, text="Hello! How can I help you?"
        )

    @patch("src.sqs.ContextTypes.DEFAULT_TYPE")
    @patch("src.sqs.Update")
    def test_handle_message(self, mock_update, mock_context):
        mock_context.bot.send_message = AsyncMock()
        mock_update.message.text = "hello"
        mock_update.effective_chat.id = 12345
        # Simulate calling handle_message with a message containing "hello"
        self.run_async(sqs.handle_message(mock_update, mock_context))

        # Assert send_message was called once with expected parameters
        mock_context.bot.send_message.assert_awaited_with(
            chat_id=12345, text="Hello there! Glad you messaged."
        )

        # Reset the mock to simulate a different message
        mock_update.message.text = "text"

        # Simulate calling handle_message with a message containing "hello"
        self.run_async(sqs.handle_message(mock_update, mock_context))

        # Assert send_message was called once with expected parameters
        mock_context.bot.send_message.assert_awaited_with(
            chat_id=12345, text="I don't understand."
        )


if __name__ == "__main__":
    unittest.main()
