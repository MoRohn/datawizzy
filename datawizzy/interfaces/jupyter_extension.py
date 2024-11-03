from IPython.core.magic import register_line_magic
from datawizzy.nlp_processor import NLPProcessor
from datawizzy.instruction_generator import InstructionGenerator
from datawizzy.safety import SafetyChecker
from IPython.display import display, Markdown

@register_line_magic
def datawizard(line):
    query = line.strip()
    nlp = NLPProcessor()
    safety = SafetyChecker()
    generator = InstructionGenerator()

    raw_instructions = nlp.generate_instructions(query)

    if safety.check_content(raw_instructions):
        instructions = generator.format_instructions(raw_instructions)
        display(Markdown(instructions))
    else:
        print("The generated content was deemed unsafe.")