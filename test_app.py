import unittest
from App import app, ask_gemini
from unittest.mock import patch

class TestWhatsAppAgent(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_welcome_message(self):
        """Test if welcome message is sent for greeting inputs"""
        test_data = {'Body': 'hi', 'From': 'whatsapp:+1234567890'}
        response = self.app.post('/whatsapp', data=test_data)
        self.assertIn('Welcome to Mahaveer Securities', response.get_data(as_text=True))

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_gemini_response(self, mock_generate):
        """Test if Gemini API is called and response is processed"""
        # Mock Gemini response
        mock_generate.return_value.text = "This is a test response from Gemini"
        
        # Test normal query
        response = ask_gemini("What are your mutual fund services?")
        self.assertIsNotNone(response)
        self.assertEqual(response, "This is a test response from Gemini")

    def test_error_handling(self):
        """Test if errors are handled gracefully"""
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            response = ask_gemini("Test query")
            # Match the exact apostrophe character from the App.py file
            expected_error = "⚠️ Sorry, I couldn’t process that request. Error: API Error"
            self.assertEqual(response, expected_error)

if __name__ == '__main__':
    unittest.main()