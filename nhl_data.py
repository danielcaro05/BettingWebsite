import requests
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import pandas as pd
import json
import copy
import os
import urllib.parse as up
from time import time
from concurrent.futures import ThreadPoolExecutor, as_completed


base_url = 'https://api-web.nhle.com/v1'
today = datetime.today()
today = today.strftime("%Y-%m-%d")

def urlencode_wrapper(qstrobj):
    return (up.urlencode(qstrobj, quote_via=up.quote)
            .replace('%3D', '=')
            .replace('%3A', ':')
            .replace('%2C', ',')
            .replace('%5B%27', '')
            .replace('%27%5D', '')
    )
def generate_qstrobj(qstrobj, start, year, skater):#, teamID):
    qstrobj = copy.deepcopy(qstrobj)
    qstrobj['start'] = start
    qstrobj['cayenneExp'][0] = qstrobj['cayenneExp'][0].format(year=year, skater=skater)#, teamID=teamID)
    # qstrobj['cayenneExp'][0] = qstrobj['cayenneExp'][0].format(skater=skater)
    return urlencode_wrapper(qstrobj)


def short_2_long_name(short_name):
    switcher = {
        "ANA": "Anaheim Ducks",
        "ARI": "Arizona Coyotes",
        "BOS": "Boston Bruins",
        "BUF": "Buffalo Sabres",
        "CAR": "Carolina Hurricanes",
        "CBJ": "Columbus Blue Jackets",
        "CGY": "Calgary Flames",
        "CHI": "Chicago Blackhawks",
        "COL": "Colorado Avalanche",
        "DAL": "Dallas Stars",
        "DET": "Detroit Red Wings",
        "EDM": "Edmonton Oilers",
        "FLA": "Florida Panthers",
        "LAK": "Los Angeles Kings",
        "MIN": "Minnesota Wild",
        "MTL": "Montreal Canadiens",
        "NJD": "New Jersey Devils",
        "NSH": "Nashville Predators",
        "NYI": "New York Islanders",
        "NYR": "New York Rangers",
        "OTT": "Ottawa Senators",
        "PHI": "Philadelphia Flyers",
        "PIT": "Pittsburgh Penguins",
        "SEA": "Seattle Kraken",
        "SJS": "San Jose Sharks",
        "STL": "St. Louis Blues",
        "TBL": "Tampa Bay Lightning",
        "TOR": "Toronto Maple Leafs",
        "UTA": "Utah Hockey Club",
        "VAN": "Vancouver Canucks",
        "VGK": "Vegas Golden Knights",
        "WPG": "Winnipeg Jets",
        "WSH": "Washington Capitals"
    }
    return switcher.get(short_name, "Invalid team name")

def get_schedule():
    schedule_endpoint = '/schedule/'
    schedule_dict = requests.get(base_url + schedule_endpoint + today).json()



    games = []
    for game in schedule_dict['gameWeek'][0]["games"]:
        gameInfo = {
            "gameId": game['id'],
            "startTime": (datetime.strptime(game['startTimeUTC'][-9:-1], '%H:%M:%S') + timedelta(
                hours=int(game['easternUTCOffset'].split(":")[0]))).strftime('%I:%M %p'),
            "awayTeamName": {
                "short": game['awayTeam']['abbrev'],  # logo available
                "long": short_2_long_name(game['awayTeam']['abbrev']),
                "Id": game['awayTeam']['id'],
            },
            # "awayTeamScore": game['awayTeam']['score'],
            "homeTeamName": {
                "short": game['homeTeam']['abbrev'],  # logo available
                "long": short_2_long_name(game['homeTeam']['abbrev']),
                "Id": game['homeTeam']['id'],
            },
            # "homeTeamScore": game['homeTeam']['score'],
        }
        games.append(gameInfo)

    return games

def get_team_roster(teamAbb='TOR', season='20242025'):
    roster = []

    roster_endpoint = '/roster'
    team_endpoint = f'/{teamAbb}'
    season_endpoint = f'/{season}'
    url = base_url + roster_endpoint + team_endpoint + season_endpoint
    roster_df = requests.get(url).json()

    for row in roster_df:
        for player in roster_df[row]:
            name = player['firstName']['default'] + ' ' + player['lastName']['default']
            id = player['id']
            roster.append({'id': id, 'name': name})
    return roster

