import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import OperationFailure
from dotenv import load_dotenv

load_dotenv()


def connect_to_db():
    user = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASSWORD')
    mongo_url = f'mongodb+srv://{user}:{password}@cluster0.iphuf8z.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

    client = MongoClient(mongo_url, server_api=ServerApi('1'))
    return client.goit_3


def initial_data(db):
    db.cats.insert_many(
        [
            {
                "name": "barsik",
                "age": 3,
                "features": ["ходить в капці", "дає себе гладити", "рудий"],
            },
            {
                "name": "Lama",
                "age": 2,
                "features": ["ходить в лоток", "не дає себе гладити", "сірий"],
            },
            {
                "name": "Liza",
                "age": 4,
                "features": ["ходить в лоток", "дає себе гладити", "білий"],
            },
        ]
    )


def get_all(db):
    result = db.cats.find({})

    for el in result:
        print(el)


def get_by_name(db, name):
    result = db.cats.find_one({'name': name})
    print(result)


def update_age_by_name(db, name, new_age):
    db.cats.update_one({'name': name}, {"$set": {"age": new_age}})
    get_by_name(db, name)


def add_feature_by_name(db, name, new_feature):
    db.cats.update_one({'name': name}, {'$push': {'features': new_feature}})
    get_by_name(db, name)


def delete_by_name(db, name):
    db.cats.delete_one({"name": name})


def delete_all(db):
    db.cats.delete_many({})


if __name__ == '__main__':
    try:
        db = connect_to_db()
        initial_data(db)
        get_all(db)
        get_by_name(db, 'Lama')
        update_age_by_name(db, 'Liza', 7)
        add_feature_by_name(db, 'barsik', 'смиливий')
        delete_by_name(db, 'barsik')
        delete_all(db)
    except OperationFailure:
        print('Error to connect to Mongo DB')
