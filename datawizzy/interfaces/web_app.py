import streamlit as st
from datawizzy.nlp_processor import NLPProcessor
from datawizzy.instruction_generator import InstructionGenerator
from datawizzy.safety import SafetyChecker

def main():
    # Initialize session state variables
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Set page configuration
    st.set_page_config(page_title="DataWizard AI Chatbot", page_icon="💬", layout="wide")
    
    # Custom CSS for chat bubbles
    def add_chat_css():
        st.markdown(
            """
            <style>
            .user-message {
                background-color: #DCF8C6;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                max-width: 70%;
                align-self: flex-end;
            }
            .ai-message {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                max-width: 70%;
                align-self: flex-start;
            }
            .chat-container {
                display: flex;
                flex-direction: column;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    
    add_chat_css()
    
    st.title("💬 DataWizard AI Chatbot")
    st.write("Ask your data science questions and get assistance in real-time!")
    
    # Display the conversation history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.markdown(f"<div class='chat-container'><div class='user-message'><strong>You:</strong> {message['content']}</div></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-container'><div class='ai-message'><strong>DataWizard AI:</strong> {message['content']}</div></div>", unsafe_allow_html=True)
    
    # User input
    with st.form(key='user_input_form', clear_on_submit=True):
        user_input = st.text_input("Type your message here...", key='input')
        submit_button = st.form_submit_button(label='Send')
    
    if submit_button and user_input:
        # Add the user's message to the conversation history
        st.session_state.messages.append({'role': 'user', 'content': user_input})
    
        # Instantiate your classes
        nlp = NLPProcessor()
        safety = SafetyChecker()
        generator = InstructionGenerator()
    
        # Prepare conversation history for context
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
    
        # Generate the AI's response
        with st.spinner('DataWizard AI is typing...'):
            raw_instructions = nlp.generate_instructions(user_input, conversation_history)
    
        # Safety check
        if safety.check_content(raw_instructions):
            instructions = generator.format_instructions(raw_instructions)
            ai_message = instructions
        else:
            ai_message = "I'm sorry, but I can't assist with that request."
    
        # Add the AI's response to the conversation history
        st.session_state.messages.append({'role': 'assistant', 'content': ai_message})
    
        # Rerun the app to display the updated conversation
        st.experimental_rerun()