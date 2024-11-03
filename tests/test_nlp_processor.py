import unittest
from unittest.mock import patch, MagicMock
from datawizzy.nlp_processor import NLPProcessor

class TestNLPProcessor(unittest.TestCase):
    @patch('your_module.openai.ChatCompletion.create')
    def test_generate_instructions_success(self, mock_create):
        # Mock OpenAI response
        mock_create.return_value = MagicMock(
            choices=[MagicMock(message={'content': 'Test response'})]
        )
        processor = NLPProcessor(config_path='test_config.json')
        conversation_history = [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": "Tell me about data analysis."}
        ]
        response = processor.generate_instructions(
            query="How can I visualize data using matplotlib?",
            conversation_history=conversation_history,
            max_tokens=1000
        )
        self.assertEqual(response, "Test response")

    def test_validate_inputs_invalid_conversation_history_type(self):
        processor = NLPProcessor(config_path='test_config.json')
        with self.assertRaises(ValueError) as context:
            processor.generate_instructions(
                query="Test query",
                conversation_history="This should be a list, not a string."
            )
        self.assertIn("Conversation history must be a list of message dictionaries.", str(context.exception))

    def test_validate_inputs_invalid_message_structure(self):
        processor = NLPProcessor(config_path='test_config.json')
        # Missing 'role' key
        conversation_history = [
            {"content": "Missing role key."}
        ]
        with self.assertRaises(ValueError) as context:
            processor.generate_instructions(
                query="Test query",
                conversation_history=conversation_history
            )
        self.assertIn("Each message must contain 'role' and 'content' keys.", str(context.exception))

    def test_validate_inputs_invalid_role(self):
        processor = NLPProcessor(config_path='test_config.json')
        conversation_history = [
            {"role": "invalid_role", "content": "Invalid role."}
        ]
        with self.assertRaises(ValueError) as context:
            processor.generate_instructions(
                query="Test query",
                conversation_history=conversation_history
            )
        self.assertIn("Message 'role' must be 'system', 'user', or 'assistant'.", str(context.exception))

    def test_validate_inputs_invalid_content_type(self):
        processor = NLPProcessor(config_path='test_config.json')
        conversation_history = [
            {"role": "user", "content": 12345}  # content should be a string
        ]
        with self.assertRaises(ValueError) as context:
            processor.generate_instructions(
                query="Test query",
                conversation_history=conversation_history
            )
        self.assertIn("Message 'content' must be a string.", str(context.exception))

if __name__ == '__main__':
    unittest.main()