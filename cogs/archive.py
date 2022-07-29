from datetime import datetime
import sys
import os
import glob
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

        # msg = await ctx.send('Working to archive this channel...')
        await ctx.message.add_reaction(constants.AFFIRMATIVE_REACTION_EMOJI)

        # make dir for attachments if doesn't exist, otherwise wipe dir
        if not os.path.exists('../archives/' + ctx.channel.name + '/'):
            os.makedirs('../archives/' + ctx.channel.name + '/')
        else:
            files = glob.glob('../archives/' + ctx.channel.name + '/*')
            for f in files:
                os.remove(f)

        with open('../archives/' + ctx.channel.name + '.txt', 'w') as f:
            async for message in ctx.channel.history(limit=sys.maxsize, oldest_first=True):
                output = '[' + str(message.created_at) + ', ' + message.author.name + ']: '

                # process attachments, appropriately assign filetypes to images
                # other filetypes can be recovered using the information from the content type added to the log
                if len(message.attachments) > 0:
                    for attachment in message.attachments:
                        filetype = ''
                        if 'image' in str(attachment.content_type): filetype = '.png'
                        output += '[ATTACHMENT] ' + str(attachment.id) + ' content_type: ' + str(attachment.content_type) + '\n'
                        await attachment.save('../archives/' + ctx.channel.name + '/' +str(attachment.id) + filetype)
                else: output += message.content + '\n'


                f.write(output)
                print('wrote a message to ' + f.name)
            f.close()

        msg = await ctx.send('This channel has been saved!')
        await ctx.message.remove_reaction(constants.AFFIRMATIVE_REACTION_EMOJI, msg.author)

def setup(bot):
    bot.add_cog(Archive(bot))
