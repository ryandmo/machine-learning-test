import express from 'express';
import Sentiment from '../controllers/sentiment.js';

const sentimentRouter = express.Router();
const sentiment = new Sentiment();

sentimentRouter.post("/sentiment-analysis/", sentiment.analyseSentiment);
sentimentRouter.get("/fetch-sentiment-history/", sentiment.fetchHistory);

export default sentimentRouter;