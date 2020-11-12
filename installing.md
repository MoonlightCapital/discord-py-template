# Installing and starting to work with the bot

## Clone the repository
```
git clone https://github.com/MoonlightCapital/something
```

## Install dependencies
```
pip3 install -r requirements.txt
```

## Configuration
The configuration file resides at location `data/config.json`. An example file you can copy is `data/config.example.json`

### Config values
`prefix`: The prefix to use for the bot (required)
`description`: A description of the bot, to show in the help command
`intents`: Array of strings that represent [gateway intents](https://discord.com/developers/docs/topics/gateway#gateway-intents). For permitted values, look for the attributes in [the Discord.py docs](https://discordpy.readthedocs.io/en/latest/api.html#discord.Intents). Special values (`all`, `default`, and `none`) are also permitted.
`database`: Set this to true to enable the database (will require additional variables, see below)

### Environment variables
Some secrets are best to be kept in a separate file from configuration. You can also add your own. Put them in a file named `.env`. Again, an example file is provided. They are all written in UPPER_SNAKE_CASE and are __case-sensitive__.
For now, the only one you need to know is `BOT_TOKEN`, which is to set the Discord bot's token.

# Advanced functionalities

## Database
umongo is provided by the bot, and ready to be used. **To enable it, set the `database` key of config.json to true.**
Then set up those variables for your MongoDB instance, so the bot can connect. Those have to be set either by env or config file.

`MONGO_CONNECTION_STRING`/`mongoConnectionString` for the connection string.
`MONGO_DATABASE_NAME`/`mongoDbName` indicates the database name.

> Note: env is recommended over config.json for this sensitive data

Then, you're ready to connect. To implement database collections schemas, put the class files inside the `/database` folder and you can import them as modules, for example:

```py
# database/Dummy.py
from umongo import Document, validate
from umongo.fields import *

from internal.database_init import instance

@instance.register
class Dummy(Document):
    """A dummy document type, to show how to operate with the database"""

    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    author = StringField(required=True, max_length=50)


# In any of your cog files
from database.Dummy import Dummy

my_dummy_entry = Dummy(
  title='Sample Post',
  content='Some engaging content',
  author='Scott'
) # Instantiates a class from the database

my_dummy_entry.commit() # Saves the document
```

For an in-depth guide on umongo, refer to https://umongo.readthedocs.io/en/latest/index.html

## Keep alive endpoint
For some free hosting services like [REPL.it](https://repl.it), you may need to keep your bot alive 24/7 through an external input. You can set the `KEEP_ALIVE` environment variable to true (or literally anything but empty since they're strings). It will create a page you can send HTTP GET requests to, on the root of the web directory. If you open the page in your browser, you should see "I'm alive" in plain text. A good autopinger is https://cron-job.org, which is completely free and can ping every minute. The endpoint uses port 8080.

## Docker
A Dockerfile is provided. You can build the image and run it in a container like any other Docker app.

# FAQ/Troubleshooting

## What Python versions are supported?
This template has been tested with 3.8.5 and 3.9.0. I believe 3.7 works as well, but 3.9 is the way to go.

## I am receiving a "AttributeError: 'NoneType' object has no attribute 'register'"
You're trying to use the database without having set the database key in the config file to true, thus no database exists and you cannot perform operations on it.
