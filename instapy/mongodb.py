import pymongo
import os


class Database(object):
    def __init__(self, host="localhost", port=27017, database="instapy"):
        host = os.getenv("MONGODB_HOST", "localhost"),
        port = int(os.getenv("MONGODB_PORT", 27017)),
        database = os.getenv("MONGODB_DB", "instapy"),
        username = os.getenv(
            "MONGODB_USER", "")
        password = os.getenv(
            "MONGODB_PWD", "")
        if username and password:
            constr = "mongodb://%s:%s@%s:%s/%s" % (username,
                                                   password, host, int(port), database)
        else:
            constr = "mongodb://%s:%s/%s" % (host, int(port), database)
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
