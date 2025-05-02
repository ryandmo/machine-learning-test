"""
### 3. AI Image Caption Generator
**Description**: Build a web app where users upload an image, and the app generates a descriptive caption using an AI model. The React frontend handles image uploads, and the Python backend processes the image with a vision-language AI API.

**Tech Stack**:
- **Frontend**: React (for image upload and caption display)
- **Backend**: Python with Flask or FastAPI
- **AI API**: **Hugging Face Inference API** (free tier, use a model like `Salesforce/blip-image-captioning-base` for image captioning).

**How It Works**:
- Create a React component with an image upload input and a button to generate a caption.
- Send the uploaded image (as a base64 string or file) to the Python backend via a POST request.
- Use the Hugging Face API to process the image and generate a caption.
- Return the caption to the React frontend and display it below the image.

**Learning Outcomes**:
- Handling file uploads in React.
- Processing binary data (images) in Python.
- Integrating vision-based AI APIs.
- Error handling for invalid inputs (e.g., non-image files).

**Extensions**:
- Add a gallery to show previously captioned images.
- Allow users to edit the generated caption and save it.
- Include a loading animation during API processing.
"""
import requests
from PIL import Image

from database_wrapper import DatabaseWrapper
from config import IMAGE_DIR, HUGGING_FACE_API
from config import logger


class ImageCaptionGenerator:
    """
    A class to generate captions for images using a pre-trained model from Hugging Face.

    Attributes:
        headers (dict): Contains the authorization header for API requests.
        model (str): The model identifier for the image captioning model.
        database (str): The name of the database to store results.
        database_wrapper (DatabaseWrapper): An instance of DatabaseWrapper for database operations.
    """

    def __init__(self):
        """
        Initializes the ImageCaptionGenerator with API headers, model name,
        database name, and a database wrapper instance.
        """
        self.headers = {
            "Authorization": f"Bearer {HUGGING_FACE_API['key']}"
        }
        self.model = "Salesforce/blip-image-captioning-base"
        self.database = "sentiment_analysis"
        self.database_wrapper = DatabaseWrapper()

    def save_the_input(self, input_file):
        """
        Saves the input image file to the specified directory.

        Args:
            input_file: The input file object containing the image data.

        Returns:
            str: The file path where the image is saved.
        """
        file_name = "{}{}".format(
            IMAGE_DIR,
            input_file.filename
        )
        with open(file_name, 'wb') as ip_sheet:
            ip_sheet.write(input_file.file.read())
        return file_name

    def generate_caption_for_image(self, input_file):
        """
        Generates a caption for the provided image file.

        Args:
            input_file: The input file object containing the image data.

        Returns:
            dict: The result containing the generated caption and associated metadata.
        """
        file_name = self.save_the_input(input_file)
        img_files = {
            'image': (
                file_name,
                Image.open(file_name).tobytes()
            )
        }
        result = requests.post(
            f"{HUGGING_FACE_API['api']}{self.model}",
            headers=self.headers,
            files=img_files
        ).json()
        result[0].update({"questions": input_file.filename})
        logger.info(self.database_wrapper.save_data(
            result[0],
            self.database
        ))
        return result[0]
