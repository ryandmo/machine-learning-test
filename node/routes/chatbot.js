import express from 'express';
import Chatbot from '../controllers/chatbot.js';

const chatbotRouter = express.Router();
const chatbot = new Chatbot();

chatbotRouter.post("/get_assistance/", chatbot.getAssistance);

export default chatbotRouter;