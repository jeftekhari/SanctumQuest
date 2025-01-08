from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__, static_folder='static')

@app.route("/")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/update-leaderboard")
def update_leaderboard():
    # Read data from mock_data.json
    with open("data/mock_data.json", "r") as file:
        leaderboard_data = json.load(file)
    return render_template("leaderboard_rows.html", data=leaderboard_data)

@app.route("/search")
def search_leaderboard():
    query = request.args.get("name", "").strip().lower()
    
    # Read data from mock_data.json
    with open("data/mock_data.json", "r") as file:
        leaderboard_data = json.load(file)
    
    # Filter data by name
    if query:
        print("query" + query)
        filtered_data = [entry for entry in leaderboard_data if query in entry["name"].lower()]
    else:
        print("no query")
        filtered_data = leaderboard_data
    
    return render_template("leaderboard_rows.html", data=filtered_data)

@app.route("/user-details/<int:rank>")
def user_details(rank):
    # Load data from the mock_data.json file
    with open("data/mock_data.json", "r") as file:
        leaderboard_data = json.load(file)

    # Find the user by rank
    user = next((entry for entry in leaderboard_data if entry["rank"] == rank), None)

    # If user not found, return an empty response
    if not user:
        return ""

    # Render the user's pet details
    return render_template("user_details.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)