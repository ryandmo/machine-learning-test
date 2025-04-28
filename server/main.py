import os
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import File, UploadFile
from fastapi.responses import FileResponse

from utils.chatbot import ChatBot
from utils.sentiment import SentimentAnalyzer
from utils.image_caption_generator import ImageCaptionGenerator

from config import ip_address, DEFAULT_UI_PORT, DEFAULT_SERVER_PORT
from config import IMAGE_DIR

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
    chatbot = ChatBot()
    data = await request.form()
    return chatbot.respond_to_question(
        json.loads(data["json"])
    )

@app.post("/sentiment-analysis/")
async def sentiment_analysis(request: Request):
    sentiments = SentimentAnalyzer()
    data = await request.form()
    return sentiments.analyse_sentiment_of_message(
        json.loads(data["json"])
    )

@app.get("/fetch-sentiment-history/")
async def fetch_sentiment_history(request: Request):
    sentiments = SentimentAnalyzer()
    return sentiments.fetch_sentiment_history()

@app.post("/generate-caption-for-image/")
def generate_caption_for_image(input_file: UploadFile = File(...)):
    image_caption_gen = ImageCaptionGenerator()
    return image_caption_gen.generate_caption_for_image(input_file)

@app.get("/get-image/")
def get_image(filename: str):
    filepath = "{}{}".format(IMAGE_DIR, filename)
    if os.path.isfile(filepath):
        return FileResponse(filepath, media_type="image/jpeg")
    else:
        return FileResponse("{}{}".format(IMAGE_DIR, "default.jpg"), media_type="image/jpeg")