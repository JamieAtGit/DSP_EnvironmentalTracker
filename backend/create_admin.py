#!/usr/bin/env python3
"""
Secure admin user creation script for Carbon Footprint Tracking System.
This script should only be run once during initial setup.
"""
import json
import os
import getpass
import secrets
from werkzeug.security import generate_password_hash

USERS_FILE = os.path.join("backend", "api", "routes", "users.json")

def create_initial_admin():
    """Create the first admin user securely."""
    
    print("🔐 Carbon Footprint Tracker - Initial Admin Setup")
    print("=" * 50)
    
    # Check if admin already exists
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
            
            admin_exists = any(user.get("role") == "admin" for user in users)
            if admin_exists:
                print("⚠️  Admin user already exists!")
                response = input("Do you want to create another admin? (y/N): ")
                if response.lower() != 'y':
                    print("Exiting...")
                    return
        except json.JSONDecodeError:
            print("⚠️  Users file exists but is corrupted. Creating fresh file.")
            users = []
    else:
        users = []
        print("📝 Creating new users database...")
    
    # Get admin credentials
    print("\n📋 Enter admin user details:")
    while True:
        username = input("Admin username: ").strip()
        if len(username) >= 3 and username.isalnum():
            break
        print("❌ Username must be at least 3 characters and alphanumeric only.")
    
    while True:
        password = getpass.getpass("Admin password: ")
        if len(password) >= 8:
            password_confirm = getpass.getpass("Confirm password: ")
            if password == password_confirm:
                break
            else:
                print("❌ Passwords don't match. Try again.")
        else:
            print("❌ Password must be at least 8 characters long.")
    
    # Create admin user
    hashed_password = generate_password_hash(password)
    admin_user = {
        "username": username,
        "password": hashed_password,
        "role": "admin",
        "created_at": "initial_setup",
        "created_by": "setup_script",
        "is_active": True,
        "setup_admin": True  # Mark as setup admin
    }
    
    users.append(admin_user)
    
    # Create users directory if it doesn't exist
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    
    # Save users
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)
    
    print(f"\n✅ Admin user '{username}' created successfully!")
    print("\n🔐 Security Recommendations:")
    print("1. Store this password in a secure password manager")
    print("2. Enable two-factor authentication if available")
    print("3. Change the default secret key in production")
    print("4. Use HTTPS in production")
    print("5. Regularly review user accounts")
    
    # Generate a secure secret key suggestion
    secret_key = secrets.token_urlsafe(32)
    print(f"\n🔑 Suggested SECRET_KEY for production:")
    print(f"export SECRET_KEY='{secret_key}'")
    
    print("\n🚀 You can now start the application and login with these credentials.")

if __name__ == "__main__":
    try:
        create_initial_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        exit(1)