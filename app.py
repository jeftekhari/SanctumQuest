from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from solders.pubkey import Pubkey 
from solana.rpc.api import Client
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import os
import json

app = Flask(__name__, static_folder='static')
CORS(app)

MOCK_DATA_FILE = "data/mock_data.json"

# Solana RPC client (optional if you need on-chain validation)
solana_client = Client("https://api.mainnet-beta.solana.com")

def read_mock_data():
    if not os.path.exists(MOCK_DATA_FILE):
        return []
    with open(MOCK_DATA_FILE, "r") as file:
        return json.load(file)

def write_mock_data(data):
    with open(MOCK_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

@app.route('/add-record', methods=['POST'])
def add_record():
    data = request.json
    wallet_address = data.get("wallet_address")

    if not wallet_address:
        return jsonify({"success": False, "error": "Missing wallet address"}), 400

    mock_data = read_mock_data()

    # Check if wallet_address already exists
    if any(record.get("wallet_address") == wallet_address for record in mock_data):
        return jsonify({"success": False, "message": "Wallet address already exists"}), 200

    # Create a new record
    new_record = {
        "rank": len(mock_data) + 1,
        "name": f"Player{len(mock_data) + 1}",
        "score": 0,
        "pets": [],
        "wallet_address": wallet_address
    }
    mock_data.append(new_record)
    write_mock_data(mock_data)

    return jsonify({"success": True, "message": "Record added successfully"}), 201

# Endpoint to generate a message for signing
@app.route('/generate-message', methods=['GET'])
def generate_message():
    # Generate a unique message (e.g., using a nonce or timestamp)
    message = f"Sign this message to authenticate. Timestamp: {os.urandom(16).hex()}"
    return jsonify({"message": message})

# Endpoint to verify the signed message
@app.route('/verify-signature', methods=['POST'])
def verify_signature():
    data = request.json
    wallet_address = data.get('wallet_address')
    signature = data.get('signature')
    message = data.get('message')

    if not wallet_address or not signature or not message:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        # Decode the public key and signature
        public_key = Pubkey.from_string(wallet_address)
        verify_key = VerifyKey(bytes(public_key))

        # Verify the signature
        verify_key.verify(message.encode(), bytes(signature["data"]))
        return jsonify({"success": True, "message": "Signature verified!"})
    except BadSignatureError:
        return jsonify({"success": False, "error": "Invalid signature"}), 400

# Endpoint to verify the signed message
@app.route('/update-record', methods=['POST'])
def update_record():
    data = request.json
    wallet_address = data.get("wallet_address")
    new_name = data.get("name")

    if not wallet_address or not new_name:
        return jsonify({"success": False, "error": "Missing wallet address or name"}), 400

    mock_data = read_mock_data()

    # Find the record by wallet address
    for record in mock_data:
        if record.get("wallet_address") == wallet_address:
            record["name"] = new_name
            write_mock_data(mock_data)
            return jsonify({"success": True, "message": "Record updated successfully"}), 200

    return jsonify({"success": False, "error": "Wallet address not found"}), 404

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

@app.route('/get-user-details', methods=['POST'])
def get_user_details():
    data = request.json
    wallet_address = data.get("wallet_address")

    if not wallet_address:
        return jsonify({"success": False, "error": "Missing wallet address"}), 400

    mock_data = read_mock_data()

    # Find the user by wallet address
    for record in mock_data:
        if record.get("wallet_address") == wallet_address:
            return jsonify({"success": True, "user": record}), 200

    return jsonify({"success": False, "error": "Wallet address not found"}), 404

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