import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from utils.chatbot import ChatBot
from utils.sentiment import SentimentAnalyzer

from config import ip_address, DEFAULT_UI_PORT, DEFAULT_SERVER_PORT

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

@app.get("/generate-sentiment-chart/")
async def generate_sentiment_chart_data(request: Request):
    sentiments = SentimentAnalyzer()
    return sentiments.get_sentiment_chart_data()
