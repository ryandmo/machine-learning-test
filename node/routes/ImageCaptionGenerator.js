import express from 'express';
import ImageCaptionGenerator from '../controllers/ImageCaptionGenerator.js';

const imageCaptionGeneratorRouter = express.Router();
const imageCaptionGenerator = new ImageCaptionGenerator();

imageCaptionGeneratorRouter.post("/generate-caption-for-image/", imageCaptionGenerator.generateCaptionForImage);

export default imageCaptionGeneratorRouter;