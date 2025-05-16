import express from 'express';
import Post from '../controllers/post.js';

const postRouter = express.Router();
const post = new Post();

postRouter.get("/posts/", post.getPosts);
postRouter.post("/posts/", post.createPost);
postRouter.delete("/posts/", post.deletePost);

export default postRouter;