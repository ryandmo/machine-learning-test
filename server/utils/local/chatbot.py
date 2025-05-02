"""
Build a simple chatbot interface where users can type messages, and an AI model responds intelligently.
The frontend will be a clean React UI, and the backend will use Python to interact with a free AI API to generate responses.
"""

from huggingface_hub import login
from transformers import pipeline

from database_wrapper import DatabaseWrapper
from config import HUGGING_FACE_API, logger

"""
This interface connects with hugging face API to get a intelligent response to the questions asked by the user.
Currently using a developer free tier hugging face account, for enterprise purposes buying a "Enterprise license" is recommended.
This library will be based on text generation model, 
"""

class ChatBot:
    def __init__(self):
        """
        Initializes the ChatBot instance.

        Sets up the chatbot model and database wrapper.
        The model used is a lightweight version (distilgpt2) for testing purposes.
        A more advanced model can be used if a powerful GPU is available.
        """
        # login(token=HUGGING_FACE_API["api_key"])
        # A Decently intelligent model, with rational thinking, however it requires a strong GPU to run locally.
        # If anyone has powerful GPU available they can use this model.
        # For getting a glance at the responses of this model checkout the functioning by switching to remote module.
        # self.chatbot = pipeline(model="deepseek-ai/DeepSeek-R1")
        # using a low level chat model with intelligence comparison to a girls brain, for testing purpose
        self.chatbot = pipeline(model="distilgpt2")
        self.database = "chatbot"
        self.database_wrapper = DatabaseWrapper()  # Creating a database operation handler.

    def respond_to_question(self, questions: []):
        """
        Generates a response to the provided question.

        Args:
            questions (list): A list containing a dictionary with a key "questions"
                              that holds the question string.

        Returns:
            list: A list containing the generated response text with line breaks replaced by HTML <br /> tags.
        """
        result = self.chatbot(questions["questions"][0])
        result[0].update({"questions": questions["questions"][0]})
        logger.info(self.database_wrapper.save_data(result[0], self.database))
        return [result[0]["generated_text"].replace('\n', '<br /> ')]
