from pymongo import MongoClient


def get_db(db_name: str = "employee_db"):
    client = MongoClient("mongodb://localhost:27017")
    return client[db_name]