import redis
import os
from dotenv import load_dotenv

load_dotenv()
class RedisService:
    def __init__(self):
        self.__host = os.getenv("HOST_REDIS")
        self.__port = os.getenv("PORT_REDIS")
        self.__redis_client = redis.Redis(host=self.__host, port=int(self.__port), decode_responses=True)
        try:
            if self.__redis_client.ping():
                print("Connected to Redis successfully!")
        except redis.ConnectionError:
            print("Failed to connect to Redis.")

    def setKey(self, key, value):
        self.__redis_client.set(key, value)

    def getValue(self, key):
        self.__redis_client.get(key)

    def deleteValue(self, key):
        self.__redis_client.delete(key)
