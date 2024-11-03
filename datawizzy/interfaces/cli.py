import argparse
import sys
from datawizzy.nlp_processor import NLPProcessor
from datawizzy.instruction_generator import InstructionGenerator
from datawizzy.safety import SafetyChecker
import textwrap
import logging

def setup_logging():
    logging.basicConfig(
        filename='datawizzy.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='DataWizzy CLI - Ask data science questions and receive AI-powered assistance.',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent('''\
            Examples:
              python cli.py "How can I visualize a pandas DataFrame using matplotlib?"
              python cli.py -q "Best practices for data cleaning in Python." --verbose
            ''')
    )
    parser.add_argument(
        '-q', '--query',
        type=str,
        help='Your data science or analytical question',
        required=True
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    return parser.parse_args()

def initialize_components(verbose=False):
    try:
        if verbose:
            print("[DEBUG] Initializing NLPProcessor...")
        nlp = NLPProcessor()
        if verbose:
            print("[DEBUG] Initializing SafetyChecker...")
        safety = SafetyChecker()
        if verbose:
            print("[DEBUG] Initializing InstructionGenerator...")
        generator = InstructionGenerator()
        return nlp, safety, generator
    except Exception as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)

def display_response(title, content, verbose=False):
    print(f"\n**{title}:**\n")
    print(content)

def main():
    setup_logging()
    logging.info("DataWizzy CLI started.")
    
    args = parse_arguments()

    if args.verbose:
        print("[DEBUG] Parsing arguments...")

    nlp, safety, generator = initialize_components(verbose=args.verbose)

    conversation_history = f"User: {args.query}"

    # Generate initial instructions
    if args.verbose:
        print("[DEBUG] Generating initial instructions...")
    try:
        raw_instructions = nlp.generate_instructions(args.query, conversation_history)
    except Exception as e:
        print(f"Error generating instructions: {e}")
        sys.exit(1)

    # Safety check for initial instructions
    if safety.check_content(raw_instructions):
        instructions = generator.format_instructions(raw_instructions)
        display_response("DataWizzy AI", instructions, verbose=args.verbose)
    else:
        display_response("DataWizzy AI", "The generated content was deemed unsafe.", verbose=args.verbose)
        sys.exit(1)

    # Prompt for more information
    while True:
        user_choice = input("\nDo you need more detailed information? (yes/no): ").strip().lower()
        if user_choice in ['yes', 'y']:
            if args.verbose:
                print("[DEBUG] Generating detailed instructions...")
            try:
                detailed_instructions = nlp.generate_detailed_instructions(args.query, conversation_history)
            except Exception as e:
                print(f"Error generating detailed instructions: {e}")
                break

            # Safety check for detailed instructions
            if safety.check_content(detailed_instructions):
                detailed = generator.format_instructions(detailed_instructions)
                display_response("DataWizzy AI (Detailed)", detailed, verbose=args.verbose)
            else:
                display_response("DataWizzy AI", "The detailed content was deemed unsafe.", verbose=args.verbose)
            break
        elif user_choice in ['no', 'n']:
            print("Thank you for using DataWizzy!")
            break
        else:
            print("Please enter 'yes' or 'no'.")

if __name__ == '__main__':
    main()
