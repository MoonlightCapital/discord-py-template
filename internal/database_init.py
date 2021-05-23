import os

from motor.motor_asyncio import AsyncIOMotorClient
from umongo.frameworks.motor_asyncio import MotorAsyncIOInstance

instance = None

def init(dburl, dbname):
    global instance

    client = AsyncIOMotorClient(dburl)

    instance = MotorAsyncIOInstance(client[dbname])
