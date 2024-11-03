import re

class SafetyChecker:
    def check_content(self, content):
        # Simple disallowed content check
        disallowed_patterns = [
            r"import\s+os",
            r"import\s+sys",
            r"exec\(",
            r"eval\(",
            r"subprocess",
        ]
        for pattern in disallowed_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        return True

    def check_code(self, code):
        # Analyze code for potential security risks
        # Implement additional static code analysis if needed
        return self.check_content(code)