# def findBets(roster, hit_num=9, last_x_games=10):
#     bets = []
#     season = 20242025
#     game_type = 2
#
#     for dude in roster:
#
#         player = dude['id']
#
#         endpoint = f'/player/{player}/game-log/{season}/{game_type}'
#         url = base_url + endpoint
#         gamelog_df = requests.get(url).json()
#
#         gameLog = gamelog_df['gameLog']
#         if len(gameLog) < last_x_games:
#             continue
#         try:
#             a = gameLog[0]['shots']
#         except KeyError:
#             continue
#
#         minG = None
#         minA = None
#         minP = None
#         minS = None
#
#         goals = []
#         assists = []
#         points = []
#         shots = []
#
#         for i, game in enumerate(gameLog[:last_x_games]):
#             goals.append(game['goals'])
#             assists.append(game['assists'])
#             points.append(game['goals'] + game['assists'])
#             shots.append(game['shots'])
#
#         goals = sorted(goals)
#         assists = sorted(assists)
#         points = sorted(points)
#         shots = sorted(shots)
#
#         minG = goals[last_x_games - hit_num]
#         minA = assists[last_x_games - hit_num]
#         minP = points[last_x_games - hit_num]
#         minS = shots[last_x_games - hit_num]
#
#         nameStr = 20
#
#         if minG:
#             bets.append(f'{dude["name"]:{nameStr}} ---   {minG} goal(s)    ---   {last_x_games - goals.index(minG)}/{last_x_games}')
#         if minA:
#             bets.append(f'{dude["name"]:{nameStr}} ---   {minA} assist(s)  ---   {last_x_games - assists.index(minA)}/{last_x_games}')
#         if minP:
#             bets.append(f'{dude["name"]:{nameStr}} ---   {minP} point(s)   ---   {last_x_games - points.index(minP)}/{last_x_games}')
#         if minS:
#             bets.append(f'{dude["name"]:{nameStr}} ---   {minS} shot(s)    ---   {last_x_games - shots.index(minS)}/{last_x_games}')
#     return bets







def fetch_game_log(playerId, player_name, season, game_type):
    """Fetch game log data for a single player."""
    endpoint = f'/player/{playerId}/game-log/{season}/{game_type}'
    url = base_url + endpoint
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we handle HTTP errors
        return player_name, response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for player {player_name}: {e}")
        return player_name, None


def process_player_data(player_data, last_x_games, hit_num, nameStr=20):
    """Process game log data to find bets for a single player."""
    player_name, gamelog_data = player_data
    if gamelog_data is None:
        return []

    gameLog = gamelog_data.get('gameLog', [])
    if len(gameLog) < last_x_games:
        return []

    try:
        _ = gameLog[0]['shots']  # Check for key existence
    except KeyError:
        return []

    goals, assists, points, shots = [], [], [], []
    for game in gameLog[:last_x_games]:
        goals.append(game['goals'])
        assists.append(game['assists'])
        points.append(game['goals'] + game['assists'])
        shots.append(game['shots'])

    goals.sort()
    assists.sort()
    points.sort()
    shots.sort()

    minG = goals[last_x_games - hit_num] if hit_num <= len(goals) else None
    minA = assists[last_x_games - hit_num] if hit_num <= len(assists) else None
    minP = points[last_x_games - hit_num] if hit_num <= len(points) else None
    minS = shots[last_x_games - hit_num] if hit_num <= len(shots) else None

    bets = []
    if minG:
        bets.append(
            f'{player_name:{nameStr}} ---   {minG} goal(s)    ---   {last_x_games - goals.index(minG)}/{last_x_games}')
    if minA:
        bets.append(
            f'{player_name:{nameStr}} ---   {minA} assist(s)  ---   {last_x_games - assists.index(minA)}/{last_x_games}')
    if minP:
        bets.append(
            f'{player_name:{nameStr}} ---   {minP} point(s)   ---   {last_x_games - points.index(minP)}/{last_x_games}')
    if minS:
        bets.append(
            f'{player_name:{nameStr}} ---   {minS} shot(s)    ---   {last_x_games - shots.index(minS)}/{last_x_games}')

    return bets


def findBets(roster, hit_num=9, last_x_games=10, max_threads=16):
    bets = []
    season = 20242025
    game_type = 2

    with ThreadPoolExecutor(max_threads) as executor:
        futures = {
            executor.submit(fetch_game_log, dude['id'], dude['name'], season, game_type): dude['name']
            for dude in roster
        }

        for future in as_completed(futures):
            player_name = futures[future]
            try:
                player_data = future.result()
                bets.extend(process_player_data(player_data, last_x_games, hit_num))
            except Exception as e:
                print(f"Error processing data for player {player_name}: {e}")

    return bets

# start_time = time()
# roster1 = get_team_roster('NJD')
# bets1 = findBets(roster1)
# print(bets1)
#
# roster2 = get_team_roster('NYR')
# bets2 = findBets(roster2)
# print(bets2)
#
#
# print("--- %s seconds ---" % (time() - start_time))
