from datetime import datetime
import urllib.request
import sys
import os
from internal import constants
import nextcord as discord
from nextcord.ext import commands

class Archive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(read_message_history=True)
    @commands.is_owner()
    async def archive(self, ctx):
        """
        Records entire history of this channel onto the bot's storage. All images are downloaded and the text log is saved.
        """

        msg = await ctx.send('Working to archive this channel...')

        with open('../archives/' + ctx.channel.name + '.txt', 'w') as f:
            async for message in ctx.channel.history(limit=sys.maxsize, oldest_first=True):
                output = '[' + str(message.created_at) + ', ' + message.author.name + ']: '
                if len(message.attachments) > 0:
                    for attachment in message.attachments:
                        output += '[ATTACHMENT] ' + attachment.url
                else: output += message.content + '\n'
                f.write(output)
                print('wrote a message to ' + f.name)
            f.close()

        msg = await ctx.send('This channel has been saved!')

def setup(bot):
    bot.add_cog(Archive(bot))
