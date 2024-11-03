import streamlit as st
from datawizzy.nlp_processor import NLPProcessor
from datawizzy.instruction_generator import InstructionGenerator
from datawizzy.safety import SafetyChecker
import json
import os

def initialize_components(model_provider: str):
    try:
        nlp = NLPProcessor(model_provider=model_provider)
        safety = SafetyChecker()
        generator = InstructionGenerator()
        return nlp, safety, generator
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        st.stop()

def add_chat_css():
    st.markdown(
        """
        <style>
        /* Set the entire page background color */
        .chat-container {
            background-color: #0F1116
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .user-message {
            background-color: #333333;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            max-width: 75%;
            align-self: flex-end;
        }
        .ai-message {
            background-color: #41424C;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            max-width: 90%;
            align-self: flex-start;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
        }
        .need-more-info-button {
            align-self: flex-start;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def display_conversation():
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message['role'] == 'user':
                st.markdown(
                    f"<div class='chat-container'><div class='user-message'><strong>You:</strong> {message['content']}</div></div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"<div class='chat-container'><div class='ai-message'><strong>DataWizzy:</strong> {message['content']}</div></div>",
                    unsafe_allow_html=True
                )
                # Check if a detailed response has already been requested for this message
                if not st.session_state.detailed_requested.get(i, False):
                    if st.button('Need More Info', key=f'need_more_info_{i}'):
                        handle_need_more_info(i)

def save_conversation():
    """
    Saves the current conversation history to a JSON file.
    """
    try:
        with open('conversation_history.json', 'w') as f:
            json.dump(st.session_state.messages, f, indent=4)
        st.success("Conversation history saved successfully!")
    except Exception as e:
        st.error(f"Error saving conversation history: {e}")

def load_conversation():
    """
    Loads the conversation history from a JSON file.
    """
    if os.path.exists('conversation_history.json'):
        try:
            with open('conversation_history.json', 'r') as f:
                st.session_state.messages = json.load(f)
            st.success("Conversation history loaded successfully!")
        except Exception as e:
            st.error(f"Error loading conversation history: {e}")
    else:
        st.warning("No saved conversation history found.")

def handle_need_more_info(message_index):
    corresponding_user_query = ""
    for j in range(message_index-1, -1, -1):
        if st.session_state.messages[j]['role'] == 'user':
            corresponding_user_query = st.session_state.messages[j]['content']
            break
    if not corresponding_user_query:
        st.error("Original user query not found.")
        return
    
    # Generate the detailed AI response
    with st.spinner('Generating more detailed information...'):
        try:
            # Pass the entire conversation history as a list of dictionaries
            detailed_instructions = st.session_state.nlp.generate_detailed_instructions(
                corresponding_user_query,
                st.session_state.messages  # Correctly pass as list of dicts
            )
        except Exception as e:
            st.error(f"Error generating detailed instructions: {e}")
            return
    
    # Safety check
    try:
        if st.session_state.safety.check_content(detailed_instructions):
            instructions = st.session_state.generator.format_instructions(detailed_instructions)
            ai_message = instructions
        else:
            ai_message = "I'm sorry, but I can't provide more details on that request."
    except Exception as e:
        st.error(f"Error during safety check: {e}")
        return
    
    # Append the detailed AI response to the conversation history
    st.session_state.messages.append({'role': 'assistant', 'content': ai_message})
    
    # Mark that a detailed response has been requested for this message
    st.session_state.detailed_requested[message_index] = True
    
    # Rerun the app to display the new message
    st.rerun()

def main():
    # Set the page configuration
    st.set_page_config(page_title="DataWizzy", page_icon="🤓", layout="wide")
    
    # Define the path to the header image
    header_image_path = os.path.join("datawizzy", "assets", "header.png")  # Update with your actual image path
    
    # Display the header image
    if os.path.exists(header_image_path):
        st.image(header_image_path, use_column_width=False)
    else:
        st.error(f"Header image not found at path: {header_image_path}")
        st.title("🤓 DataWizzy")  # Fallback to text title
    
    st.markdown("## Ask your data science questions and get assistance in real-time!")

    # Sidebar components
    with st.sidebar:
        # Define the path to the sidebar image
        sidebar_image_path = os.path.join("datawizzy", "assets", "sidebar.png")  # Update with your actual image path
        
        # Display the sidebar image
        if os.path.exists(sidebar_image_path):
            st.image(sidebar_image_path, use_column_width=True)
        else:
            st.error(f"Sidebar image not found at path: {sidebar_image_path}")
        
        # Sidebar model selection
        model_provider = st.selectbox(
            "Select LLM Provider",
            ("openai", "ollama")
        )

        # Add Save and Load buttons
        st.header("Conversation Management")
        if st.button("Save Conversation"):
            save_conversation()
        if st.button("Load Conversation"):
            load_conversation()
    
    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'detailed_requested' not in st.session_state:
        st.session_state.detailed_requested = {}
    if 'nlp' not in st.session_state or 'safety' not in st.session_state or 'generator' not in st.session_state:
        nlp, safety, generator = initialize_components(model_provider)
        st.session_state.nlp = nlp
        st.session_state.safety = safety
        st.session_state.generator = generator
    
    # Add custom CSS
    add_chat_css()
    
    # Display the conversation history
    display_conversation()
    
    # User input
    with st.form(key='user_input_form', clear_on_submit=True):
        user_input = st.text_input("Type your message here...", key='input')
        submit_button = st.form_submit_button(label='Send')
    
    if submit_button and user_input:
        # Add the user's message to the conversation history
        st.session_state.messages.append({'role': 'user', 'content': user_input})
    
        # Generate the AI's response
        with st.spinner('DataWizzy is typing...'):
            try:
                # Pass the entire conversation history as a list of dictionaries
                raw_instructions = st.session_state.nlp.generate_concise_response(
                    user_input,
                    st.session_state.messages  # Correctly pass as list of dicts
                )
            except ValueError as ve:
                st.error(f"Input validation error: {ve}")
                return
            except Exception as e:
                st.error(f"Error generating instructions: {e}")
                return
    
        # Safety check
        try:
            if st.session_state.safety.check_content(raw_instructions):
                instructions = st.session_state.generator.format_instructions(raw_instructions)
                ai_message = instructions
            else:
                ai_message = "I'm sorry, but I can't assist with that request."
        except Exception as e:
            st.error(f"Error during safety check: {e}")
            return
    
        # Add the AI's response to the conversation history
        st.session_state.messages.append({'role': 'assistant', 'content': ai_message})
    
        # Rerun the app to display the updated conversation
        st.rerun()

if __name__ == "__main__":
    main()