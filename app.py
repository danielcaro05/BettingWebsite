from flask import Flask, render_template, jsonify, request
from testy import get_schedule, get_team_roster, findBets
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    games = get_schedule()
    print(games)  # Debugging: Print games to ensure the data is retrieved correctly
    if not games:
        return "No games available or an error occurred."

    return render_template('Schedule/schedule.html', games=games)

@app.route('/roster/<team>')
def roster(team):
    try:
        roster = get_team_roster(team)
        return render_template('roster.html', roster=roster, team=team)
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/bets', methods=['GET', 'POST'])
def bets():
    total_bets = []
    selected_game = request.form.get('game')  # Retrieve the selected game
    try:
        team1 = selected_game[1:-1].split(', ')[0][1:-1]
        team2 = selected_game[1:-1].split(', ')[1][1:-1]
        game = request.form.get('game')
        hit_num = int(request.form.get('hit_num', 9))
        last_x_games = int(request.form.get('last_x_games', 10))

        roster1 = get_team_roster(team1)
        bets1 = findBets(roster1, hit_num, last_x_games)

        roster2 = get_team_roster(team2)
        bets2 = findBets(roster2, hit_num, last_x_games)

        total_bets = bets1 + bets2

        return render_template('bets.html', bets=total_bets, team=f'{team1} vs {team2}')
    except Exception as e:
        return f"An error occurred: {e}"

@app.route('/betting_form', methods=['GET', 'POST'])
def betting_form():
    games = get_schedule()
    return render_template('betting_form.html', games=games)

@app.route('/add_parlay', methods=['GET', 'POST'])
def add_parlay():
    selected_game = request.form.get('selectedGame')
    awayAbb = selected_game.split(',')[0]
    homeAbb = selected_game.split(',')[1]

    awayRoster = get_team_roster(awayAbb)
    homeRoster = get_team_roster(homeAbb)

    awayNames = []
    homeNames = []

    for player in awayRoster:
        awayNames.append(player['name'])

    for player in homeRoster:
        homeNames.append(player['name'])

    playerNames = awayNames + homeNames

    return render_template('AddParlay/add_parlay.html', game=selected_game, playerNames=playerNames)

@app.route('/view_parlays', methods=['GET', 'POST'])
def view_parlays():
    selected_game = {
        'gameId': '2024020433',
        'awayTeamName': {
                'short': 'TOR',
                'long': 'Toronto Maple Leafs',
                'Id': 10,
            },
        'homeTeamName': {
                'short': 'PIT',
                'long': 'Pittsburgh Penguins',
                'Id': 5,
            },
    }

    all_parlays = {
        'gid': {
            'game': selected_game,
            'parlays': []
        }
    }

    parlay1 = {
        'legs': [
            {'player': 'Crosby', 'bet': 'S', 'quantity': 2},
            {'player': 'Matthews', 'bet': 'G', 'quantity': 1},
        ],
        'amount': 10,
    }

    all_parlays['gid']['parlays'].append(parlay1)
    return render_template('ViewParlays/view_parlays.html', parlays=all_parlays)

@app.route('/to_view_parlays')
def to_view_parlays():
    games = get_schedule()
    return render_template('choose_game.html', games=games, form_action='/view_parlays')

@app.route('/to_add_parlay')
def to_add_parlay():
    games = get_schedule()
    return render_template('choose_game.html', games=games, form_action='/add_parlay')

@app.route('/save_parlay', methods=['POST'])
def save_parlay():
    data = request.get_json()  # Get the JSON data from the request
    try:
        # Save the data to parlays.json
        with open('parlays.json', 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({"message": "Parlay saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
