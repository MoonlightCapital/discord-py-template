import os

from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance

instance = None

def init(dburl, dbname):
    global instance

    client = AsyncIOMotorClient(dburl)

    instance = Instance(client[dbname])
