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

def findBets(roster, hit_num=9, last_x_games=10):
    bets = []
    season = 20242025
    game_type = 2

    for dude in roster:

        player = dude['id']

        endpoint = f'/player/{player}/game-log/{season}/{game_type}'
        url = base_url + endpoint
        gamelog_df = requests.get(url).json()

        gameLog = gamelog_df['gameLog']
        if len(gameLog) < last_x_games:
            continue
        try:
            a = gameLog[0]['shots']
        except KeyError:
            continue

        minG = None
        minA = None
        minP = None
        minS = None

        goals = []
        assists = []
        points = []
        shots = []

        for i, game in enumerate(gameLog[:last_x_games]):
            goals.append(game['goals'])
            assists.append(game['assists'])
            points.append(game['goals'] + game['assists'])
            shots.append(game['shots'])

        goals = sorted(goals)
        assists = sorted(assists)
        points = sorted(points)
        shots = sorted(shots)

        minG = goals[last_x_games - hit_num]
        minA = assists[last_x_games - hit_num]
        minP = points[last_x_games - hit_num]
        minS = shots[last_x_games - hit_num]

        nameStr = 20

        if minG:
            bets.append(f'{dude["name"]:{nameStr}} ---   {minG} goal(s)    ---   {last_x_games - goals.index(minG)}/{last_x_games}')
        if minA:
            bets.append(f'{dude["name"]:{nameStr}} ---   {minA} assist(s)  ---   {last_x_games - assists.index(minA)}/{last_x_games}')
        if minP:
            bets.append(f'{dude["name"]:{nameStr}} ---   {minP} point(s)   ---   {last_x_games - points.index(minP)}/{last_x_games}')
        if minS:
            bets.append(f'{dude["name"]:{nameStr}} ---   {minS} shot(s)    ---   {last_x_games - shots.index(minS)}/{last_x_games}')
    return bets

def get_roster(game_data, roster_spots):
    for player in roster_spots:
        if player['teamId'] == game_data['awayTeamName']['Id']:
            game_data['awayRoster'][player['playerId']] = { # Headshots available
                "name": f"{player['firstName']['default']} {player['lastName']['default']}",
                "sweaterNumber": player['sweaterNumber'],
                "position": player['positionCode'],
                "playerId": player['playerId'],
            }
            playerInfo = []
            for info in ['name', 'sweaterNumber', 'position']:
                playerInfo.append(game_data['awayRoster'][player['playerId']][info])
            game_data['awayRoster'][player['playerId']]['combinedInfo'] = f"{playerInfo[2]} #{playerInfo[1]} {playerInfo[0]}"
        
        elif player['teamId'] == game_data['homeTeamName']['Id']:
            game_data['homeRoster'][player['playerId']] = { # Headshots available
                "name": f"{player['firstName']['default']} {player['lastName']['default']}",
                "sweaterNumber": player['sweaterNumber'],
                "position": player['positionCode'],
                "playerId": player['playerId'],
            }
            playerInfo = []
            for info in ['name', 'sweaterNumber', 'position']:
                playerInfo.append(game_data['homeRoster'][player['playerId']][info])
            game_data['homeRoster'][player['playerId']]['combinedInfo'] = f"{playerInfo[2]} #{playerInfo[1]} {playerInfo[0]}"
    return game_data


def get_live_game_data(game_info):
    live_game_endpoint = '/gamecenter/'
    play_by_play_endpoint = '/play-by-play'
    live_game_dict = requests.get(base_url + live_game_endpoint + str(game_info['gameId']) + play_by_play_endpoint).json()

    game_data = {
        "gameId": game_info['gameId'],
        "period": 0,
        "timeRemaining": '20:00',
        "isIntermission": True,

        "awayTeamName": game_info['awayTeamName'],
        "awayScore": live_game_dict['awayTeam']['score'],
        "awayShots": 0,
        "awayRoster": {},
        "awayOnIce": [],

        "homeTeamName": game_info['homeTeamName'],
        "homeScore": live_game_dict['homeTeam']['score'],
        "homeShots": 0,
        "homeRoster": {},
        "homeOnIce": [],
    }
    
    if not live_game_dict['gameState'] == 'FUT': # If game has started
        game_data["period"]= live_game_dict['displayPeriod']
        game_data["timeRemaining"]= live_game_dict['clock']['timeRemaining']
        game_data["isIntermission"]= live_game_dict['clock']['inIntermission']

        game_data["awayShots"]= live_game_dict['awayTeam']['sog']
        game_data["homeShots"]= live_game_dict['homeTeam']['sog']

    game_data = get_roster(game_data, live_game_dict['rosterSpots'])

    awayOnIce = []
    homeOnIce = []
    if not live_game_dict['gameState'] == 'FUT' and live_game_dict['summary']:
        awayOnIce = live_game_dict['summary']['iceSurface']['awayTeam']['forwards'] + live_game_dict['summary']['iceSurface']['awayTeam']['defensemen']
        homeOnIce = live_game_dict['summary']['iceSurface']['homeTeam']['forwards'] + live_game_dict['summary']['iceSurface']['homeTeam']['defensemen']

    onIce = []
    for player in awayOnIce:
        onIce.append(game_data['awayRoster'][player['playerId']]['combinedInfo'])
    game_data["awayOnIce"] = onIce

    onIce = []
    for player in homeOnIce:
        onIce.append(game_data['homeRoster'][player['playerId']]['combinedInfo'])
    game_data["homeOnIce"] = onIce

    # Get score, time remaining, period, etc.
    # can get score, shots, period, time remaining from play by play --> maybe who's on the ice!!
    # this is followed by a list of all players for both teams --> get player id's
    # play by play from first to last follows, including coords of event with center ice being 0,0 --> range: x: -100 to 100, y: -42 to 42 (in feet)
    # uses team and player id's

def get_live_stats(player, selected_game, isAway=True):

    live_game_endpoint = '/gamecenter/'
    boxscore_endpoint = '/boxscore'
    live_game_dict = requests.get(base_url + live_game_endpoint + str(selected_game['gameId']) + boxscore_endpoint).json()
    info = []
    if live_game_dict['gameState'] == 'FUT': # If game has not started
        return info
    
    if isAway:
        for pos in ['forwards', 'defense']:
            for away_player in live_game_dict['playerByGameStats']['awayTeam'][pos]:
                if player['playerId'] == away_player['playerId']:
                    info.append([away_player['name']['default']])
                    for stat in ['goals', 'assists', 'sog', 'faceoffWinningPctg']:
                        info[0].append(away_player[stat])
    
    else:
        for pos in ['forwards', 'defense']:
            for home_player in live_game_dict['playerByGameStats']['homeTeam'][pos]:
                if player['playerId'] == home_player['playerId']:
                    info.append([home_player['name']['default']])
                    for stat in ['goals', 'assists', 'sog', 'faceoffWinningPctg']:
                        info[0].append(home_player[stat])

    return info

# start_time = time()
# roster1 = get_team_roster('NJD')
# for player in roster1:
#     print(player)
# bets1 = findBets(roster1)
# print(bets1)
#
# roster2 = get_team_roster('NYR')
# bets2 = findBets(roster2)
# print(bets2)
#
#
# print("--- %s seconds ---" % (time() - start_time))
