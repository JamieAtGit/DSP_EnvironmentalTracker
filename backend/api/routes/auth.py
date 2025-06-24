# auth.py (Flask authentication logic)
import json
import os
from flask import request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.security import validate_input, AUTH_SCHEMA, log_security_event, rate_limit

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
    @rate_limit(requests_per_minute=5, requests_per_hour=20)  # Prevent abuse
    @validate_input(AUTH_SCHEMA)
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
        
        # SECURITY FIX: Remove automatic admin role assignment
        # Admin users must be manually created by existing admins
        new_user = {
            "username": username, 
            "password": hashed_pw, 
            "role": "user",
            "created_at": json.dumps({"timestamp": "now"}),  # Add timestamp for auditing
            "is_active": True
        }

        users.append(new_user)
        save_users(users)
        return jsonify({"message": "✅ User registered"}), 200

    @app.route("/login", methods=["POST"])
    @rate_limit(requests_per_minute=10, requests_per_hour=50)  # Prevent brute force
    @validate_input(AUTH_SCHEMA)
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        users = load_users()
        user = next((u for u in users if u["username"] == username), None)
        
        if not user or not check_password_hash(user["password"], password):
            log_security_event("FAILED_LOGIN", f"Username: {username}", "WARNING")
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Check if user account is active
        if not user.get("is_active", True):
            log_security_event("DISABLED_ACCOUNT_LOGIN", f"Username: {username}", "WARNING")
            return jsonify({"error": "Account disabled"}), 401

        # Successful login
        session["user"] = {
            "username": user["username"], 
            "role": user["role"],
            "login_time": json.dumps({"timestamp": "now"})
        }
        
        log_security_event("SUCCESSFUL_LOGIN", f"Username: {username}", "INFO")
        return jsonify({"message": "✅ Logged in", "user": {
            "username": user["username"], 
            "role": user["role"]
        }}), 200

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
    
    @app.route("/admin/create_admin", methods=["POST"])
    @rate_limit(requests_per_minute=2, requests_per_hour=5)  # Very strict for admin creation
    def create_admin():
        """Secure endpoint for creating admin users - requires existing admin."""
        current_user = session.get("user")
        if not current_user or current_user.get("role") != "admin":
            log_security_event("UNAUTHORIZED_ADMIN_CREATION", f"User: {current_user}", "CRITICAL")
            return jsonify({"error": "Admin privileges required"}), 403
        
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        users = load_users()
        if any(u["username"] == username for u in users):
            return jsonify({"error": "User already exists"}), 400
        
        hashed_pw = generate_password_hash(password)
        new_admin = {
            "username": username,
            "password": hashed_pw,
            "role": "admin",
            "created_at": json.dumps({"timestamp": "now"}),
            "created_by": current_user.get("username"),
            "is_active": True
        }
        
        users.append(new_admin)
        save_users(users)
        
        log_security_event("ADMIN_USER_CREATED", f"New admin: {username}, Created by: {current_user.get('username')}", "INFO")
        return jsonify({"message": f"✅ Admin user '{username}' created successfully"}), 200
