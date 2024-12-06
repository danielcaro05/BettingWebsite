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
from nhl_data import short_2_long_name, get_schedule, get_team_roster, findBets


data = {}
season = 20242025
game_type = 2
base_url = 'https://api-web.nhle.com/v1'

today = datetime.today()
today = today.strftime("%Y-%m-%d")

schedule = get_schedule()
data['schedule'] = schedule


rosters = {}
for game in schedule:
    rosters[game['homeTeamName']['short']] = get_team_roster(game['homeTeamName']['short'])
    rosters[game['awayTeamName']['short']] = get_team_roster(game['awayTeamName']['short'])

for key in rosters:
    for dude in rosters[key]:
        player = dude['id']
        endpoint = f'/player/{player}/game-log/{season}/{game_type}'
        url = base_url + endpoint
        dude['gameLog'] = requests.get(url).json()['gameLog']

data['rosters'] = rosters

with open('data.json', 'w') as f:
    json.dump(data, f)


# What other key works can you use other than fixme and todo that come up in yellow
# The answer is: fixme, todo, bug, note, and xxx
# NOTE:





#
# base_url = 'https://api-web.nhle.com/v1'

#
# # TODO: Store the schedule into a json file

#
#

#
# # Store rosters in data.json
# data['rosters'] = rosters
#
# # Store data in data.json

