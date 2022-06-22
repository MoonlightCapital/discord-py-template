import nextcord as discord
import re
from nextcord.ext import commands

from internal import clear, constants

class Moderate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.Cog.listener("on_message")
    async def check_for_links(self, message):
        """
        This event checks every top-level message received in #babe-wake-up to make sure it has a link.
        """
        if message.author.bot: return  # ignore all bots
        if message.channel.name != 'babe-wake-up': # ignore messages that aren't top-level and in babe-wake-up
            print('Wrong channel, skipping message listener...\n')
            return
            
        print('reading message for link...')

        #regexLinkPattern = re.compile('((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
        link = re.search('((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:\-_=#][a-zA-Z0-9\.\/\?\:\-_=#]+', message.content)
        #link = regexLinkPattern.search(message.content)

        if link is None: # act upon linkless message
            
            msg = await message.channel.send('' + message.author.mention + ' this message does not contain any links. If this message relates to a previously linked video, please consider making a threaded response to that video. This notification will self-destruct when you move your message.')
            
            # delete message after 2 minutes or if clear reaction is clicked, whichever comes first
            await clear.clear_on_message_deleted(self.bot, msg, message)

        else:
            print('message has link as expected')


def setup(bot):
    bot.add_cog(Moderate(bot))
