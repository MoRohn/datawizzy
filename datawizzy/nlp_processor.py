import os
import openai

class NLPProcessor:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        openai.api_key = self.api_key

    def generate_instructions(self, query, conversation_history=""):
        prompt = f"""
        You are an AI assistant specializing in data science and Python programming.
        Below is the conversation history between you and the user:

        {conversation_history}

        User: {query}

        Provide a detailed, step-by-step guide on how to accomplish the user's request using Python, pandas, and matplotlib. Include code snippets and explanations.
        """
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["User:", "DataWizzy:"]
        )
        return response.choices[0].text.strip()