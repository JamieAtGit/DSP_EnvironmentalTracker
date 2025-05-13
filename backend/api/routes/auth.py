# auth.py (Flask authentication logic)
import json
import os
from flask import request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = os.path.join("backend", "api", "routes", "users.json")

def load_users():
    if not os.path.exists(USERS_FILE):
        print("⚠️ users.json does not exist.")
        return []
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
        print(f"✅ Loaded {len(users)} users from {USERS_FILE}")
        return users  # ✅ return the already loaded data

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register_routes(app):

    @app.route("/signup", methods=["POST"])
    def signup():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400

        users = load_users()
        if any(u["username"] == username for u in users):
            return jsonify({"error": "User already exists"}), 400

        hashed_pw = generate_password_hash(password)
        new_user = {"username": username, "password": hashed_pw, "role": "user"}
        if username == "admin":
            new_user["role"] = "admin"

        users.append(new_user)
        save_users(users)
        return jsonify({"message": "✅ User registered"}), 200

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        users = load_users()
        user = next((u for u in users if u["username"] == username), None)
        if not user or not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        session["user"] = {"username": user["username"], "role": user["role"]}
        return jsonify({"message": "✅ Logged in", "user": session["user"]}), 200

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("user", None)
        return jsonify({"message": "Logged out"})

    @app.route("/me", methods=["GET"])
    def me():
        user = session.get("user")
        if not user:
            return jsonify({"error": "Not logged in"}), 401
        return jsonify(user)
