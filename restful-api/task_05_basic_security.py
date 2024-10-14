#!/usr/bin/python3
"""API Security and Authentication Techniques"""

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_jwt_extended import jwt_required, JWTManager

app = Flask(__name__)
app.config-["JWT_SECRET_KEY"] = "123"
jwt = JWTManager(app)
auth = HTTPBasicAuth()

users = {
    "user1": {"username": "user1",
              "password": generate_password_hash("hello"),
              "role": "user"},
    "admin1": {"username": "admin1",
               "password": generate_password_hash("bye"),
               "role": "admin"}
}

# Basic Authentication


@auth.verify_password
def verify_password(username, password):
    if (username in users and
            check_password_hash(users[username]['password'], password)):
        return username


@app.route('/basic-protected')
@auth.login_required
def basic_protected():
    return jsonify({"message": "Basic Auth: Access Granted"})


# JSON Web Token(JWT) Authentication


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if (username in users and
            check_password_hash(users[username]['password'], password)):
        access_token = create_access_token(
            identity={"username": username, "role": users[username]['role']})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Unauthorized username or password"}), 401


@app.route('/jwt-protected')
@jwt_required()
def jwt_protected():
    return jsonify({"message": "JWT Auth: Access Granted"})


@app.route('/admin-only')
@jwt_required
def admin_only():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    return "Admin Access: Granted"


@jwt.unauthorized_loader
def handle_unauthorized_error(err):
    return jsonify({"error": "Missing or invalid token"}), 401


@jwt.invalid_token_loader
def handle_invalid_token_error(err):
    return jsonify({"error": "Invalid token"}), 401


@jwt.expired_token_loader
def handle_expired_token_error(header, payload):
    return jsonify({"error": "Token has expired"}), 401


if __name__ == "__main__":
    app.run()
