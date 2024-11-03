import subprocess
import sys
import os

def main():
    # Determine the path to the web_app.py script
    script_path = os.path.join(os.path.dirname(__file__), 'web_app.py')
    
    # Run the Streamlit app using subprocess
    subprocess.run(['streamlit', 'run', script_path] + sys.argv[1:])

if __name__ == '__main__':
    main()