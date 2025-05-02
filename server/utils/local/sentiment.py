"""
### 2. Sentiment Analysis Dashboard
**Description**: Create a web app where users can input text (e.g., a tweet or review), and the app displays whether the sentiment is positive, negative, or neutral. The React frontend handles user input, and the Python backend uses an AI API to analyze sentiment.

**Tech Stack**:
- **Frontend**: React (for input form and result display)
- **Backend**: Python with Flask or FastAPI
- **AI API**: **Hugging Face Inference API** (free tier, use a sentiment analysis model like `distilbert-base-uncased-finetuned-sst-2-english`).

**How It Works**:
- Build a React form with a textarea for user input and a button to submit.
- Set up a Python backend to receive the text via a POST request.
- Use the Hugging Face API to analyze the text’s sentiment and return the result (e.g., “Positive” with a confidence score).
- Display the sentiment result and confidence score in the React UI with a visual indicator (e.g., green for positive, red for negative).

**Learning Outcomes**:
- Handling form submissions in React.
- Creating RESTful APIs in Python.
- Parsing and displaying JSON responses from an AI API.
- Basic UI design with conditional rendering.

**Extensions**:
- Add a history section to show previous analyses.
- Include a bar chart (using a library like Chart.js) to visualize sentiment scores.
- Allow users to analyze multiple texts at once.

---
"""

# need to learn Model training using AutoNLP and fine tuned approach, check if its universal or huggingface specific.

# import tweepy
import time
from transformers import pipeline
from database_wrapper import DatabaseWrapper

from config import twitter
from config import HUGGING_FACE_API, logger

class SentimentAnalyzer:
    def __init__(self):
        self.sentiment_analysis = pipeline(model = "distilbert-base-uncased-finetuned-sst-2-english")
        self.database = "sentiment_analysis"
        self.database_wrapper = DatabaseWrapper()  # creating a database operation handler.

    def analyse_sentiment_of_message(self, content):
        if len(content['questions']):
            # Fetch data from DB if available else hit sentiment analyzer
            sentiment = self.database_wrapper.document_read(
                database = self.database,
                document = self.database_wrapper.get_id(content['questions'][0]),
                partition = "default"
            )
            if sentiment["status_code"] <= 400:
                logger.info("Found in DB")
                tweet = {
                    'questions': sentiment['content']['questions'],
                    'sentiment': sentiment['content']['sentiment']
                }
            else:
                sentiment = self.sentiment_analysis(content['questions'][0])
                logger.info("From transformer API")
                tweet = {
                    'questions': content['questions'][0],
                    'sentiment': sentiment[0]['label']
                }
                # Save all sentiments into Database
                logger.info(self.database_wrapper.save_data(tweet, self.database))
            return tweet
        return []
