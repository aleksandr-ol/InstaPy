import pymongo


class Database(object):
    def __init__(self, host="localhost", port=27017, database="my_databse"):
        self.db_client = pymongo.MongoClient(host, int(port))
        self.db = self.db_client[database]

    def get_database(self):
        return self.db

    def get_collection(self, collection=None):
        if collection is not None:
            return self.db[collection]

