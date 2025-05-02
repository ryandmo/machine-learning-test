import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

from config import ip_address, DEFAULT_UI_PORT, DEFAULT_SERVER_PORT
from config import IMAGE_DIR, AI_API_REMOTE


if not AI_API_REMOTE:
    # Import the local AI Models
    from utils.local.chatbot import ChatBot
    from utils.local.sentiment import SentimentAnalyzer
    from utils.local.image_caption_generator import ImageCaptionGenerator
else:
    # Import the remote AI Models
    from utils.remote.chatbot import ChatBot
    from utils.remote.sentiment import SentimentAnalyzer
    from utils.remote.image_caption_generator import ImageCaptionGenerator


CORS_ORIGINS = [
    "http://localhost:{}".format(DEFAULT_UI_PORT),
    "https://localhost:{}".format(DEFAULT_UI_PORT),
    "https://{}:{}".format(ip_address, DEFAULT_UI_PORT),
    "http://{}:{}".format(ip_address, DEFAULT_UI_PORT),
    "http://{}:{}".format(ip_address, DEFAULT_SERVER_PORT),
    "https://{}:{}".format(ip_address, DEFAULT_SERVER_PORT)
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, compresslevel=1)

@app.post("/get_assistance/")
async def get_assistance(request: Request):
    """
    Handles POST requests to the /get_assistance/ endpoint.

    This function processes the incoming request to retrieve assistance from the chatbot.
    It extracts the form data from the request, specifically looking for a JSON string,
    and then passes it to the chatbot for a response.

    Args:
        request (Request): The incoming HTTP request containing form data.

    Returns:
        Response: The response from the chatbot based on the provided question.
    """
    chatbot = ChatBot()
    data = await request.form()
    return chatbot.respond_to_question(
        json.loads(data["json"])
    )


@app.post("/sentiment-analysis/")
async def sentiment_analysis(request: Request):
    """
    Handles POST requests to the /sentiment-analysis/ endpoint.

    This function processes the incoming request to perform sentiment analysis on a message.
    It extracts the form data from the request, specifically looking for a JSON string,
    and then passes it to the SentimentAnalyzer for analysis.

    Args:
        request (Request): The incoming HTTP request containing form data.

    Returns:
        Response: The result of the sentiment analysis based on the provided message.
    """
    sentiments = SentimentAnalyzer()
    data = await request.form()
    return sentiments.analyse_sentiment_of_message(
        json.loads(data["json"])
    )


@app.get("/fetch-sentiment-history/")
async def fetch_sentiment_history(request: Request):
    """
    Handles GET requests to the /fetch-sentiment-history/ endpoint.

    This function retrieves the sentiment history from the database using the SentimentAnalyzer.
    It initializes the SentimentAnalyzer and calls its database wrapper to fetch the history
    without any specific selector criteria.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        Response: The sentiment history retrieved from the database.
    """
    sentiments = SentimentAnalyzer()
    return sentiments.database_wrapper.fetch_history(
        sentiments.database,
        {'selector': {}}
    )

@app.post("/generate-caption-for-image/")
def generate_caption_for_image(input_file: UploadFile = File(...)):
    """
    Handles POST requests to the /generate-caption-for-image/ endpoint.

    This function processes the incoming image file and generates a caption for it
    using the ImageCaptionGenerator. The input file is expected to be an image that
    the generator can analyze to produce a descriptive caption.

    Args:
        input_file (UploadFile): The uploaded image file for which the caption is to be generated.

    Returns:
        str: The generated caption for the provided image.
    """
    image_caption_gen = ImageCaptionGenerator()
    return image_caption_gen.generate_caption_for_image(input_file)


@app.get("/get-image/")
def get_image(filename: str):
    """
    Handles GET requests to the /get-image/ endpoint.

    This function retrieves an image file based on the provided filename. It checks if the
    specified image file exists in the IMAGE_DIR directory. If the file exists, it returns
    the file as a response with the media type set to 'image/jpeg'. If the file does not
    exist, it returns a default image instead.

    Args:
        filename (str): The name of the image file to retrieve.

    Returns:
        FileResponse: The image file if it exists, or a default image if it does not.
    """
    filepath = "{}{}".format(IMAGE_DIR, filename)
    if os.path.isfile(filepath):
        return FileResponse(filepath, media_type="image/jpeg")
    else:
        return FileResponse("{}{}".format(
            IMAGE_DIR,
            "default.jpg"),
            media_type="image/jpeg"
        )


@app.get("/fetch-image-caption-history/")
def fetch_image_caption_history():
    """
    Handles GET requests to the /fetch-image-caption-history/ endpoint.

    This function retrieves the history of image captions from the database using the
    ImageCaptionGenerator. It initializes the generator and calls its database wrapper
    to fetch the history, excluding entries where the question is "default.jpg".

    Returns:
        Response: The history of image captions retrieved from the database.
    """
    image_caption_gen = ImageCaptionGenerator()
    return image_caption_gen.database_wrapper.fetch_history(
        image_caption_gen.database,
        {
            'selector': {
                "questions": {
                    "$ne": "default.jpg"
                }
            }
        }
    )

@app.put("/update-caption-for-image/")
async def update_caption_for_image(request: Request):
    """
    Handles PUT requests to the /update-caption-for-image/ endpoint.

    This function processes the incoming request to update the caption for a specific image.
    It initializes the ImageCaptionGenerator, extracts the form data from the request,
    and saves the updated caption data to the database.

    Args:
        request (Request): The incoming HTTP request containing form data, including a JSON string
                           with the updated caption information.

    Returns:
        Response: The result of the save operation, which typically indicates success or failure.
    """
    image_caption_gen = ImageCaptionGenerator()
    data = await request.form()
    return image_caption_gen.database_wrapper.save_data(
        json.loads(data["json"]),
        image_caption_gen.database
    )
