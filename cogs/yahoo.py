from struct import unpack
import nextcord as discord
import json
from nextcord.ext import commands
from yfpy.data import Data
from yfpy.query import YahooFantasySportsQuery as YahooQuery
from yfpy.utils import unpack_data
from yfpy.models import League, Team, Standings, Scoreboard, Manager

from database.FantasyManagers import FantasyManagers

class Yahoo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Data.retrieve(filename, yf_query, params=None, data_type_class=None, new_data_dir=None)
    controller = Data('../yahoo', True)

    # api id, secret, league_id, max_team_name_length
    config = None
    with open('data/private.json') as f:
        config = json.load(f)
        
    async def find_user(self, userId):
        return await FantasyManagers.find_one({'_id': userId, 'league': self.config['league_id']})
    
    async def find_discord_user(self, userId):
        user = self.bot.get_user(userId)
        if (user is None):  user = await self.bot.fetch_user(userId)
        return user.display_name

    async def assign_user_to_team(self, userId: str, teamId: int):
        # ensure teamId is not bound already
        existing_binding = await FantasyManagers.find_one({'team': teamId})
        if (existing_binding is not None):
            return False
        
        # bind userId to team
        new_entry = FantasyManagers(user=userId)
        new_entry['team'] = teamId
        new_entry['league'] = self.config['league_id']
        await new_entry.commit()
        return True

    def enforce_sports_channel():
        async def predicate(ctx):
            if ctx.guild is not None and ((str(ctx.guild.name) != 'Dedotated waam' and str(ctx.guild.name) != 'An-D\'s waambot dev') or str(ctx.channel.name) != 's-p-o-r-t-s'):
                print('ff command used outside of sports channel but not in a DM, skipping..\n')
                await ctx.send(':rotating_light: Cannot use a waambot ff command in this channel')
                return False
            return True
        return commands.check(predicate)

    def enforce_user_registered():
        async def predicate(ctx):
            with open('data/private.json') as f:
                config = json.load(f)
                existing_user = await FantasyManagers.find_one({'_id': str(ctx.author.id), 'league': config['league_id']})
                if (existing_user is None): 
                    await ctx.send(':rotating_light: You must be registered to use this command. Use `wb ff teaminfo` to find your team and `wb ff register [ID]` to register.')
                    return False
                else: return True
        return commands.check(predicate)

    @commands.group(aliases=['ff', 'fantasy'])
    @enforce_sports_channel()
    async def yahoo(self, ctx): pass

    @yahoo.command()
    @enforce_user_registered()
    async def test(self, ctx):
        """
        A test command, which can be used to test components.
        """
        print('Successful Yahoo FF test\n')
        msg = await ctx.send('Successful Yahoo FF test')
        pass
 
    @yahoo.command(name='register')
    async def register(self, ctx, teamNo: int):
        """
        Register a team in the league to yourself. This facilitates other commands such as `wb ff team` to show you your own team by default.
        """
        # Pull team ID info
        query = YahooQuery('data/', self.config['league_id'])
        leagueTeams = self.controller.retrieve('league_teams', query.get_league_teams)

        # Stop if teamNo is bad
        if (teamNo < 0 or teamNo > len(leagueTeams)):
            await ctx.send(":rotating_light: Invalid Team ID number. Check IDs by using `wb ff teaminfo` and try again.")
            return

        # Check for commanding user in the FantasyManagers mongodb doc
        existing_entry = await self.find_user(str(ctx.author.id))

        # If this is a new user
        if (existing_entry is None):
            result = await self.assign_user_to_team(str(ctx.author.id), teamNo)
            if result is True:
                await ctx.send('Success! ' + ctx.author.name + ' has been bound with team number ' + str(teamNo) + '.')
            else:
                await ctx.send('Error! Team number ' + str(teamNo) + ' has already been claimed by another user in this channel.')
        else:
            await ctx.send('Error! You have already registered to a team in this channel. If you want to change your registration, use `wb ff unregister`')

    @yahoo.command(name='unregister')
    async def unregister(self, ctx):
        """
        Remove the binding between your discord user ID and one of the team IDs in the league.
        """
        # Check for commanding user in the FantasyManagers mongodb doc
        existing_entry = await self.find_user(str(ctx.author.id))
        if (existing_entry is None):
            await ctx.send('You are not currently registered to a team in this channel. Use `wb ff teaminfo` to find your team\'s ID number and then `wb ff register [number]`')
        else:
            await existing_entry.delete()
            await ctx.send('Success! Binding for ' + ctx.author.name + ' has been removed.')

    @yahoo.command(name='teaminfo')
    async def teaminfo(self, ctx):
        """
        Retrieve Yahoo Fantasy teams and IDs.
        """
        print('Fetching fantasy league info...\n')

        query = YahooQuery('data/', self.config['league_id'])

        leagueInfo: League = self.controller.retrieve(
            'league_info', 
            query.get_league_info
        )

        leagueTeams = self.controller.retrieve(
            'league_teams', 
            query.get_league_teams
        )

        output = 'League info acquired for: ' + leagueInfo.name + '\n```'
        output += 'Id | Team Name              | Manager(s)\n'
        for i in leagueTeams:
            team: Team = i['team']
            id = str(team.team_id).rjust(2, ' ') + ' |'
            name = ' ' + str(team.name, 'UTF-8').ljust(int(self.config['max_team_name_length']), ' ') + ' |'
            managers = ' ' + team.managers['manager'].nickname

            output += id + name + managers + '\n'
        output += '```'

        msg = await ctx.send(output)

    @yahoo.command(name='standings')
    async def standings(self, ctx):
        """
        Display the current standings page for the fantasy league.
        """
        query = YahooQuery('data/', self.config['league_id'])
        standings: Standings = self.controller.retrieve(
            'league_standings', 
            query.get_league_standings
        )

        output = 'Current Standings:```Rank | ' + 'Team Name'.ljust(int(self.config['max_team_name_length']), ' ') + ' |  W-L-T    | Pts For | Pts Agnst | Streak | Waiver | Moves\n'
        for teamObj in standings.teams:
            team: Team = teamObj['team']
            rank = '   0 |' if team.team_standings.rank is None else (str(team.team_standings.rank) + ' |').rjust(6, ' ')
            name = ' ' + str(team.name, 'UTF-8').ljust(int(self.config['max_team_name_length']), ' ') + ' |'
            wlt = ' ' + str(team.wins).rjust(2, ' ') + ('-' + str(team.losses) + '-' + str(team.ties)).ljust(7, ' ') + ' |'
            ptsFor = ' ' + str(round(team.points_for, 2)).rjust(6, ' ').ljust(7, '0') + ' |'
            ptsAgnst = ' ' + str(round(team.points_against, 2)).rjust(8, ' ').ljust(9, '0') + ' |'
            streak = ' ' + (' ' if team.streak_type == '' else team.streak_type) + ' - ' + str(team.streak_length).rjust(2, ' ') + ' |'
            waiver = ' ' + ('0' if team.waiver_priority is None else str(team.waiver_priority)).rjust(6, ' ') + ' |'
            moves = ' ' + ('0' if team.number_of_moves is None else str(team.number_of_moves)).rjust(5, ' ')
            output += rank + name + wlt + ptsFor + ptsAgnst + streak + waiver + moves + '\n'

        await ctx.send(output + '```')

    # potentially include live IRL NFL scoreboard stuff with this, and extend that to the gameday routine.
    @yahoo.command(name='scoreboard')
    @enforce_user_registered()
    async def scoreboard(self, ctx, week: int = 0):
        """
        Display the current scoreboard for the fantasy league. Optional week parameter for retrospective/lookahead.
        """
        if (week > 16):
            await ctx.send('`Week` parameter is out of bounds. Try something less than 17.')
            return

        query = YahooQuery('data/', self.config['league_id'])
        league: League = self.controller.retrieve(
            'league_metadata', 
            query.get_league_metadata
        )

        if week == 0: week = int(league.current_week)
        output = 'Week ' + str(week) + ':```'

        scoreboard: Scoreboard = self.controller.retrieve(
            'league_scoreboard_week_' + str(week), 
            query.get_league_scoreboard_by_week, 
            {'chosen_week': str(week)}
        )

        for matchup in scoreboard.matchups:
            pass

        await ctx.send(output + '```')
        
    @yahoo.command(name='matchup')
    @enforce_user_registered()
    async def matchup(self, ctx, matchup: int = 0):
        """
        Display the current matchup for your fantasy team. Optional matchup ID parameter for viewing other matchups - requires getting the ID from the scoreboard output.
        """
        pass
        
    @yahoo.command(name='team')
    @enforce_user_registered()
    async def team(self, ctx, teamId: int = 0):
        """
        Display the current matchup for your fantasy team. Optional team ID parameter for viewing other matchups - requires getting the ID from the teaminfo output.
        """
        pass
        
    @yahoo.command(name='gameday')
    @enforce_user_registered()
    async def gameday(self, ctx):
        """
        Display and pin the league scoreboard with live updates (edits) every 30s until the day's games are over.
        """
        pass

def setup(bot):
    bot.add_cog(Yahoo(bot))
