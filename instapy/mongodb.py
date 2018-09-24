import pymongo
import os


class Database(object):
    def __init__(self, host="localhost", port=27017, database="my_databse"):
        username = os.getenv(
            "MONGODB_USER", "")
        password = os.getenv(
            "MONGODB_PWD", "")
        constr = "mongodb://%s:%s@%s:%s/%s" % (username,
                                               password, host, int(port), database)
        try:
            self.db_client = pymongo.MongoClient(constr)
            self.db = self.db_client[database]
        except Exception as error:
            print(error)

    def get_database(self):
        return self.db

    def get_collection(self, collection=None):
        if collection is not None:
            return self.db[collection]
