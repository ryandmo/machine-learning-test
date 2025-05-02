import requests
import datetime
import hashlib
import json

from config import COUCHDB_CONF, logger

class DatabaseWrapper:
    def __init__(self) -> None:
        """
        Initializes the DatabaseWrapper instance by creating a new session for requests.
        Sets up authentication and headers for CouchDB interactions.
        """
        self.session = requests.Session()

        self.session.auth = (
            COUCHDB_CONF["user"],
            COUCHDB_CONF["password"]
        )
        self.headers = {
            "Accept": "application/json",
            "Content-type": "application/json",
        }

    def get_all_databases(self):
        '''
        List all the databases in the CouchDB instance.
        Returns:
            list: A list of all database names.
        '''
        return self.database_read("_all_dbs", partition="")

    # Master Functions
    def query_database(self, operation, database, partition=None, bulk=False, query={}) -> tuple:
        """
        Performs various operations on a specified database.

        Args:
            operation (str): The operation to perform (create, read, find, filter, delete).
            database (str): The name of the database to operate on.
            partition (str, optional): The partition to operate on. Defaults to None.
            bulk (bool, optional): Indicates if the operation is a bulk operation. Defaults to False.
            query (dict, optional): The query parameters for the operation. Defaults to an empty dict.

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        path = database + (f"/_partition/{partition}" if partition else "")
        try:
            if bulk:
                response = self.session.post(f"{COUCHDB_CONF['connection_string']}/{database}/_bulk_docs", headers=self.headers,
                                             json={"docs": query})
            else:
                if operation == "create":
                    response = self.session.put(f"{COUCHDB_CONF['connection_string']}/{database}", headers=self.headers,
                                                params=query)
                if operation == "read":
                    response = self.session.get(f"{COUCHDB_CONF['connection_string']}/{path}", headers=self.headers)
                if operation == "find":
                    response = self.session.post(f"{COUCHDB_CONF['connection_string']}/{path}/_find", headers=self.headers,
                                                 json=query)
                if operation == "filter":
                    response = self.session.post(
                        f"{COUCHDB_CONF['connection_string']}/{database}/_changes?filter=_selector&include_docs=true",
                        headers=self.headers, json={"selector": query})
                if operation == "delete":
                    response = self.session.delete(f"{COUCHDB_CONF['connection_string']}/{database}", headers=self.headers)
            response.raise_for_status()
            return {"status_code": response.status_code, "content": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status_code": e.response.status_code, "content": e.response.json()}

    def query_document(self, operation, database, partition=None, document=None, rev=None, data=None) -> tuple:
        """
        Performs various operations on a specified document within a database.

        Args:
            operation (str): The operation to perform (create, read, update, delete).
            database (str): The name of the database to operate on.
            partition (str, optional): The partition to operate on. Defaults to None.
            document (str, optional): The ID of the document to operate on. Defaults to None.
            rev (str, optional): The revision ID of the document for delete operations. Defaults to None.
            data (dict, optional): The data to be used for create or update operations. Defaults to None.

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        path = database + (f"/_partition/{partition}" if partition else "")
        try:
            if operation == "create":
                # Need a creation_date and modification_date for record
                data["creation_date"] = str(datetime.datetime.utcnow())
                data["modification_date"] = str(datetime.datetime.utcnow())
                response = self.session.post(f"{COUCHDB_CONF['connection_string']}/{database}", headers=self.headers, json=data)
            if operation == "read":
                logger.debug(f"{COUCHDB_CONF['connection_string']}/{path}/{document}")
                response = self.session.get(f"{COUCHDB_CONF['connection_string']}/{path}/{document}", headers=self.headers,
                                            params=data)
            if operation == "update":
                data["modification_date"] = str(datetime.datetime.utcnow())
                response = self.session.put(f"{COUCHDB_CONF['connection_string']}/{path}/{document}", headers=self.headers,
                                            json=data)
            if operation == "delete":
                response = self.session.delete(f"{COUCHDB_CONF['connection_string']}/{path}/{document}?rev={rev}",
                                               headers=self.headers)
            response.raise_for_status()
            return {"status_code": response.status_code, "content": response.json()}
        except requests.exceptions.RequestException as e:
            return {"status_code": e.response.status_code, "content": e.response.json()}

    # Convenience Functions
    def database_create(self, database, partition="default") -> tuple:
        """
        Creates a new database in CouchDB.

        Args:
            database (str): The name of the database to be created.
            partition (str, optional): The partition to create the database in. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_database(operation="create", database=database, query={"partitioned": "true"})

    def database_read(self, database, partition="default") -> tuple:
        """
        Reads information about a specified database.

        Args:
            database (str): The name of the database to read information from.
            partition (str, optional): The partition to read from. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_database(operation="read", database=database, partition=partition)

    def database_delete(self, database) -> tuple:
        """
        Deletes a specified database from CouchDB.

        Args:
            database (str): The name of the database to be deleted.

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_database(operation="delete", database=database)

    def database_find(self, database, query, partition="default") -> tuple:
        """
        Finds documents in a specified database that match a given query.

        Args:
            database (str): The name of the database to search in.
            query (dict): The query parameters to filter documents.
            partition (str, optional): The partition to search in. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_database(operation="find", database=database, partition=partition, query=query)

    def database_filter(self, database, query) -> tuple:
        """
        Filters documents in a specified database using a selector query.

        Args:
            database (str): The name of the database to filter documents from.
            query (dict): The key-value pairs to filter documents.

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_database(operation="filter", database=database, query=query)

    def database_truncate(self, database, partition="default") -> tuple:
        """
        Truncates a specified database by removing all documents except design documents.

        Args:
            database (str): The name of the database to truncate.
            partition (str, optional): The partition to truncate from. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        read_result = self.document_read(database=database, partition=partition)
        if read_result["status_code"] == 200:
            data = self.get_list_from_content(read_result["content"]["rows"])
            for row in data:
                row["_deleted"] = True
            return self.query_database(operation="", database=database, partition=partition, query=data, bulk=True)
        return read_result

    def document_upsert(self, database, data, partition="default") -> tuple:
        """
        Inserts or updates documents in bulk in a specified database.

        Args:
            database (str): The name of the database to upsert documents into.
            data (list): A list of documents to be upserted.
            partition (str, optional): The partition to insert data into. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_database(operation="", database=database, partition=partition, query=data, bulk=True)

    def document_create(self, database, data, partition="default") -> tuple:
        """
        Creates a new document in a specified database.

        Args:
            database (str): The name of the database to insert the document into.
            data (dict): The contents of the document to be created.
            partition (str, optional): The partition to insert data into. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_document(operation="create", database=database, partition=partition, data=data)

    def document_read(self, database, document="_all_docs", data="", partition="default") -> tuple:
        """
        Reads document(s) from a specified database.

        Args:
            database (str): The name of the database to read from.
            document (str, optional): The ID of the document to fetch. Defaults to "_all_docs".
            data (dict, optional): Extra parameters for the query. Defaults to an empty string.
            partition (str, optional): The partition to read from. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_document(operation="read", database=database, document=document, partition=partition,
                                   data=data)

    def document_update(self, database, document, data, partition=None) -> tuple:
        """
        Updates an existing document in a specified database.

        Args:
            database (str): The name of the database to update the document in.
            document (str): The ID of the document to be updated.
            data (dict): The updated contents of the document. Must include '_rev' field.
            partition (str, optional): The partition to update in. Defaults to None.

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_document(operation="update", database=database, partition=partition, document=document,
                                   data=data)

    def document_delete(self, database, document, rev, partition=None) -> tuple:
        """
        Deletes a specified document from a database.

        Args:
            database (str): The name of the database to delete the document from.
            document (str): The ID of the document to be deleted.
            rev (str): The most recent revision ID of the document.
            partition (str, optional): The partition to delete from. Defaults to None.

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        return self.query_document(operation="delete", database=database, partition=partition, document=document,
                                   rev=rev)

    @staticmethod
    def get_list_from_content(content):
        """
        Extracts a list of documents from the provided content.

        Args:
            content (list): The content containing documents.

        Returns:
            list: A list of documents extracted from the content.
        """
        return list(map(lambda doc: doc["doc"] if "doc" in doc else doc["value"], content))

    def get_id(self, question, partition="default"):
        """
        Generates a unique ID for a given question based on its content and partition.

        Args:
            question (dict): The question data to generate an ID for.
            partition (str, optional): The partition to include in the ID. Defaults to "default".

        Returns:
            str: The generated unique ID.
        """
        id_text = hashlib.md5(json.dumps(question).encode()).hexdigest()
        return f"{partition}:{id_text}"

    def add_id_and_creation_data_for_db_record(self, data, is_modified=False, partition="default"):
        """
        Adds an ID and creation/modification timestamps to a database record.

        Args:
            data (dict): The record data to modify.
            is_modified (bool, optional): Indicates if the record has been modified. Defaults to False.
            partition (str, optional): The partition to include in the ID. Defaults to "default".

        Returns:
            dict: The modified record data with added ID and timestamps.
        """
        logger.debug(data)
        logger.debug("In add_id_and_creation_data_for_db_record")
        if not is_modified:
            data["creation_date"] = str(datetime.datetime.utcnow())
        data["modification_date"] = str(datetime.datetime.utcnow())
        data["_id"] = self.get_id(data["questions"], partition=partition)
        return data

    def save_data(self, data, database, partition="default"):
        """
        Saves data into a specified database, creating the database if it does not exist.

        Args:
            data (dict): The data to be saved.
            database (str): The name of the database to save data into.
            partition (str, optional): The partition to save data into. Defaults to "default".

        Returns:
            tuple: A tuple containing the status code and content of the response.
        """
        logger.debug("Saving data into database")
        is_modified = True
        # Create database if not already created for packages
        try:
            self.database_create(database)
            is_modified = False
        except Exception as ex:
            logger.info("Database already exists")

        return self.document_upsert(
            database,
            [self.add_id_and_creation_data_for_db_record(
                data,
                is_modified,
                partition
            )]
        )

    def fetch_history(self, database, selector_query):
        """
        Fetches the history of records from a specified database based on a selector query.

        Args:
            database (str): The name of the database to fetch history from.
            selector_query (dict): The query to filter the records.

        Returns:
            list: A list of documents fetched from the database, or an empty list if the collection does not exist.
        """
        logger.debug(selector_query)
        docs = self.database_find(
            database=database,
            query=selector_query
        )
        if docs["status_code"] < 400:
            return docs["content"]["docs"]
        else:
            # In case collection is not created yet
            return []
