import nextcord as discord
from nextcord.ext import commands

from pymongo import DESCENDING
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

    async def send_autoreply(self, message, user):
        reply = await self.find_reply(str(user.id))
        if (reply is None): return # mentioned user has not set up a reply, go next

        await message.channel.send(user.display_name + ' is not currently available. They left this note:\n`' + reply['message'] + '`')

    @commands.group(name='autoreply')
    async def base_autoreply(self, ctx): pass

    @base_autoreply.command(name='')
    async def autoreply(self, ctx, *, message=''):
        """
        Sets up or modifies an autoreply message for the command author. If no message is supplied, instead deletes any existing autoreply for the author.
        """
        print('Starting new autoreply')
        existing_reply = await self.find_reply(str(ctx.author.id))

        # alter message to change any tags into plaintext
        for mentioned in ctx.message.mentions:
            mention_text = '<@' + str(mentioned.id) + '>'
            print('mentioned id is: ' + mention_text)
            print('message contents were: ' + ctx.message.content)
            mentionee = await self.find_discord_user(mentioned.id)
            print('mentionee name is: ' + mentionee)
            plaintext_mention = u'@\u200c' + mentionee
            message = message.replace(mention_text, plaintext_mention)

        if (existing_reply is None):
            if (message == ''):
                print('Aborting autoreply deletion, does not exist')
                await ctx.send('My brother in christ you do not have an autoreply set, so I cannot delete.')
                return # do nothing, cannot delete an autoreply that does not exist
            
            # add new autoreply to database
            new_entry = AutoReplydb(user=str(ctx.author.id), message=message)

            await new_entry.commit()
            await ctx.send('New auto reply created for `' + ctx.author.display_name + '`')
            print('New auto reply created for ' + ctx.author.display_name)

        else:
            if (message == ''):
                await existing_reply.delete()
                await ctx.send('Deleted autoreply for `' + ctx.author.display_name + '`')
                print('Deleted autoreply for ' + ctx.author.display_name)
                return

            # update auto reply message
            existing_reply['message'] = message

            await existing_reply.commit()
            await ctx.send('Updated autoreply for `' + ctx.author.display_name + '`')
            print('Updated auto reply for ' + ctx.author.display_name)

    @base_autoreply.command(name='clear')
    @commands.is_owner()
    async def clear(self, ctx, user: discord.User):
        """
        Admin: Clears a given user\'s autoreply setting. 
        """

        print('Starting autoreply-clear')
        existing_entry = await self.find_reply(str(user.id))

        if (existing_entry is None):
            msg = await ctx.send("User `" + user.display_name + "` does not have an autoreply set.")

        else:
            await existing_entry.delete()
            print('Removed user \"' + user.display_name + '\'s\" autoreply setting.')
            await ctx.send('Removed autoreply setting for `' + user.display_name + '`')

    @base_autoreply.command(name='list')
    @commands.is_owner()
    async def list(self, ctx):
        """
        Admin: Prints autoreplies alphabetically by user, and in the case of >10 records, writes the whole lot to a text file and attaches.
        """
        log_output = '```\n'
        file_output = log_output
        count = 0

        length = await AutoReplydb.count_documents()
        log_list = await AutoReplydb.find().sort('user', DESCENDING).to_list(length)

        for doc in log_list:
            if count < 10:
                user_display = await self.find_discord_user(doc.user)
                log_output += user_display + ":\t" + str(doc.message) + "\n"

                file_output = log_output
                count += 1
            else:
                # put the rest of the log in a text file
                file_output += user_display + ":\t" + str(doc.message) + "\n"
            
        log_output += "```"
        file_output += "```"
        
        msg = await ctx.send(log_output)

        if count >= 10:
            # write to file
            with open("autoreplies.txt", "w") as file:
                file.write(file_output)

            # send file to Discord in message
            with open("autoreplies.txt", "rb") as file:
                await ctx.send("Here is the full autoreplies list:", file=discord.File(file, "result.txt"))
            
    @commands.Cog.listener("on_message")
    async def check_for_tags(self, message):
        """
        This event checks every message received by the bot for user tags that have an auto-reply set up.
        """
        if message.author.bot: return  # ignore all bots
        if message.content[0:12] == 'wb autoreply': return # ignore commands from this module
            
        print('Autoreply.py: reading message...')
        mentioned = []

        for i in message.mentions:
            print('found message mentioning ' + i.display_name)
            mentioned.append(str(i.id))

            await self.send_autoreply(message, i)

        for j in message.role_mentions:
            print('found message mentioning role ' + j.name)

            for k in j.members:
                print('checking ' + k.display_name + ' for a message')

                # check if user already processed (users have many roles and good to avoid duplicates)
                if str(k.id) in mentioned: continue
                else: mentioned.append(str(k.id))
                
                await self.send_autoreply(message, k)

def setup(bot):
    bot.add_cog(AutoReply(bot))