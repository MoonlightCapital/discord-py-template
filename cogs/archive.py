from datetime import datetime
import sys
import os
import glob
import time
from internal import constants
import nextcord as discord
from nextcord.ext import commands

class Archive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Get identifying path for this archive, and remove attachments from past archive
    # I do not save versioned attachment archives because I do not own enough bits
    def getTextFilePath(self, ctx):
        intermediate = str(ctx.guild.name).replace(' ', '-')
        guildName = intermediate.replace('\'', '')
        textFilePath = '../archives/' + guildName + '/' + ctx.channel.name + '/'

        try:
            os.makedirs(os.path.dirname(textFilePath), exist_ok=True)
        except FileExistsError:
            files = glob.glob(textFilePath)
            for f in files: os.remove(f)

        return textFilePath

    @commands.group(name='archive')
    async def base_archive(self, ctx): pass

    @base_archive.command(name='all')
    @commands.bot_has_permissions(read_message_history=True)
    @commands.is_owner()
    async def all(self, ctx):
        """
        Records entire history of this channel onto the bot's storage. All images are downloaded and the text log is saved.
        """

        await ctx.message.add_reaction(constants.AFFIRMATIVE_REACTION_EMOJI)
        textFilePath = self.getTextFilePath(ctx)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        textFileName = textFilePath + timestr + '.txt'

        with open(textFileName, 'w') as f:
            f.write('Archived channel ' + ctx.channel.name + 'from guild: ' + ctx.guild.name + '\n')
            async for message in ctx.channel.history(limit=sys.maxsize, oldest_first=True):
                output = '[' + str(message.created_at) + ', ' + message.author.name + ']: '

                # process attachments, appropriately assign filetypes to images
                # other filetypes can be recovered using the information from the content type added to the log
                if len(message.attachments) > 0:
                    for attachment in message.attachments:
                        filetype = ''
                        if 'image' in str(attachment.content_type): filetype = '.png'
                        output += '[ATTACHMENT] ' + str(attachment.id) + ' content_type: ' + str(attachment.content_type) + '\n'
                        await attachment.save(textFilePath + 'attachments/' + str(attachment.id) + filetype)
                else: output += message.content + '\n'


                f.write(output)
                print('wrote a message to ' + f.name)
            f.close()

        msg = await ctx.send('This channel has been saved!')
        await ctx.message.remove_reaction(constants.AFFIRMATIVE_REACTION_EMOJI, msg.author)

    @base_archive.command(name='')
    @commands.bot_has_permissions(read_message_history=True)
    @commands.is_owner()
    async def archive(self, ctx):
        """
        Records text log history of this channel onto the bot's storage. Attachments are skipped, but links remain. 
        """

        await ctx.message.add_reaction(constants.AFFIRMATIVE_REACTION_EMOJI)
        textFilePath = self.getTextFilePath(ctx)
        timestr = time.strftime("%Y%m%d-%H%M%S")
        textFileName = textFilePath + timestr + '.txt'

        with open(textFileName, 'w') as f:
            f.write('Archived channel ' + ctx.channel.name + 'from guild: ' + ctx.guild.name + '\n')

            async for message in ctx.channel.history(limit=sys.maxsize, oldest_first=True):
                output = '[' + str(message.created_at) + ', ' + message.author.name + ']: '

                # make note of attachments but do not download them for the sake of my precious hard drives
                if len(message.attachments) > 0:
                    for attachment in message.attachments:
                        output += '[ATTACHMENT NOT SAVED] content_type: ' + str(attachment.content_type) + '\n'
                else: output += message.content + '\n'


                f.write(output)
                print('wrote a message to ' + f.name)
            f.close()

        msg = await ctx.send('This channel has been saved!')
        await ctx.message.remove_reaction(constants.AFFIRMATIVE_REACTION_EMOJI, msg.author)

def setup(bot):
    bot.add_cog(Archive(bot))
