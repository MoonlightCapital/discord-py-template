import sys
import nextcord as discord
import re
import json
from nextcord.ext import commands

class Moderate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    config = None
    with open('data/config.json') as f:
        config = json.load(f)
    
    async def reprimand_offender(self, user: discord.User, reason=''):
        reprimand = self.bot.get_cog('Reprimand')
        if reprimand is not None:
            await reprimand.process_reprimand(user, reason)
        else:
            print('Could not reprimand offender, self.bot.get_cog(\'Reprimand\' is None.')


    @commands.Cog.listener("on_message")
    async def check_for_links(self, message):
        """
        This event checks every top-level message received in the video_essay_channel to make sure it has a link.
        """
        if message.author.bot: return  # ignore all bots
        if message.channel.name != self.config['video_essay_channel']: # ignore messages that aren't top-level and in video_essay_channel
            print('Moderate.py: Wrong channel, skipping message listener...\n')
            return
        if message.thread is not None: 
            print('Moderate.py: Thread created, skipping message listener...\n')
            return # ignore messages that create threads

        print('reading message for link...')
        link = re.search('((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:\-_=#][a-zA-Z0-9\.\/\?\:\-_=#]+', message.content)

        if link is None: # act upon linkless message
            msg = await message.reply('This message does not contain any link(s); if it relates to previously linked media, please consider making a threaded response to the original post. You have been reprimanded, and this notification will self-destruct when you move your message.')
            await self.reprimand_offender(message.author, 'Moderator: #' + self.config['video_essay_channel'] + ' rule violation.')

        else:
            print('message has link as expected')

        
    @commands.Cog.listener("on_message_delete")
    @commands.bot_has_permissions(read_message_history=True)
    async def clean_up_channel(self, deletedMessage: discord.Message):
        """
        This event checks every deleted message in the media channel for replies from itself to remove / clean up. 
        """
        if message.author.bot: return  # ignore all bots
        if message.channel.name != self.config['video_essay_channel']: # ignore messages that aren't top-level and in video_essay_channel
            print('Moderate.py: Wrong channel, skipping message listener...\n')
            return
        
        # find the reply to the deleted message and clean it up
        async for message in deletedMessage.channel.history(limit=sys.maxsize, before=None, after=deletedMessage.created_at):
            if (message.author.id == self.bot.user.id) and (message.reference.message_id == deletedMessage.id):
                await message.delete()
                return 
                # there will be only one message to remove
                # it is likely to be the very next message in the history, so this method minimizes iteration
    


def setup(bot):
    bot.add_cog(Moderate(bot))
