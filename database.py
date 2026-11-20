from pymongo import MongoClient

from config import MONGO_DATABASE, MONGO_URI


def dbConnection():
    """Return the configured MongoDB database handle."""
    client = MongoClient(MONGO_URI)
    return client[MONGO_DATABASE]
