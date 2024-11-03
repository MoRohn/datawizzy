class InstructionGenerator:
    def format_instructions(self, raw_text):
        # Split the raw text into steps and format code blocks
        lines = raw_text.split('\n')
        formatted_lines = []
        for line in lines:
            if line.strip().startswith('```') or line.strip().endswith('```'):
                formatted_lines.append(line)
            elif line.strip().startswith('import') or '=' in line:
                formatted_lines.append(f'```python\n{line}\n```')
            else:
                formatted_lines.append(line)
        return '\n'.join(formatted_lines)
