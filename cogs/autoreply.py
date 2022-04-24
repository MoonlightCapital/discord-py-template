import nextcord as discord
from nextcord.ext import commands

from database.AutoReply import AutoReply as AutoReplydb

class AutoReply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def find_reply(self, userId):
        return await AutoReplydb.find_one({'_id': userId})

    async def find_discord_user(self, userId):
        user = self.bot.get_user(userId)
        if (user is None):  user = await self.bot.fetch_user(userId)
        return user.display_name

    @commands.command()
    async def autoreply(self, ctx, *, message=''):
        """
        Sets up or modifies an autoreply message for the command author. If no message is supplied, instead deletes any existing autoreply for the author.
        """
        print('Starting new autoreply')
        existing_reply = await self.find_reply(str(ctx.author.id))

        if (existing_reply is None):
            if (message == ''):
                print('Aborting autoreply deletion, does not exist')
                return # do nothing, cannot delete an autoreply that does not exist
            
            # add new autoreply to database
            new_entry = AutoReplydb(user=str(ctx.author.id), message=message)

            await new_entry.commit()
            await ctx.send('New auto reply created for ' + ctx.author.display_name)
            print('New auto reply created for ' + ctx.author.display_name)

        else:
            if (message == ''):
                await existing_reply.delete()
                await ctx.send('Deleted autoreply for ' + ctx.author.display_name)
                print('Deleted autoreply for ' + ctx.author.display_name)
                return

            # update auto reply message
            existing_reply['message'] = message

            await existing_reply.commit()
            await ctx.send('Updated autoreply for ' + ctx.author.display_name)
            print('Updated auto reply for ' + ctx.author.display_name)
            
    @commands.Cog.listener("on_message")
    async def check_for_tags(self, message):
        """
        This event checks every message received by the bot for user tags that have an auto-reply set up.
        """
        if message.author.bot:
            return  # ignore all bots
            
        print('reading message for autoreply...')

        for i in message.mentions:
            print('found message mentioning ' + i.display_name)
            reply = await self.find_reply(str(i.id))
            if (reply is None): continue # mentioned user has not set up a reply, go next

            await message.channel.send(i.display_name + ' is not currently available. They left this note:\n`' + reply['message'] + '`')

        



def setup(bot):
    bot.add_cog(AutoReply(bot))