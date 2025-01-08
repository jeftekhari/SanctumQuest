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

# Solana RPC client (optional if you need on-chain validation)
solana_client = Client("https://api.mainnet-beta.solana.com")

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