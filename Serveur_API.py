import json
from flask import Flask, request, jsonify, render_template_string
URLBASE="orga"
# API Serveur : Stocke les infos et gère les requêtes
server = Flask(__name__)
team_info = {
    "blue": {"name": "", "score": 0},
    "green": {"name": "", "score": 0},
    "timer": 0
}

matches = []
teams = []
pools = [[], [], [],[] ]

def load_data():
    global matches, teams, pools
    try:
        with open('matches.json', 'r') as f:
            matches = json.load(f)
    except FileNotFoundError:
        matches = []
    try:
        with open('teams.json', 'r') as f:
            teams = json.load(f)
    except FileNotFoundError:
        teams = []
    try:
        with open('pools.json', 'r') as f:
            pools = json.load(f)
    except FileNotFoundError:
        pools = [[], [], [],[]]

def save_data():
    with open('matches.json', 'w') as f:
        json.dump(matches, f)
    with open('teams.json', 'w') as f:
        json.dump(teams, f)
    with open('pools.json', 'w') as f:
        json.dump(pools, f)

def reset_data():
    global matches, teams, pools
    matches = []
    teams = []
    pools = [[], [], [],[]]
    save_data()

load_data()

# HTML template for index.html
index_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Match Info</title>
    <link rel="icon" type="image/png" href="/static/Ballon_tr2.png">
    <link rel="script" type="text/javascript" href="/static/js/script.js">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }
        h1, h2 {
            color: #333;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background: #fff;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 10px;
        }
        input[type="text"], input[type="datetime-local"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ccc;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .delete-button {
            background-color: #dc3545;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .delete-button:hover {
            background-color: #c82333;
        }
        .reset-button {
            background-color: #ffc107;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .reset-button:hover {
            background-color: #e0a800;
        }
        .start-button {
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .start-button:hover {
            background-color: #0056b3;
        }
        .end-button {
            background-color: #17a2b8;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .end-button:hover {
            background-color: #138496;
        }
    </style>

</head>
<body>
    <h1>Match Infos</h1>
    <h2>Matchs</h2>
    <table>
        <thead>
            <tr>
                <th>Poule 1</th>
                <th>Poule 2</th>
                <th>Poule 3</th>
                <th>Poule 4</th>
            </tr>
        </thead>
        <tbody>
            {% for i in range(max(len(pools[0]), len(pools[1]), len(pools[2]), len(pools[3]))) %}
            <tr>
                {% for j in range(4) %}
                <td>
                    {% if i < len(pools[j]) %}
                    {{ pools[j][i] }}
                    {% endif %}
                </td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <h2>Generated Matchs</h2>
    <table>
        <thead>
            <tr>
                <th>Match ID</th>
                <th>Poule</th>
                <th>Blue Team</th>
                <th>Green Team</th>
                <th>Blue Score</th>
                <th>Green Score</th>
                <th>Status</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for match in matches %}
            <tr>
                <td>{{ match.id }}</td>
                <td>{{ match.poule }}</td>
                <td>{{ match.blue_team }}</td>
                <td>{{ match.green_team }}</td>
                <td>{{ match.blue_score }}</td>
                <td>{{ match.green_score }}</td>
                <td>{{ match.status }}</td>
                <td>
                    {% if match.status == 'upcoming' %}
                    <button class="start-button" onclick="startMatch({{ match.id }})">Start Match</button>
                    {% elif match.status == 'ongoing' %}
                    <button class="end-button" onclick="endMatch({{ match.id }})">End Match</button>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <h2>Add Team</h2>
    <form id="add_team" action="/orga/add_team" method="post" onsubmit="submitForm(event, 'add_team')">
        <label for="team_name">Team Name:</label>
        <input type="text" id="team_name" name="team_name">
        <button type="submit">Add Team</button>
    </form>
    <h2>Generate Pools</h2>
    <form id="generate_pools" action="/orga/generate_pools" method="post" onsubmit="submitForm(event, 'generate_pools')">
        <button type="submit">Generate</button>
    </form>
    {% if pools[0] or pools[1] or pools[2] or pools[3] %}
    <h2>Generate Matches</h2>
    <form id="generate_matches" action="/orga/generate_matches" method="post" onsubmit="submitForm(event, 'generate_matches')">
        <button type="submit">Generate Matches</button>
    </form>
    {% endif %}
    <h2>Team Standings</h2>
    <table>
        <thead>
            <tr>
                <th>Team</th>
                <th>Wins</th>
                <th>Losses</th>
            </tr>
        </thead>
        <tbody>
            {% for team, record in standings.items() %}
                <tr>
                    <td>{{ team }}</td>
                    <td>{{ record.wins }}</td>
                    <td>{{ record.losses }}</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
    <h2>Teams</h2>
    <ul>
        {% for team in teams %}
            <li>{{ team }} <button class="delete-button" onclick="deleteTeam('{{ team }}')">Delete</button></li>
        {% endfor %}
    </ul>
    <button class="reset-button" onclick="resetData()">Reset Data</button>
</body>
</html>
"""

def calculate_standings():
    standings = {}
    for match in matches:
        if match["status"] == "completed":
            blue_team = match["blue_team"]
            green_team = match["green_team"]
            if blue_team not in standings:
                standings[blue_team] = {"wins": 0, "losses": 0}
            if green_team not in standings:
                standings[green_team] = {"wins": 0, "losses": 0}
            if match["blue_score"] > match["green_score"]:
                standings[blue_team]["wins"] += 1
                standings[green_team]["losses"] += 1
            else:
                standings[blue_team]["losses"] += 1
                standings[green_team]["wins"] += 1
    return standings

@server.route("/")
def index():
    standings = calculate_standings()
    return render_template_string(index_html, team_info=team_info, matches=matches, standings=standings, teams=teams, pools=pools, len=len, max=max)

def distribute_teams_into_pools(teams):
    import random
    random.shuffle(teams)
    num_pools = min(4, max(2, len(teams) // 3))  # Create up to 4 pools of 3 teams each, at least 1 pool
    for i in range(num_pools):
        pools[i] = teams[i::num_pools]

@server.route(f"/{URLBASE}/generate_pools", methods=["POST"])
def generate_pools():
    try:
        if len(teams) < 2:
            return jsonify({"message": "At least 2 teams are required to generate pools"}), 400
        for pool in pools:
            pool.clear()  # Clear existing pools before creating new ones
        distribute_teams_into_pools(teams)
        save_data()
        return jsonify({"message": "Pools generated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error generating pools"}), 500

def generate_matches_for_pools():
    match_id = 1
    for pool_index, pool in enumerate(pools):
        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                matches.append({
                    "id": match_id,
                    "poule": pool_index + 1,
                    "blue_team": pool[i],
                    "green_team": pool[j],
                    "blue_score": 0,
                    "green_score": 0,
                    "status": "upcoming"
                })
                match_id += 1

@server.route("/{URLBASE}/generate_matches", methods=["POST"])
def generate_matches():
    try:
        matches.clear()  # Clear existing matches before creating new ones
        generate_matches_for_pools()
        save_data()
        return jsonify({"message": "Matches generated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error generating matches"}), 500

@server.route("/{URLBASE}/add_team", methods=["POST"])
def add_team():
    try:
        team_name = request.form.get("team_name")
        if team_name:
            teams.append(team_name)
            save_data()
            return jsonify({"message": "Team added successfully"}), 200
        else:
            return jsonify({"message": "Invalid team name"}), 400
    except Exception as e:
        return jsonify({"message": "Error adding team"}), 500

@server.route("/{URLBASE}/delete_team", methods=["POST"])
def delete_team():
    try:
        data = request.get_json()
        team_name = data.get("team_name")
        if team_name in teams:
            teams.remove(team_name)
            save_data()
            return jsonify({"message": "Team deleted successfully"}), 200
        else:
            return jsonify({"message": "Team not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error deleting team"}), 500

@server.route("/{URLBASE}/reset_data", methods=["POST"])
def reset_data_route():
    try:
        reset_data()
        return jsonify({"message": "Data reset successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error resetting data"}), 500

@server.route("/{URLBASE}/update_score", methods=["POST"])
def update_score():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["blue_score"] = data.get("blue_score", match["blue_score"])
            match["blue_team"] = data.get("blue_name", match["blue_team"])
            match["green_score"] = data.get("green_score", match["green_score"])
            match["green_team"] = data.get("green_name", match["green_team"])
            match["timer"] = data.get("timer", match.get("timer", 0))
            save_data()
            return jsonify({"message": "Scores, names, and timer updated"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error updating scores, names, and timer"}), 500

@server.route("/{URLBASE}/set_team_name", methods=["POST"])
def set_team_name():
    global team_info
    try:
        data = request.form
        team_info["blue"]["name"] = data.get("blue_name", team_info["blue"]["name"])
        team_info["green"]["name"] = data.get("green_name", team_info["green"]["name"])
        save_data()
        return jsonify({"message": "Team names updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error updating team names"}), 500

@server.route("/{URLBASE}/get_team_info", methods=["GET"])
def get_team_info():
    match_id = request.args.get("match_id")
    try:
        if match_id == "Select Match":
            return jsonify({"message": "Invalid match ID"}), 400
        match_id = int(match_id)
        match = next((m for m in matches if m["id"] == match_id), None)
        if match:
            return jsonify({
                "blue": {"name": match["blue_team"], "score": match["blue_score"]},
                "green": {"name": match["green_team"], "score": match["green_score"]},
                "timer": match.get("timer", 0)
            }), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error fetching team info"}), 500

@server.route("/{URLBASE}/get_matches", methods=["GET"])
def get_matches():
    try:
        return jsonify(matches), 200
    except Exception as e:
        return jsonify({"message": "Error fetching matches"}), 500

@server.route("/{URLBASE}/add_update_match", methods=["POST"])
def add_update_match():
    global matches
    try:
        data = request.form
        match_id = data.get("match_id")
        blue_team = data.get("blue_team")
        green_team = data.get("green_team")
        match_time = data.get("match_time")
        
        if match_id:
            match_id = int(match_id)
            for match in matches:
                if match["id"] == match_id:
                    match["blue_team"] = blue_team
                    match["green_team"] = green_team
                    match["match_time"] = match_time
                    match["status"] = "upcoming"
                    break
            else:
                matches.append({"id": match_id, "blue_team": blue_team, "green_team": green_team, "blue_score": 0, "green_score": 0, "status": "upcoming", "match_time": match_time})
        else:
            new_id = max(match["id"] for match in matches) + 1 if matches else 1
            matches.append({"id": new_id, "blue_team": blue_team, "green_team": green_team, "blue_score": 0, "green_score": 0, "status": "upcoming", "match_time": match_time})
        
        save_data()
        return jsonify({"message": "Match added/updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": "Error adding/updating match"}), 500

@server.route("/{URLBASE}/orga/start_match", methods=["POST"])
def start_match():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["status"] = "ongoing"
            save_data()
            return jsonify({"message": "Match started successfully"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error starting match"}), 500

@server.route("/{URLBASE}/end_match", methods=["POST"])
def end_match():
    global matches
    try:
        data = request.get_json()
        match_id = data.get("match_id")
        match = next((m for m in matches if m["id"] == int(match_id)), None)
        if match:
            match["status"] = "completed"
            match["blue_score"] = team_info["blue"]["score"]
            match["green_score"] = team_info["green"]["score"]
            match["timer"] = team_info["timer"]
            save_data()
            return jsonify({"message": "Match ended successfully"}), 200
        else:
            return jsonify({"message": "Match not found"}), 404
    except Exception as e:
        return jsonify({"message": "Error ending match"}), 500
from werkzeug.middleware.dispatcher import DispatcherMiddleware



app_with_prefix = DispatcherMiddleware(Flask('dummy_app'), {
    '/{URLBASE}': server
})
if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple("127.0.0.1", 5000, app_with_prefix)
    #server.run(host='0.0.0.0', port=5000, debug=True)
