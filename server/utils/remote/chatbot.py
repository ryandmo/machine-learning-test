"""
Build a simple chatbot interface where users can type messages, and an AI model responds intelligently.
The frontend will be a clean React UI, and the backend will use Python to interact with a free AI API to generate responses.
"""

import markdown

from huggingface_hub import InferenceClient

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
        messages.append(
            {
                "role": "user",  # The role of the message sender.
                "content": questions["questions"],  # The content of the question.
            }
        )

        # Use the max allowed token size, i.e. max_tokens = 1024 for free API.
        # In case a higher number of response tokens are expected, consider using a paid version.
        completion = self.client.chat_completion(messages)

        # Process the choices returned by the API.
        for choice in completion.choices:
            # Uncomment the following lines if you need to access finish_reason or seed.
            # finish_reason = choice.finish_reason
            # seed = choice.seed
            output.append(
                self.initial_markdown_formatting(choice.message.content)
            )

        logger.debug(output)
        logger.info((self.save_chat_history(questions, output)))
        return output  # Return the list of responses

    def open_order_unordered_list(self, line, list_first_occurence, ordered_list):
        if ordered_list:
            line = f"{line.replace(line[:3], '<li>')}</li>"
        else:
            line = f"{line.replace(line[:2], '<li>')}</li>"
        if list_first_occurence is None:
            list_first_occurence = True
            if ordered_list:
                line = f"<ol>{line}"
            else:
                line = f"<ul>{line}"
        return (list_first_occurence, line)

    def close_order_unordered_list(self, list_first_occurence, ordered_list):
        if list_first_occurence:
            if ordered_list:
                line = f"</ol>"
            else:
                line = f"</ul>"
        else:
            line = ''
        return (None, line)

    def initial_markdown_formatting(self, data):
        final_content = []
        #break into pieces for processing.
        # Currently handling only known scenarios encountered from AI responses
        # In case more scenarios are encountered they can be handled accordingly.
        data = data.split("\\n")
        list_first_occurence = None
        ordered_list = False
        markup_mapping = {
            '# ': {'start': '<Header size="6xl"><b>', 'end': '</b></Header>'},
            '## ': {'start': '<Header size="5xl"><b>', 'end': '</b></Header>'},
            '### ': {'start': '<Header size="4xl"><b>', 'end': '</b></Header>'},
            '___': {'start': '<hr />', 'end': ''},
            '---': {'start': '<hr />', 'end': ''},
            '***': {'start': '<hr />', 'end': ''}
        }
        for line in data:
            tag_opened = True
            # Handling only two levels of ordered/unordered list
            if len(line) and (line.startswith('- ') or line.startswith('+ ') or line.startswith('* ')):
                ordered_list = False
                list_first_occurence, line = self.open_order_unordered_list(line, list_first_occurence, ordered_list)
            elif len(line) and line[0].isnumeric() and line[1:3] == '. ':
                ordered_list = True
                list_first_occurence, line = self.open_order_unordered_list(line, list_first_occurence, ordered_list)
            else:
                for key in markup_mapping:
                    if line.startswith(key):
                        list_first_occurence, closing_tag = self.close_order_unordered_list(list_first_occurence, ordered_list)
                        line = f"{closing_tag}{line.replace(key, markup_mapping[key]['start'])}{markup_mapping[key]['end']}"
            final_content.append(line)

        return " <br /> ".join(final_content)

    def save_chat_history(self, questions, responses, partition = None):
        logger.debug("In save_chat_history")
        is_modified = True
        # Create database if not already created for packages
        try:
            self.database_wrapper.database_create(self.database)
            is_modified = False
        except Exception as ex:
            logger.info("Database already exists")
        questions["responses"] = responses
        questions = self.database_wrapper.add_id_and_creation_data_for_db_record(
            questions,
            is_modified,
            partition
        )
        return self.database_wrapper.document_upsert(
            self.database,
            [questions]
        )
