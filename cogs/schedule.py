from pprint import pprint
from queue import Empty
import re
import nextcord as discord
import requests
from bs4 import BeautifulSoup
from nextcord.ext import commands


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

    @commands.command()
    async def schedule(self, ctx, *, league):
        """
        Scrapes espn for ongoing/upcoming sporting events.
        """
        league = league.lower()
        league_name = self.LEAGUE_ALIASES[league]
        if league_name is None:
            print('schedule.py 111: invalid league alias')
            await ctx.send('Beep boop. I do not recognize that league parameter. Try a more conventional name for the league, or petition for it to be included.')
            return

        # need to include a dictionary of different aliases for each prominent sports league, to ensure a user-friendly command


        response = requests.get(f"https://www.espn.com/{league_name}/schedule")
        page = BeautifulSoup(response.content, 'html.parser')
        # print(page.find(class_='Card').prettify())

        # append name of league as heading and begin multiline code block
        output = 'Here is the schedule for: ' + league_name + '\n'

        print('about to iterate over date objects on schedule page')

        # depending on the league, date subtables are denoted by id sched-container (nfl, cfb) OR class ScheduleTables (everything else)
        if league_name == 'nfl' or league_name == 'college-football':
            subpage = page.find(id='sched-container')
            print('1')
            schedule_tables = subpage.find_all('table', class_='schedule')
            print('2')
            schedule_dates = subpage.find_all('h2')
            print('3')

            rows_count = 0
            for i in range(len(schedule_dates)):
                if rows_count > 20: break
                output += schedule_dates[i].text + '\n'

                # gather headings
                headings_count = 0
                for heading in schedule_tables[i].find_all('th'):
                    if headings_count == 4: break
                    else: headings_count += 1
                    content = heading.find('span')
                    if content is None: output += '\t'
                    else: output += content.text + '\t'
                output += '\n'

                # populate matches
                tbody = schedule_tables[i].find('tbody')
                for row in tbody.find_all('tr'):
                    if rows_count > 20: break
                    else: rows_count += 1
                    cells = row.find_all('td')
                    headings_count = 0
                    for cell in cells: 
                        if headings_count == 4: break
                        else: headings_count += 1
                        if cell.find('span') is not None: output += cell.find('span').text + '\t'
                        else: 
                            if cell.find('a') is not None: output += cell.text + '\t'
                            else: output += '\t'
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
                headings_count = 0
                for heading in section.find_all('th'):
                    if headings_count == 3: break
                    else: headings_count += 1
                    print('4')
                    output += heading.text + '\t'
                output += '\n'

                # populate matches
                tbody = section.find('tbody')
                for row in tbody.find_all('tr'):
                    if rows_count > 20: break
                    else: rows_count += 1
                    print('5')

                    headings_count = 0
                    for cell in row.find_all('td'):
                        if headings_count == 4: break
                        else: headings_count += 1
                        print('6 ' + cell.text)

                        # check all the spans and avoid the gameNote one
                        # text is too long and pushes discord character limit
                        if cell.find('span') is None or cell.find('p') is not None:
                            if cell.find('p') is None and cell.find('a') is not None: 
                                output += cell.find('a').text + '\t'
                                print('put out: ' + cell.find('a').text)
                            else: output += cell.text + '\t'
                        else: 
                            for span in cell.find_all('span'):
                                if 'gameNote' in span['class'] or 'pr2' in span['class']: continue
                                else: output += span.text + '\t'
                    output += '\n'
                output += '\n'

        await ctx.send(output)
            
def setup(bot):
    bot.add_cog(Schedule(bot))
