import nextcord as discord
from nextcord.ext import commands
from pymongo import DESCENDING
import pprint

from database.ReprimandLog import ReprimandLog

class Reprimand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def find_user(self, userId):
        return await ReprimandLog.find_one({'_id': userId})
    
    async def find_discord_user(self, userId):
        user = self.bot.get_user(userId)
        if (user is None):  user = await self.bot.fetch_user(userId)
        return user.display_name

    async def process_reprimand(self, mandee: discord.User, reason=''):
        print('Starting reprimand')
        existing_entry = await self.find_user(str(mandee.id))
        pprint.pprint(existing_entry)

        if (existing_entry is None):
            new_entry = ReprimandLog(user=str(mandee.id))
            
            # add potential reason to new log's reason list
            if reason != '': new_entry['reasons'].append(reason)

            await new_entry.commit()
            print('new reprimand log created for ' + mandee.display_name)

        else:
            existing_entry['count'] += 1

            # add potential reason to log's reason list
            if reason != '': existing_entry['reasons'].append(reason)

            await existing_entry.commit()
            print('incremented reprimand log for ' + mandee.display_name)

        response = "" + mandee.display_name + ", you're reprimanded!"
        if reason != '': response += " Reason given: `" + reason + "`"

        return response

    @commands.command()
    async def reprimand(self, ctx, mandee: discord.User, *, reason=''):
        """
        Basic reprimand command, called with the name of the reprimandee. Record is made of the reprimand in the database.
        """
        confirmation = await self.process_reprimand(mandee, reason)
        msg = await ctx.send(confirmation)

    @commands.command()
    async def reprimands(self, ctx, mandee:discord.User=None):
        """
        No User: Prints the top ten reprimandees, and in the case of a log >10 records, writes the whole log to a text file and attaches. 

        User Provided: Prints the top ten reasons a given user was reprimanded. In the event of >10 reasons, they are all output into
        a text file
        """
        log_output = '```\n'
        file_output = log_output
        count = 0

        if mandee is None:
            length = await ReprimandLog.count_documents()
            log_list = await ReprimandLog.find().sort('count', DESCENDING).to_list(length)
            for doc in log_list:
                if count < 10:
                    user_display = await self.find_discord_user(doc.user)
                    log_output += user_display + ": " + str(doc.count) + " reprimand"

                    # only add the s if the count is more than one
                    log_output += "s\n" if doc.count > 1 else "\n"

                    file_output = log_output
                    count += 1
                else:
                    # put the rest of the log in a text file
                    file_output += user_display + ": " + str(doc.count) + " reprimand"

                    # only add the s if the count is more than one
                    file_output += "s\n" if doc.count > 1 else "\n"
        
        # If given a user arg, instead list reasons they have been reprimanded
        else:
            print('getting reasons for ' + mandee.display_name)
            existing_entry = await self.find_user(str(mandee.id))

            # check for edge cases of unreprimanded or empty reasons list
            if existing_entry is None:
                return await ctx.send('`' + mandee.display_name + "` has not been reprimanded")
            if (len(existing_entry['reasons']) == 0):
                return await ctx.send('`' + mandee.display_name + "` does not have any justified reprimands")

            # construct return dialog/document
            for reason in existing_entry['reasons']:
                if count < 10:
                    log_output += "- " + reason + "\n"
                    count += 1
                
                # put the whole log in a text file
                file_output += "- " + reason + "\n"
            
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


    @commands.is_owner()
    @commands.command()
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
