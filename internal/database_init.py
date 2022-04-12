import os

from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance
from pymongo.errors import ConnectionFailure

instance = None

def init(dburl, dbname):
    global instance

    print('initializing database instance')

    client = AsyncIOMotorClient(dburl)
    
    try:
        # The ping command is cheap and does not require auth.
        client.admin.command('ping')
    except ConnectionFailure:
        print("Server not available")

    instance = MotorAsyncIOInstance(client[dbname])
