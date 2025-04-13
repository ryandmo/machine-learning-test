"""
Build a simple chatbot interface where users can type messages, and an AI model responds intelligently.
The frontend will be a clean React UI, and the backend will use Python to interact with a free AI API to generate responses.
"""
import json
import hashlib
import datetime

from huggingface_hub import InferenceClient

from database_wrapper import DatabaseWrapper
from config import HUGGING_FACE_API, PARTITION_NAME, logger

"""
This interface connects with hugging face API to get a intelligent response to the questions asked by the user.
Currently using a developer free tier hugging face account, for enterprise purposes buying a "Enterprise license" is recommended.
This library will be based on text generation model, 
"""

class ChatBot:
    def __init__(self):
        """
        Initializes an instance of the class and sets up the InferenceClient.

        This constructor method is called when a new instance of the class is created.
        It initializes the InferenceClient with the specified provider, API key, and model
        from the HUGGING_FACE_API configuration.

        Attributes:
            client (InferenceClient): An instance of the InferenceClient used for making API calls.
        """
        self.client = InferenceClient(
            provider=HUGGING_FACE_API["provider"],  # The provider for the inference API.
            api_key=HUGGING_FACE_API["api_key"],  # The API key for authenticating requests.
            model=HUGGING_FACE_API["model"]  # The model to be used for inference.
        )
        self.database = "chatbot"
        self.database_wrapper = DatabaseWrapper() # creating a database operation handler.

    def respond_to_question(self, questions: list):
        """
        Responds to a list of questions by sending them to a chat completion API.

        Args:
            questions (list): A list of questions to be sent to the API.

        Returns:
            list: A list of responses, where each response corresponds to a question.
        """
        messages = []  # Initialize a list to hold the formatted messages for the API request.
        output = []  # Initialize a list to hold the final output responses.

        # Format each question into the required message structure.
        for question in questions:
            messages.append(
                {
                    "role": "user",  # The role of the message sender.
                    "content": question,  # The content of the question.
                }
            )

        # Use the max allowed token size, i.e. max_tokens = 1024 for free API.
        # In case a higher number of response tokens are expected, consider using a paid version.
        # completion = self.client.chat_completion(messages)
        #
        # # Process the choices returned by the API.
        # for choice in completion.choices:
        #     # Uncomment the following lines if you need to access finish_reason or seed.
        #     # finish_reason = choice.finish_reason
        #     # seed = choice.seed
        #
        #     # Split the content of the response message for purpose of displaying in pure markdown format.
        #     # More infor on markdown format can be found at:
        #     # https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax
        #     answers = choice.message.content.split("\n")
        #
        #     # Append the answers to the output list, replacing empty strings with '<br />' for HTML formatting purposes.
        #     output.append([i if i != '' else '<br />' for i in answers])

        # Also dump in file for verification
        output = json.load(open("response.txt"))
        # with open("response.txt") as chat:
        #     chat.write(json.dumps(output))
        logger.info((self.save_chat_history(questions, output)))
        return output  # Return the list of responses

    def save_chat_history(self, questions, responses, partition = None):
        is_modified = True
        # Create database if not already created for packages
        try:
            self.database_wrapper.database_create(self.database)
            is_modified = False
        except Exception as ex:
            print("Database already exists")
        print(questions)
        questions["responses"] = responses
        questions = self.add_id_and_creation_data_for_db_record(questions, is_modified, partition)
        return self.database_wrapper.document_upsert(
            self.database,
            [questions]
        )

    def add_id_and_creation_data_for_db_record(self, data, is_modified = False, partition = None):
        if not partition:
            partition = PARTITION_NAME
        if not is_modified:
            data["creation_date"] = str(datetime.datetime.utcnow())
        data["modification_date"] = str(datetime.datetime.utcnow())
        id_text = hashlib.md5(json.dumps(data["questions"]).encode()).hexdigest()
        data["_id"] = f"{partition}:{id_text}"
        return data