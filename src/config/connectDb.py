from pymongo import MongoClient
import os

def connect_to_mongodb():
    try:
        # Create a MongoClient to the running mongod instance
        client = MongoClient(os.getenv(''))
        
        # Access the specified database
        db = client["symbols_predict"]
        
        # Optionally print the databases and collections
        print("Databases:", client.list_database_names())
        print("Collections in database:", db.list_collection_names())
        
        return db
    except Exception as e:
        print(f"An error occurred: {e}")
        return None