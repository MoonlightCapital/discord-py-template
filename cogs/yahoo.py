from struct import unpack
from time import sleep
import nextcord as discord
import json
import datetime
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, wait
from nextcord.ext import commands
from internal import constants
from yfpy.data import Data
from yfpy.query import YahooFantasySportsQuery as YahooQuery
from yfpy.utils import unpack_data
from yfpy.models import League, Team, Standings, Scoreboard, Matchup, Player, PlayerStats

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
            type = str(ctx.channel.type)

            if ctx.guild is not None and (
                (str(ctx.guild.name) != 'Dedotated waam' and str(ctx.guild.name) != 'An-D\'s waambot dev') or 
                (type == 'text' and str(ctx.channel.name) != 's-p-o-r-t-s') or
                (type == 'public_thread' and ctx.channel.parent.name != 's-p-o-r-t-s')):
                
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

    @commands.group(aliases=['yahoo', 'fantasy'])
    @enforce_sports_channel()
    async def ff(self, ctx): pass

    @ff.command()
    @enforce_user_registered()
    async def test(self, ctx):
        """
        A test command, which can be used to test components.
        """
        print('Successful Yahoo FF test\n')
        msg = await ctx.send('Successful Yahoo FF test')
        pass
 
    @ff.command(name='register')
    async def register(self, ctx, teamNo: int):
        """
        Register a team in the league to yourself. This facilitates other commands such as `wb ff team` to show you your own team by default.
        """
        # Pull team ID info
        query = YahooQuery('data/', self.config['league_id'])
        leagueTeams = self.controller.retrieve(
            'league_teams', 
            query.get_league_teams
        )

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

    @ff.command(name='unregister')
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

    @ff.command(name='teaminfo')
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

    @ff.command(name='standings')
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
    @ff.command(name='scoreboard')
    @enforce_user_registered()
    async def scoreboard(self, ctx, week: int = 0):
        """
        Display the current scoreboard for the fantasy league. Optional week parameter for retrospective/lookahead.
        """
        if (week > 16):
            await ctx.send('`Week` parameter is out of bounds. Try something less than 17.')
            return

        await ctx.message.add_reaction(constants.AFFIRMATIVE_REACTION_EMOJI)
        exposition = await ctx.send('This will take several seconds: I need to make many API calls.')

        #query = YahooQuery('data/', self.config['league_id'])
        query = YahooQuery('data/', league_id='950358', game_id=406)
        league: League = self.controller.retrieve(
            'league_metadata', 
            query.get_league_metadata
        )

        if week == 0: week = int(league.current_week)
        scoreboard: Scoreboard = self.controller.retrieve(
            'league_scoreboard_week_' + str(week), 
            query.get_league_scoreboard_by_week, 
            {'chosen_week': week}
        )

        def do_matchup(count, messages, matchup: Matchup):
            output = '```Week ' + str(week) + ' Matchup ' + str(count + 1) + ':\n'

            team1: Team = matchup.teams[0]['team']
            team2: Team = matchup.teams[1]['team']
            manager1: str = ' (' + team1.managers['manager'].nickname + ')'
            manager2: str = ' (' + team2.managers['manager'].nickname + ')'
            output += '' + (str(team1.name, 'UTF-8') + manager1)[:30].rjust(30, ' ') + ' vs. ' + (str(team2.name, 'UTF-8') + manager2)[:30].ljust(30, ' ') + '\n'

            players1 = self.controller.retrieve(
                ('team_' + str(team1.team_id) + 'roster_player_stats_by_week_' + str(week)),
                query.get_team_roster_player_stats_by_week,
                {
                    'team_id': str(team1.team_id),
                    'chosen_week': week
                }
            )
            
            players2 = self.controller.retrieve(
                ('team_' + str(team2.team_id) + 'roster_player_stats_by_week_' + str(week)),
                query.get_team_roster_player_stats_by_week,
                {
                    'team_id': str(team2.team_id),
                    'chosen_week': week
                }
            )

            # Take out bench players to streamline the char count
            sortedPlayers1 = list(player for player in players1 if (player['player'].selected_position.position != 'BN' and player['player'].selected_position.position != 'IR'))
            sortedPlayers2 = list(player for player in players2 if (player['player'].selected_position.position != 'BN' and player['player'].selected_position.position != 'IR'))

            # Write out player scoring by position (bench omitted for brevity)
            smallerPlayerCount = len(sortedPlayers1) if len(sortedPlayers1) < len(sortedPlayers2) else len(sortedPlayers2)
            for i in range(smallerPlayerCount):
                player1: Player = sortedPlayers1[i]['player']
                player2: Player = sortedPlayers2[i]['player']
                name1 = ('' + player1.first_name[:1] + '. ' + player1.last_name) if player1.last_name is not None else player1.full_name
                name2 = ('' + player2.first_name[:1] + '. ' + player2.last_name) if player2.last_name is not None else player2.full_name
                points1 = '0.0' if player1.player_points.total is None else player1.player_points.total
                points2 = '0.0' if player2.player_points.total is None else player2.player_points.total
                position = 'FLX' if player1.selected_position.position == 'W/R/T' else player1.selected_position.position
                number1 = ('#' + str(player1.uniform_number).ljust(3, ' ')) if (player1.uniform_number is not False and player1.uniform_number is not None) else '     '
                number2 = (' #' + str(player2.uniform_number).ljust(3, ' ')) if (player2.uniform_number is not False and player2.uniform_number is not None) else '     '
                teamcode1 = player1.editorial_team_abbr.ljust(4, ' ')
                teamcode2 = player2.editorial_team_abbr.rjust(3, ' ')
                output += '' + teamcode1 + number1 + name1[:15].ljust(15, ' ') + str(points1).rjust(5, ' ') + ' '
                output += position.ljust(3, ' ') + ' ' + str(points2).ljust(5, ' ') + name2[:15].rjust(15, ' ') + number2 + teamcode2 + '\n'
            
            # Totals line /w total prediction
            output += '(Proj) Total ' + ('(' + str(team1.team_projected_points.total) + ') ' + str(team1.team_points.total)).rjust(17, ' ') + ' TOT '
            output += ('' + str(team2.team_points.total) + ' (' + str(team2.team_projected_points.total) + ')').ljust(17, ' ') + ' Total (Proj)'

            messages[count] = (output + '```')
            

        # Write each matchup in parallel to be sent in series later
        threads = [None] * 6
        messages = [None] * 6
        with ThreadPoolExecutor(max_workers=6) as executor:
            for index, matchupObj in enumerate(scoreboard.matchups): 
                print('starting thread ' + str(index))
                threads[index] = executor.submit(do_matchup, index, messages, matchupObj['matchup'])

            # Wait for threads to stop
            wait(threads)
        
        await ctx.message.remove_reaction(constants.AFFIRMATIVE_REACTION_EMOJI, exposition.author)

        msg: list(discord.Message) = []
        carryover = ''
        for index, text in enumerate(messages):
            if (index % 2 == 0): carryover = text
            else: msg.append(await ctx.send(carryover + text))
        
        await exposition.delete()
        
    @ff.command(name='matchup')
    @enforce_user_registered()
    async def matchup(self, ctx, matchup: int = 0):
        """
        Display the current matchup for your fantasy team. Optional matchup ID parameter for viewing other matchups - requires getting the ID from the scoreboard output.
        """
        # get commanding user's matchup if needed
        if matchup == 0:
            existing_entry = await self.find_user(str(ctx.author.id))
        
        prequery = str(datetime.datetime.now())
        query = YahooQuery('data/', league_id='950358', game_id=406)
        league: League = self.controller.retrieve(
            'league_metadata', 
            query.get_league_metadata
        )
        postquery1 = str(datetime.datetime.now())

        week = 3
        if week == 0: week = int(league.current_week)

        teammatchups = self.controller.retrieve(
            'team' + str(matchup) + '_matchups', 
            query.get_team_matchups, 
            {'team_id': 2}
        )
        print('Pre-Query: ' + prequery)
        print('Post-Query 1: ' + postquery1)
        print('Post-Query 2: ' + str(datetime.datetime.now()))
        await ctx.send('test')
        print('Post-Msg 1: ' + str(datetime.datetime.now()))
        await ctx.send('test')
        print('Post-Msg 2: ' + str(datetime.datetime.now()))
        await ctx.send('test')
        print('Post-Msg 3: ' + str(datetime.datetime.now()))
        await ctx.send('test')
        print('Post-Msg 4: ' + str(datetime.datetime.now()))
        await ctx.send('test')
        print('Post-Msg 5: ' + str(datetime.datetime.now()))
        await ctx.send('test')
        print('Post-Msg 6: ' + str(datetime.datetime.now()))
        # get_league_matchups_by_week
        # get_team_roster_by_week x2
        
    @ff.command(name='team')
    @enforce_user_registered()
    async def team(self, ctx, teamId: int = 0):
        """
        Display the current matchup for your fantasy team. Optional team ID parameter for viewing other matchups - requires getting the ID from the teaminfo output.
        """
        # get_team_roster_by_week
        pass
        
    @ff.command(name='gameday')
    @enforce_user_registered()
    async def gameday(self, ctx):
        """
        Display and pin the league scoreboard with live updates (edits) every 30s until the day's games are over.
        """
        pass

def setup(bot):
    bot.add_cog(Yahoo(bot))
