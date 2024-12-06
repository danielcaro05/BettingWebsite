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


def get_team_roster(team_abb):
    # Get roster data from data.json
    with open('data.json', 'r') as f:
        return(json.load(f)['rosters'][team_abb])

def get_schedule():
    # Get schedule data from data.json
    with open('data.json', 'r') as f:
        return(json.load(f)['schedule'])

def findBets(roster, hit_num=9, last_x_games=10):
    bets = []

    for dude in roster:

        gameLog = dude['gameLog']

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
