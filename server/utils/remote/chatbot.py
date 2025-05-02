"""
Build a simple chatbot interface where users can type messages, and an AI model responds intelligently.
The frontend will be a clean React UI, and the backend will use Python to interact with a free AI API to generate responses.
"""

import markdown

from huggingface_hub import InferenceClient
from enum import Enum
from typing import Tuple, Optional, Dict

from database_wrapper import DatabaseWrapper
from config import HUGGING_FACE_API, logger

"""
This interface connects with hugging face API to get a intelligent response to the questions asked by the user.
Currently using a developer free tier hugging face account, for enterprise purposes buying a "Enterprise license" is recommended.
This library will be based on text generation model, 
"""

class ListType(Enum):
    """Enum to represent list types."""
    ORDERED = "ol"
    UNORDERED = "ul"
    NONE = None

# Constants for Markdown patterns
UNORDERED_LIST_MARKERS = {"- ", "+ ", "* "}
ORDERED_LIST_MARKER = ". "
HEADER_MARKERS = {
    "# ": {"start": '<Header size="6xl"><b>', "end": "</b></Header>"},
    "## ": {"start": '<Header size="5xl"><b>', "end": "</b></Header>"},
    "### ": {"start": '<Header size="4xl"><b>', "end": "</b></Header>"},
}
HORIZONTAL_RULE_MARKERS = {"___": "<hr />", "---": "<hr />", "***": "<hr />"}
LINE_BREAK = " <br /> "

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
                self.format_markdown_to_html(choice.message.content)
            )

        logger.debug(output)
        questions["responses"] = output
        logger.info(self.database_wrapper.save_data([questions], self.database))
        return output  # Return the list of responses


    def open_list_item(self,
        line: str, is_first: Optional[bool], list_type: ListType
    ) -> Tuple[Optional[bool], str]:
        """
        Convert a Markdown list item to HTML and open the list if it's the first item.

        Args:
            line: The input Markdown line.
            is_first: Whether this is the first list item.
            list_type: The type of list (ordered or unordered).

        Returns:
            A tuple of (is_first flag, formatted HTML line).
        """
        if list_type == ListType.NONE:
            return is_first, line

        # Determine the marker length based on list type
        marker_length = 3 if list_type == ListType.ORDERED else 2
        formatted_line = f"<li>{line[marker_length:]}</li>"

        # Add opening tag for the first list item
        if is_first is None:
            formatted_line = f"<{list_type.value}>{formatted_line}"
            is_first = True

        return is_first, formatted_line

    def close_list(self,
        is_first: Optional[bool], list_type: ListType
    ) -> Tuple[None, str]:
        """
        Close an HTML list if it was opened.

        Args:
            is_first: Whether a list is currently open.
            list_type: The type of list (ordered or unordered).

        Returns:
            A tuple of (None, closing tag or empty string).
        """
        if is_first and list_type != ListType.NONE:
            return None, f"</{list_type.value}>"
        return None, ""

    def format_markdown_to_html(self, data: str) -> str:
        """
        Convert Markdown text to HTML with specific formatting rules.

        Args:
            data: The input Markdown text.

        Returns:
            The formatted HTML string with lines joined by <br /> tags.

        Examples:
            >>> format_markdown_to_html("# Header\\n- Item")
            '<Header size="6xl"><b>Header</b></Header> <br /> <ul><li>Item</li>'
        """
        final_content = []
        lines = data.split("\\n")
        is_list_open = None
        current_list_type = ListType.NONE

        for line in lines:
            if not line.strip():
                # Close any open list for empty lines
                is_list_open, closing_tag = self.close_list(is_list_open, current_list_type)
                final_content.append(closing_tag)
                current_list_type = ListType.NONE
                continue

            # Check for unordered list
            if any(line.startswith(marker) for marker in UNORDERED_LIST_MARKERS):
                if current_list_type != ListType.UNORDERED:
                    is_list_open, closing_tag = self.close_list(is_list_open, current_list_type)
                    final_content.append(closing_tag)
                    current_list_type = ListType.UNORDERED
                is_list_open, formatted_line = self.open_list_item(line, is_list_open, ListType.UNORDERED)
                final_content.append(formatted_line)
                continue

            # Check for ordered list
            if line and line[0].isdigit() and line[1:3] == ORDERED_LIST_MARKER:
                if current_list_type != ListType.ORDERED:
                    is_list_open, closing_tag = self.close_list(is_list_open, current_list_type)
                    final_content.append(closing_tag)
                    current_list_type = ListType.ORDERED
                is_list_open, formatted_line = self.open_list_item(line, is_list_open, ListType.ORDERED)
                final_content.append(formatted_line)
                continue

            # Close any open list before processing other markup
            is_list_open, closing_tag = self.close_list(is_list_open, current_list_type)
            final_content.append(closing_tag)
            current_list_type = ListType.NONE

            # Process headers
            for marker, tags in HEADER_MARKERS.items():
                if line.startswith(marker):
                    final_content.append(f"{tags['start']}{line[len(marker):]}{tags['end']}")
                    break
            else:
                # Process horizontal rules
                if line in HORIZONTAL_RULE_MARKERS:
                    final_content.append(HORIZONTAL_RULE_MARKERS[line])
                else:
                    final_content.append(line)

        # Close any remaining open list
        if is_list_open:
            _, closing_tag = self.close_list(is_list_open, current_list_type)
            final_content.append(closing_tag)

        return LINE_BREAK.join(final_content)
