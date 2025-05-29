import dotenv from 'dotenv';
import crypto from 'crypto';

dotenv.config();

export default class CouchDB{
	constructor(partition){
		this.setPartition(partition);
		this.status = undefined;
	}

	connect = async (uri, method, json, params) => {
		const token = Buffer.from(
			`${process.env.DB_USER}:${process.env.DB_PASSWORD}`
		).toString('base64');

		let fetchParams = {
		    mode: 'cors',
		    method: method,
		    headers: {
				"content-type": "application/json", 
				"accept": "application/json",
				'Authorization': `Basic ${token}`
			}
		};

		const connection_string = `http://${process.env.DB_HOST}:${process.env.DB_PORT}`;

		if (json !== undefined){
			fetchParams['body'] = JSON.stringify(json);
		}
		if (params !== undefined){
			params = '?' + Object.keys(params).map((key, index) => {
				return `${key}=${params[key]}`;
			}).join('&')
		}else{
			params = ''
		}
		this.status = undefined;
		return await fetch(
			`${connection_string}${uri}${params}`,
			fetchParams
		)
		.then(response => {
			this.status = response.status;
			return response.json();
		}).then(data => {
			return {
				"status": this.status,
				"data": data
			};
		})
		.catch(err => {
		    console.log(err);
		});
	}

	setPartition = (partition) => {
		this.partition = (partition === undefined || partition === '') ? process.env.DB_PARTITION : partition;
	}

	getAllCollections = () => {
		this.connect("/_all_dbs", 'GET');
	}

	queryCollection = (operation, collectionName, query, bulk) => {
		bulk = (bulk === undefined) ? false : bulk;
		let uri = undefined;
		let json = undefined;
		let method = undefined;
		let params = undefined;
		if (bulk){
			uri = `/${collectionName}/_bulk_docs`;
			json = {
				"docs": query
			}
			method = 'POST';
		}else{
			switch(operation){
				case 'create':
					uri = `/${collectionName}`;
					method = 'PUT';
					params = query;
					break;
				case 'read':
					uri = `/${collectionName}/_partition/${this.partition}`;
					method = 'GET';
					break;
				case 'find':
					uri = `/${collectionName}/_partition/${this.partition}/_find`;
					method = 'POST';
					json = query;
					break;
				case 'filter':
					uri = `/${collectionName}/_changes?filter=_selector&include_docs=true`;
					json = {
						"selector": query
					}
					method = 'POST';
					break;
				case 'delete':
					uri = `/${collectionName}`;
					method = 'DELETE';
					break;
				case 'default':
					throw `Invalid operation: ${operation}`;
			}
		}
		return this.connect(uri, method, json, params);
	}

	queryDocument = (operation, collectionName, document, rev, data) => {
		let uri = undefined;
		let json = undefined;
		let method = undefined;
		let params = undefined;

		switch(operation){
			case 'create':
				uri = `/${collectionName}`;
				const current_time = new Date().toISOString();
				data["creation_date"] = current_time;
				data["modification_date"] = current_time;
				json = data;
				method = 'POST';
				break;
			case 'read':
				document = (document === undefined) ? '_all_docs': document;
				uri = `/${collectionName}/_partition/${this.partition}/${document}`;
				method = 'GET';
				params = data;
				break;
			case 'update':
				data["modification_date"] = new Date().toISOString();
				uri = `/${collectionName}/_partition/${this.partition}/${document}`;
				method = 'PUT';
				json = data;
				break;
			case 'delete':
				uri = `/${collectionName}/${document}?rev=${rev}`;
				method = 'DELETE';
				break;
			case 'default':
				throw (`Invalid operation: ${operation}`);
		}
		return this.connect(uri, method, json, params);
	}

	createCollection = (collectionName) => {
		return this.queryCollection(
			'create',
			collectionName,
			{
				"partitioned": "true"
			}
		);
	}

	readCollection = (collectionName) => {
		return this.queryCollection(
			'read',
			collectionName
		);
	}

	deleteCollection = (collectionName) => {
		return this.queryCollection(
			'delete',
			collectionName
		);
	}

	findInCollection = (collectionName, query) => {
		return this.queryCollection(
			'find',
			collectionName,
			query
		);
	}

	filterCollection = (collectionName, query) => {
		return this.queryCollection(
			'filter',
			collectionName,
			query
		);
	}

	updateDocuments = (collectionName, data) => {
		return this.queryCollection(
			"",
			collectionName,
			data,
			true
		);
	}

	createDocument = (collectionName, data) => {
		return this.queryDocument(
			"create",
			collectionName,
			undefined,
			undefined,
			data
		);
	}

	readDocument = (collectionName, docId, data) => {
		return this.queryDocument(
			"read",
			collectionName,
			(docId === undefined) ? '_all_docs' : docId,
			data
		);
	}

	updateDocument = (collectionName, docId, data) => {
		return this.queryDocument(
			"update",
			collectionName,
			docId = (docId === undefined) ? '_all_docs' : docId,
			data
		);
	}

	deleteDocument = (collectionName, docId, rev) => {
		return this.queryDocument(
			"delete",
			collectionName,
			docId,
			rev
		);
	}

	getId = (key) => {
		const id_text = crypto.createHash('sha1').update(key).digest('hex');
		return `${this.partition}:${id_text}`;
	}

	saveData = async (collectionName, data, keyName) => {
		// Create database if does not exists
		const response = await this.createCollection(
			collectionName
		);
		return this.updateDocuments(
			collectionName,
			data.map(obj => {
				obj['_id'] = this.getId(obj[keyName]);
				const current_time = new Date().toISOString();
				if(obj["creation_date"] === undefined){
					obj["creation_date"] = current_time;
				}
				obj["modification_date"] = current_time;
				return obj;
			})
		)
	}

	fetchData = async (collectionName, query) => {
		// pass the selector query for filtering.
		// e.g. {"fname": "Ram"}, will returns documents with column fname set to value Ram.
		// e.g. {"age": {"$gt": 45}}, will return all docs with age column value above 45.
		// e.g {}, will return all the docs in the collection.
		return  this.findInCollection(
			collectionName,
			{
				"selector": query
			}
		);
	}
}
