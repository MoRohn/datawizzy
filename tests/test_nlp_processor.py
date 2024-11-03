import unittest
from datawizzy.nlp_processor import NLPProcessor
from unittest.mock import patch

class TestNLPProcessor(unittest.TestCase):
    @patch('datawizard.nlp_processor.openai.Completion.create')
    def test_generate_instructions(self, mock_create):
        mock_create.return_value.choices = [type('',(object,),{'text':'Sample response'})()]
        nlp = NLPProcessor()
        result = nlp.generate_instructions('Sample query')
        self.assertEqual(result, 'Sample response')

if __name__ == '__main__':
    unittest.main()