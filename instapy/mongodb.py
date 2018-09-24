import pymongo
import os


class Database(object):
    def __init__(self, host="localhost", port=27017, database="my_databse"):
        try:
            self.db_client = pymongo.MongoClient(host, port=int(port),
                                                 username=os.getenv(
                "MONGODB_USER", None),
                password=os.getenv(
                "MONGODB_PWD", None)
            )
            self.db = self.db_client[database]
        except Exception as error:
            print(error)

    def get_database(self):
        return self.db

    def get_collection(self, collection=None):
        if collection is not None:
            return self.db[collection]
