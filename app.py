from flask import Flask, render_template, jsonify, request
from nhl_data import get_schedule, get_team_roster, findBets

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

    return render_template('schedule.html', games=games)

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

if __name__ == "__main__":
    app.run(debug=True)
