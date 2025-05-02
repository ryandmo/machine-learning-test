"""
Build a simple chatbot interface where users can type messages, and an AI model responds intelligently.
The frontend will be a clean React UI, and the backend will use Python to interact with a free AI API to generate responses.
"""

import requests

from database_wrapper import DatabaseWrapper
from config import HUGGING_FACE_API, logger


"""
This interface connects with hugging face API to get a intelligent response to the questions asked by the user.
Currently using a developer free tier hugging face account, for enterprise purposes buying a "Enterprise license" is recommended.
This library will be based on text generation model, 
"""

class ChatBot:
    """
    A class to represent a chatbot that interacts with a language model
    and manages conversation data.

    Attributes:
        headers (dict): A dictionary containing the authorization header for API requests.
        model (str): The model name used for generating responses.
        database (str): The name of the database where conversation data is stored.
        database_wrapper (DatabaseWrapper): An instance of DatabaseWrapper for handling database operations.
    """

    def __init__(self):
        """
        Initializes the ChatBot with necessary headers, model name,
        database name, and a database operation handler.
        """
        self.headers = {
            "Authorization": f"Bearer {HUGGING_FACE_API['key']}"
        }
        self.model = "distilgpt2"
        self.database = "chatbot"
        self.database_wrapper = DatabaseWrapper()  # creating a database operation handler.

    def respond_to_question(self, questions: list):
        """
        Sends a list of questions to the language model and retrieves the generated response.

        Args:
            questions (list): A list containing the questions to be sent to the model.

        Returns:
            list: A list containing the generated response text with newline characters replaced by HTML line breaks.
        """
        messages = requests.post(
            f"{HUGGING_FACE_API['api']}{self.model}",
            headers=self.headers,
            json=questions['questions']
        ).json()

        messages[0].update({"questions": questions["questions"][0]})
        logger.info(self.database_wrapper.save_data(messages[0], self.database))
        return [messages[0]["generated_text"].replace('\n', '<br /> ')]
