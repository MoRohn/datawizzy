import openai
import logging
import time
from typing import List, Optional, Dict
from .setup import load_config
import os

try:
    import ollama
except ImportError:
    ollama = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self, config_path: str = 'config.json', model_provider: str = 'openai'):
        """
        Initializes the NLPProcessor with either OpenAI or Ollama based on the configuration.

        Parameters:
            config_path (str): The path to the configuration file.
            model_provider (str): The LLM provider to use ('openai' or 'ollama').
        """
        # Load configuration
        config = load_config(config_path)
        
        # Select model provider
        self.model_provider = model_provider.lower()
        
        if self.model_provider == 'openai':
            # Retrieve OpenAI API credentials from the configuration
            self.api_key = config.get('OPENAI_API_KEY')
            self.org_id = config.get('OPENAI_ORG_ID')
            self.proj_id = config.get('OPENAI_PROJECT_ID')
            
            if not self.api_key:
                logger.error("OPENAI_API_KEY not found in the configuration file.")
                raise ValueError("OPENAI_API_KEY not found in the configuration file.")
            
            # Set the OpenAI API key and organization
            openai.api_key = self.api_key
            if self.org_id:
                openai.organization = self.org_id
            
            # Set the OpenAI model name
            self.MODEL = "gpt-4o-mini"  # Update to your desired OpenAI model
            logger.info("OpenAI API client initiated.")
        
        elif self.model_provider == 'ollama':
            # Ensure the Ollama module is available
            if ollama is None:
                raise ImportError("The Ollama package is not installed. Please install it to use Ollama as the model provider.")
            self.MODEL = "llama2"  # Update to your desired Ollama model
            logger.info("Ollama API client initiated.")
        
        else:
            raise ValueError("Invalid model provider. Please use 'openai' or 'ollama'.")

    def _validate_inputs(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]]
    ):
        """
        Validates the inputs for instruction generation methods.

        Parameters:
            query (str): The user's query.
            conversation_history (Optional[List[dict]]): Previous conversation history.

        Raises:
            ValueError: If any input is invalid.
        """
        if not isinstance(query, str) or not query.strip():
            logger.error("Invalid query: Must be a non-empty string.")
            raise ValueError("Query must be a non-empty string.")
        
        if conversation_history is not None:
            if not isinstance(conversation_history, list):
                logger.error("Invalid conversation_history: Must be a list of dictionaries.")
                raise ValueError("conversation_history must be a list of dictionaries.")
            for message in conversation_history:
                if not isinstance(message, dict) or 'role' not in message or 'content' not in message:
                    logger.error("Each message in conversation_history must be a dict with 'role' and 'content' keys.")
                    raise ValueError("Each message must be a dict with 'role' and 'content'.")

    def _generate_response_openai(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float,
        frequency_penalty: float,
        presence_penalty: float,
        stop: Optional[List[str]]
    ) -> str:
        response = openai.ChatCompletion.create(
            model=self.MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop
        )
        return response.choices[0].message['content'].strip()

    def _generate_response_ollama(
        self,
        prompt: str,
        max_tokens: int
    ) -> str:
        # Assuming Ollama supports similar parameters; adjust as needed.
        response = ollama.complete(model=self.MODEL, prompt=prompt, max_tokens=max_tokens)
        return response["response"]

    def _generate_response(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.5,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.6,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Generates a response using either OpenAI or Ollama based on the selected model provider.
        """
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        if self.model_provider == 'openai':
            return self._generate_response_openai(
                messages, max_tokens, temperature, top_p, frequency_penalty, presence_penalty, stop
            )
        elif self.model_provider == 'ollama':
            return self._generate_response_ollama(prompt, max_tokens)
        else:
            raise ValueError("Unsupported model provider.")

    def generate_concise_response(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 300  # Reduced tokens for concise response
    ) -> str:
        """
        Generates a concise and generalized response based on the user's query.
        """
        # Set default conversation_history to empty list if None
        if conversation_history is None:
            conversation_history = []
        
        # Validate inputs
        self._validate_inputs(query, conversation_history)
        
        messages = [
            {"role": "system", "content": "You are an AI assistant specializing in data science and Python programming. Provide clear and concise explanations."}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": query})
        
        user_prompt = (
            "Provide a clear and concise explanation of how to accomplish the user's request using "
            "Python, pandas, and matplotlib. Focus on educating the user without delving into excessive detail."
        )
        messages.append({"role": "user", "content": user_prompt})
        
        return self._generate_response(messages, max_tokens=max_tokens)

    def generate_detailed_instructions(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 1500
    ) -> str:
        """
        Generates a more detailed, in-depth instructional guide based on the user's query.
        """
        # Set default conversation_history to empty list if None
        if conversation_history is None:
            conversation_history = []
        
        # Validate inputs
        self._validate_inputs(query, conversation_history)
        
        messages = [
            {"role": "system", "content": "You are an AI assistant specializing in data science and Python programming."}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": query})
        
        user_prompt = (
            "The user has requested more detailed instructions. Provide an even more comprehensive, step-by-step guide "
            "on how to accomplish the user's request using Python, pandas, and matplotlib. Include additional code snippets, "
            "in-depth explanations, best practices, and potential pitfalls to watch out for."
        )
        messages.append({"role": "user", "content": user_prompt})
        
        return self._generate_response(messages, max_tokens=max_tokens)