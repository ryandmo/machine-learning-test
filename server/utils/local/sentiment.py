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
        # self.auth = tweepy.AppAuthHandler(
        #     twitter['API_KEY'],
        #     twitter['API_KEY_SECRET']
        # )
        # self.api = tweepy.API(
        #     self.auth,
        #     wait_on_rate_limit=True
        # )
        self.sentiment_analysis = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")
        # self.tweets = []
        # self.tweet_count = 1000
        self.database = "sentiment_analysis"
        self.database_wrapper = DatabaseWrapper()  # creating a database operation handler.

    # Helper function for handling pagination in our search and handle rate limits
    # def limit_handled(self, cursor):
    #     while True:
    #         try:
    #             yield cursor.next()
    #         except tweepy.errors.TooManyRequests:
    #             print('Reached rate limit. Sleeping for >15 minutes')
    #             time.sleep(15 * 61)
    #         except StopIteration:
    #             break
    #
    # def get_tweets(self):
    #     # Define the term you will be using for searching tweets
    #     query = '#NFTs'
    #     query = query + ' -filter:retweets'
    #
    #     # Let's search for tweets using Tweepy
    #     return self.limit_handled(tweepy.Cursor(self.api.search,
    #          q = query,
    #          tweet_mode = 'extended',
    #          lang = 'en',
    #          count = self.tweet_count,
    #          result_type = "recent").items(self.tweet_count))
    #
    # def sentiment_analysis_of_feed_tweets(self):
    #     search = self.get_tweets()
    #     for tweet in search:
    #         try:
    #             content = tweet.full_text
    #             sentiment = self.sentiment_analysis(content)
    #             self.tweets.append({'tweet': content, 'sentiment': sentiment[0]['label']})
    #
    #         except Exception as ex:
    #             print(ex)
    #     return self.tweets

    def analyse_sentiment_of_message(self, content):
        if len(content['questions']):
            # Fetch data from DB if available else hit sentiment analyzer
            sentiment = self.database_wrapper.document_read(
                database = self.database,
                document = self.database_wrapper.get_id(content['questions'][0]),
                partition=""
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
                logger.info(self.save_sentiment_analysis([tweet]))
            return tweet
        return []

    def fetch_sentiment_history(self):
        # get all records from DB and send the list across
        docs = self.database_wrapper.database_find(
            database=self.database,
            query = {
                'selector': {}
            }
        )
        if docs["status_code"] < 400:
            return docs["content"]["docs"]
        else:
            # In case collection is not created yet
            return []

    def save_sentiment_analysis(self, data, partition = "default"):
        logger.debug("In save_sentiment_analysis")
        is_modified = True
        # Create database if not already created for packages
        try:
            self.database_wrapper.database_create(self.database)
            is_modified = False
        except Exception as ex:
            logger.info("Database already exists")
        final_data = [self.database_wrapper.add_id_and_creation_data_for_db_record(
            i,
            is_modified,
            partition
        ) for i in data]
        return self.database_wrapper.document_upsert(
            self.database,
            final_data
        )
