import dotenv from 'dotenv';

import AIModelInterface from '../helpers/AIModelInterface.js';

dotenv.config();

export default class Chatbot extends AIModelInterface{
	constructor(){
		super();
		this.task = 'text-generation';
		this.model = process.env.CHAT_AI_MODEL;
		this.collectionName = "chatbot";
	}

	getAssistance = async (req, res, next) => {
		const data = req.body;
		const chatbot = await this.getInstance();
		const response = await chatbot(data.questions[0]);
		this.couch.saveData(
			this.collectionName,
			{
				"questions": data.questions[0],
				"responses": response[0]
			},
			"questions"
		);
		res.status(200).json(response[0].replaceAll('\n', '<br /> '));
	}
}
