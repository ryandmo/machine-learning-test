import http from 'http';
import querystring from 'querystring';
import url from 'url';
import dotenv from 'dotenv';

import { pipeline, env } from '@huggingface/transformers';
import CouchDB from './couchbase.js';

dotenv.config();

export default class AIModelInterface{
	constructor(){
		this.task = undefined;
		this.couch = new CouchDB();
		this.model = undefined;
		this.instance = undefined;
		this.collectionName = undefined;
	}

	getInstance = async (progress_callback = undefined) => {
		if (this.instance === undefined) {
			this.instance = await pipeline(
				this.task, 
				this.model, 
				{ progress_callback }
			);
	    }
	    return this.instance;
	}

	fetchHistory = async (req, res, next) => {
		console.log("In fetch history.");
		const response = await this.couch.fetchData(
			this.collectionName,
			{}
		);
		res.status(response.status).json(response.data.docs);
	}
}