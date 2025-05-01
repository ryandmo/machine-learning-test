"""
Build a simple chatbot interface where users can type messages, and an AI model responds intelligently.
The frontend will be a clean React UI, and the backend will use Python to interact with a free AI API to generate responses.
"""

import markdown
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
        # login(token=HUGGING_FACE_API["api_key"])
        # A Decently intelligent model, with rational thinking, however it requires a strong GPU to run locally.
        # If anyone has powerful GPU available they can use this model.
        # For getting a glace at the responses of this model checkout the functioning by switching to remote module.
        # self.chatbot = pipeline(model="deepseek-ai/DeepSeek-R1")
        # using a low level chat model with intelligence comparison to a girls brain, for testing purpose
        self.chatbot = pipeline(model="distilgpt2")
        self.database = "chatbot"
        self.database_wrapper = DatabaseWrapper() # creating a database operation handler.

    def respond_to_question(self, questions: []):
        result = self.chatbot(questions["questions"][0])
        result[0].update({"questions": questions["questions"][0]})
        logger.info(self.save_chat_history(result[0]))
        return [result[0]["generated_text"].replace('\n', '<br /> ')]

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

    def save_chat_history(self, data, partition = None):
        logger.debug("In save_chat_history")
        is_modified = True
        # Create database if not already created for packages
        try:
            self.database_wrapper.database_create(self.database)
            is_modified = False
        except Exception as ex:
            logger.info("Database already exists")

        return self.database_wrapper.document_upsert(
            self.database,
            self.database_wrapper.add_id_and_creation_data_for_db_record(
                data,
                is_modified,
                partition
            )
        )
