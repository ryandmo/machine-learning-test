import dotenv from 'dotenv';
import fs from 'fs';

import AIModelInterface from '../helpers/AIModelInterface.js';

dotenv.config();

export default class ImageCaptionGenerator extends AIModelInterface{
	constructor(){
		super();
		this.task = 'text-classification';
		this.model = process.env.IMAGE_CAPTION_AI_MODEL;
		this.collectionName = "image_caption_generator";
	}

	saveInput = async (imageObj) => {
		fs.writeFile(process.env.IMAGE_LOCATION, imageData, (err) => {
	        if (err) {
	            console.error('Error saving image:', err);
	        } else {
	            console.log('Image saved successfully!');
	        }
	    });
	    return `${process.env.IMAGE_LOCATION}/${imageObj.name}`;
	}

	generateCaptionForImage = async (req, res, next) => {
		if (!req.files || Object.keys(req.files).length === 0) {
			return res.status(400).send('No files were uploaded.');
		}
	    const imageLocation = this.saveInput(req.files.image);
		const imageCaptionObj = await this.getInstance();
		// get the image and save to server side file system. Should be later migrated to some CDN or storage server.
		
		// check if data exists in DB, if not make call to AI
		const response = await imageCaptionObj(req.files.image);
		this.couch.saveData(
			this.collectionName,
			{
				"questions": data.questions[0],
				"sentiment": response[0]
			},
			"questions"
		);
		res.status(response.status).json({"message": "Dummy"});
	}
}