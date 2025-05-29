import express from 'express';
import dotenv from 'dotenv';
import morgan from 'morgan';
import bodyParser from "body-parser";
import postRouter from './routes/posts.js';
import chatbotRouter from './routes/chatbot.js';
import sentimentRouter from './routes/sentiment.js';
import imageCaptionGeneratorRouter from './routes/ImageCaptionGenerator.js';
import fileUpload from 'express-fileupload';

const app = express();

dotenv.config();

app.use(morgan("dev"));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));
app.use(fileUpload());

app.use(postRouter);
app.use(chatbotRouter);
app.use(sentimentRouter);
app.use(imageCaptionGeneratorRouter);

app.listen(process.env.PORT, () => {
	console.log(`Server started on HOST: ${process.env.HOST}:${process.env.PORT}`)
});