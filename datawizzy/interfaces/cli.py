import argparse
from datawizzy.nlp_processor import NLPProcessor
from datawizzy.instruction_generator import InstructionGenerator
from datawizzy.safety import SafetyChecker

def main():
    parser = argparse.ArgumentParser(description='DataWizzy CLI')
    parser.add_argument('query', type=str, help='Your data science question')
    args = parser.parse_args()

    nlp = NLPProcessor()
    safety = SafetyChecker()
    generator = InstructionGenerator()

    raw_instructions = nlp.generate_instructions(args.query)

    if safety.check_content(raw_instructions):
        instructions = generator.format_instructions(raw_instructions)
        print(instructions)
    else:
        print("The generated content was deemed unsafe.")

if __name__ == '__main__':
    main()
