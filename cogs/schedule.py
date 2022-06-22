import pytz
import datetime
import nextcord as discord
import requests
from bs4 import BeautifulSoup
from nextcord.ext import commands

from internal import clear, constants

class Schedule(commands.Cog):

    # store possible league aliases as keys and the corresponding espn URL name for that league as the value
    LEAGUE_ALIASES = {
        # college basketball
        'cbb': 'mens-college-basketball',
        'college basketball': 'mens-college-basketball',
        'college-basketball': 'mens-college-basketball',
        'college hoops': 'mens-college-basketball',
        'college-hoops': 'mens-college-basketball',
        'ncaam': 'mens-college-basketball',
        'ncaa m': 'mens-college-basketball',
        'ncaa-m': 'mens-college-basketball',
        'ncaabb': 'mens-college-basketball',
        'ncaa bb': 'mens-college-basketball',
        'ncaa-bb': 'mens-college-basketball',
        'ncaa basketball': 'mens-college-basketball',
        'ncaa-basketball': 'mens-college-basketball',
        'men\'s basketball': 'mens-college-basketball',
        'mens basketball': 'mens-college-basketball',
        'amateurism': 'mens-college-basketball',

        # nba
        'nba': 'nba',
        'national basketball association': 'nba',
        'association': 'nba',
        'the association': 'nba',
        'pro hoops': 'nba',
        'pro basketball': 'nba',
        'basketball': 'nba',

        # college football
        'cfb': 'college-football',
        'college football': 'college-football',
        'college-football': 'college-football',
        'collegiate football': 'college-football',
        'college fb': 'college-football',
        'college-fb': 'college-football',
        'collegiate fb': 'college-football',
        'ncaaf': 'college-football',
        'ncaafb': 'college-football',
        'ncaa fb': 'college-football',
        'ncaa football': 'college-football',
        'boy\'s league': 'college-football',
        'boys league': 'college-football',

        # nfl
        'nfl': 'nfl',
        'national football league': 'nfl',
        'the league': 'nfl',
        'men\'s league': 'nfl',
        'mens league': 'nfl',
        'tnf': 'nfl',
        'snf': 'nfl',
        'mnf': 'nfl',
        'redzone': 'nfl',
        'lombardi': 'nfl',
        'football': 'nfl',

        # nhl
        'nhl': 'nhl',
        'national hockey league': 'nhl',
        'hockey': 'nhl',
        'hockey league': 'nhl',
        'hockey-league': 'nhl',
        'the show': 'nhl',

        # mlb
        'mlb': 'mlb',

        # ncaaw
        'ncaaw': 'womens-college-basketball',
        'womens basketball': 'womens-college-basketball',
        'women\'s basketball': 'womens-college-basketball',
        
        # wnba
        'wnba': 'wnba',
        'womens nba': 'wnba',
        'women\'s nba': 'wnba',
        'lady hoops': 'wnba',

        # nba G league
        'g league': 'nba-g-league',
        'g-league': 'nba-g-league',
        'nba g-league': 'nba-g-league',
        'nba g league': 'nba-g-league',
        'nbag': 'nba-g-league',
        'nbagl': 'nba-g-league',
    }

    def __init__(self, bot):
        self.bot = bot

    def parseDataDate(self, olddate): # date comes in as yyyy-MM-ddThh:mmZ
        tz = pytz.timezone('America/New_York')
        time_string = olddate[11:16]
        time = datetime.datetime.strptime(time_string, '%H:%M').time()
        return str(datetime.datetime.now(pytz.utc).replace(hour=time.hour, minute=time.minute).astimezone(tz).strftime("%I:%M %p"))

    @commands.command()
    @commands.bot_has_permissions(add_reactions=True)
    async def schedule(self, ctx, *, league):
        """
        Scrapes espn for ongoing/upcoming sporting events. Add to the bot's ❌ reaction to have the message deleted (option timeout is 2min).
        """
        league = league.lower()
        try:
            league_name = self.LEAGUE_ALIASES[league]
        except (KeyError) as e:
            print('schedule.py 116: invalid league alias')
            await ctx.send(f'Beep boop. I do not recognize that league parameter. Try a more conventional name for `{league}`, or petition for it to be included.')
            return

        response = requests.get(f"https://www.espn.com/{league_name}/schedule")
        page = BeautifulSoup(response.content, 'html.parser')

        # append name of league as heading and begin multiline code block
        output = 'Here is the schedule for: ' + league_name + '\n'

        print('about to iterate over date objects on schedule page')

        # depending on the league, date subtables are denoted by id sched-container (nfl, cfb) OR class ScheduleTables (everything else)
        if league_name == 'nfl' or league_name == 'college-football' or league_name == 'wnba':
            subpage = page.find(id='sched-container')
            schedule_tables = subpage.find_all('table', class_='schedule')
            schedule_dates = subpage.find_all('h2')

            rows_count = 0
            for i in range(len(schedule_dates)):
                if rows_count > 20: break
                output += schedule_dates[i].text + '\n'

                # no games scheduled for this date if there is no table head
                if schedule_tables[i].find('thead') is None:
                    output += 'No games scheduled for this date\n\n'
                    continue

                # gather headings
                # only take 3 headings if the 4th one is not "nat tv", as finished games would instead have a leading scorer listed
                headings_count = 0
                headings_max = 4 if schedule_tables[i].find_all('th')[3].find('span').text == 'nat tv' else 3
                for heading in schedule_tables[i].find_all('th'):
                    if headings_count == headings_max: break
                    else: headings_count += 1
                    content = heading.find('span')
                    if content is None: output += '\t'
                    else: output += content.text.upper() + '\t'
                output += '\n'

                # populate matches
                tbody = schedule_tables[i].find('tbody')
                for row in tbody.find_all('tr'):
                    if rows_count > 20: break
                    else: rows_count += 1
                    cells = row.find_all('td')
                    headings_count = 0
                    for cell in cells: 
                        if headings_count == headings_max: break
                        else: headings_count += 1
                        if cell.find('span') is not None: 
                            output += cell.find('span').text + '\t'
                        else: 
                            try:
                                output += self.parseDataDate(cell['data-date']).lstrip('0') + '\t'
                            except (KeyError) as e: 
                                output += cell.text + '\t'
                    output += '\n'
                output += '\n'

        # from above: class ScheduleTables (everything else)
        else:
            schedule_dates = page.find_all(class_='ScheduleTables')

            rows_count = 0
            for section in schedule_dates:
                if rows_count > 20: break
                output += section.find(class_='Table__Title').text + '\n'

                # gather headings
                # only take 3 headings if the 4th one is not "TV", as finished games would instead have a leading scorer listed
                headings_count = 0
                headings_max = 4 if section.find_all('th')[2].text == 'TV' else 3
                for heading in section.find_all('th'):
                    if headings_count == headings_max: break
                    else: 
                        try:
                            headings_count += int(heading['colspan'])
                        except (ValueError, KeyError) as e:
                            headings_count += 1

                    output += heading.text.upper() + '\t'
                output += '\n'

                # populate matches
                tbody = section.find('tbody')
                for row in tbody.find_all('tr'):
                    if rows_count > 20: break
                    else: rows_count += 1

                    headings_count = 0
                    for cell in row.find_all('td'):
                        if headings_count == headings_max: break
                        else: headings_count += 1

                        # check all the spans and avoid the gameNote one
                        # text is too long and pushes discord character limit
                        if cell.find('span') is None or cell.find('p') is not None:
                            if cell.find('p') is None and cell.find('a') is not None: 
                                output += cell.find('a').text + '\t'
                            else: 
                                output += cell.text + '\t'
                        else: 
                            prev_text = ''
                            for span in cell.find_all('span'):
                                if prev_text == span.text: continue
                                else: prev_text = span.text

                                if 'gameNote' not in span['class'] and 'pr2' not in span['class']: 
                                    output += span.text + '\t'
                    output += '\n'
                output += '\n'

        msg = await ctx.send(output)
        
        cleared = await clear.author_clear(ctx, msg)

        if cleared == True:
            # await msg.edit(content=f'{constants.CLEAR_REACTION_EMOJI} Cleared long message')
            await msg.delete()
            
def setup(bot):
    bot.add_cog(Schedule(bot))
