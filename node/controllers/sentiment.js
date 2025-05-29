import dotenv from 'dotenv';

import AIModelInterface from '../helpers/AIModelInterface.js';

dotenv.config();

export default class Sentiment extends AIModelInterface{
	constructor(){
		super();
		this.task = 'text-classification';
		this.model = process.env.SENTIMENT_AI_MODEL;
		this.collectionName = "sentiment_analysis";
	}

	analyseSentiment = async (req, res, next) => {
		const data = req.body;
		const sentimentObj = await this.getInstance();
		// check if data exists in DB, if not make call to AI
		const response = await sentimentObj(data.questions[0]);
		this.couch.saveData(
			this.collectionName,
			{
				"questions": data.questions[0],
				"sentiment": response[0]
			},
			"questions"
		);
		res.status(response.status).json(response[0]);
	}
}