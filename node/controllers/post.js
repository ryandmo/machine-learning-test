import CouchDB from '../helpers/couchbase.js';

export default class Post{
	constructor(){
		this.instance = new CouchDB("default");
		this.collectionName = "posts";
	}
	getPosts = async (req, res, next) => {
		const response = await this.instance.fetchData(
			this.collectionName,
			{}
		);
		res.status(response.status).json(response["data"]);
	};

	createPost = async (req, res, next) => {
		let data = [];
		data.push(req.body);
		const response = await this.instance.saveData(
			this.collectionName,
			data,
			"title"
		);
		res.status(response.status).json(response);
	};

	deletePost = async (req, res, next) => {
		const info = req.body;
		if(!info.hasOwnProperty("post_id") || !info.hasOwnProperty("post_revision")){
			throw new Error("Post cannot be deleted as post_id and/or post_revision info are missing.");
		}
		const response = await this.instance.deleteDocument(
			"posts",
			info["post_id"],
			info["post_revision"]
		);
		res.status(response.status).json(response);
	};
}