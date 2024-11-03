import unittest
from datawizzy.safety import SafetyChecker

class TestSafetyChecker(unittest.TestCase):
    def setUp(self):
        self.safety = SafetyChecker()

    def test_safe_content(self):
        content = "This is a safe instruction."
        self.assertTrue(self.safety.check_content(content))

    def test_unsafe_content(self):
        content = "import os\nos.system('rm -rf /')"
        self.assertFalse(self.safety.check_content(content))

if __name__ == '__main__':
    unittest.main()