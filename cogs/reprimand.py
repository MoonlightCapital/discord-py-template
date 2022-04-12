import nextcord as discord
from nextcord.ext import commands
from pymongo import DESCENDING
import pprint

# from internal.database_init import instance
from database.ReprimandLog import ReprimandLog

class Reprimand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def find_user(self, userId):
        return await ReprimandLog.find_one({'_id': userId})

    @commands.command()
    async def reprimand(self, ctx, mandee: discord.User):
        """
        Basic reprimand command, called with the name of the reprimandee. Record is made of the reprimand in the database.
        """

        print('Starting reprimand')
        existing_entry = await self.find_user(str(mandee.id))
        pprint.pprint(existing_entry)

        if (existing_entry is None):
            new_entry = ReprimandLog(user=str(mandee.id))
            await new_entry.commit()
            print('new reprimand log created for ' + mandee.display_name)

        else:
            existing_entry['count'] += 1
            await existing_entry.commit()
            print('incremented reprimand log for ' + mandee.display_name)

        print(mandee.id)

        response = "" + mandee.display_name + ", you're reprimanded!"

        msg = await ctx.send(response)

    @commands.command()
    async def reprimands(self, ctx):
        """
        Prints the top ten reprimandees, and in the case of a log >10 records, writes the whole log to a text file and attaches. 
        """
        length = await ReprimandLog.count_documents()
        log_list = await ReprimandLog.find().sort('_id', DESCENDING).to_list(length)
        log_output = '```\n'
        file_output = log_output
        count = 0
        for doc in log_list:
            if count < 10:
                user = self.bot.get_user(doc.user)
                if (user is None):  user = await self.bot.fetch_user(doc.user)
                user_display = user.display_name

                log_output += user_display + ": " + str(doc.count) + " reprimand"

                if doc.count > 1: log_output += "s\n"
                else: log_output += "\n"

                file_output = log_output
                count += 1
            else:
                # put the whole log in a text file
                file_output += user_display + ": " + str(doc.count) + " reprimand"

                if doc.count > 1: file_output += "s\n"
                else: file_output += "\n"
        
        log_output += "```"
        file_output += "```"
        
        msg = await ctx.send(log_output)

        if count >= 10:
            # write to file
            with open("reprimands.txt", "w") as file:
                file.write(file_output)

            # send file to Discord in message
            with open("reprimands.txt", "rb") as file:
                await ctx.send("Here is the full reprimand log:", file=discord.File(file, "result.txt"))


    @commands.command()
    @commands.is_owner()
    async def reprimand_clear(self, ctx, mandee: discord.User):
        """
        Admin: Clears a given user from the reprimand log. 
        """

        print('Starting reprimand_clear')
        existing_entry = await self.find_user(str(mandee.id))
        pprint.pprint(existing_entry)

        if (existing_entry is None):
            msg = await ctx.send("User `" + mandee.display_name + "` not found in the log")

        else:
            await existing_entry.delete()
            print('Removed user \"' + mandee.display_name + '\" from the log')
            await ctx.send('Removed user `' + mandee.display_name + '` from the log')



def setup(bot):
    bot.add_cog(Reprimand(bot))
