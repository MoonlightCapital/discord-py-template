import os
import asyncio
import json
import logging
from pathlib import Path

import nextcord as discord
from nextcord.ext import commands

from internal.botclass import Bot
from internal.intentcalculator import calculate_intents
from internal.keepalive import keep_alive

def load_config():
    from os.path import join, dirname
    from dotenv import load_dotenv

    # Create .env file path.
    dotenv_path = join(dirname(__file__), '.env')

    # Load file from the path.
    load_dotenv(dotenv_path)

    with open('data/config.json', 'r', encoding='utf-8') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)


async def run():
    """
    Where the bot gets started. If you wanted to create an database connection pool or other session for the bot to use,
    it's recommended that you create it here and pass it to the bot as a kwarg.
    """

    def get_config_var(env_name, config_path, config_name, **kwargs):
        """
        Attempts to get a variable from the env file, then from the config key, and finally, if none found, returns the fallback value.
        """
        v = os.getenv(env_name, config_path.get(config_name, kwargs.get('fallback')))

        if v is None and kwargs.get('error', False):
            raise KeyError(f'Failed to get configuration key. Env name: {env_name}, Config name: {config_name}')

        return v

    config = load_config()
    intents = calculate_intents(config.get('intents', []))

    if config.get('database') is True:

        from internal import database_init

        database_init.init(
            get_config_var('MONGO_CONNECTION_STRING', config, 'mongoConnectionString', error=True),
            get_config_var('MONGO_DATABASE_NAME', config, 'mongoDbName', fallback='dpytemplate_default_db')
        )


    bot = Bot(
            config=config,
            description=config['description'],
            intents=intents
        )

    bot.config = config

    try:
        # Start the keepalive endpoint
        if os.getenv('KEEP_ALIVE'):
            keep_alive()

        token = get_config_var('BOT_TOKEN', config, 'token', error=True)
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.logout()
        exit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
