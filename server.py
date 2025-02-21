import logging
from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
import os
import psycopg2

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler())  # Log to console as well
CORS(app)  # This enables CORS for all routes

# Configuration for the Digital Ocean Managed Database.
DB_CONFIG = {
    "host": os.environ.get("DO_DB_HOST", "your-database-host"),
    "database": os.environ.get("DO_DB_NAME", "your-database-name"),
    "user": os.environ.get("DO_DB_USER", "your-database-user"),
    "password": os.environ.get("DO_DB_PASSWORD", "your-database-password"),
    "port": os.environ.get("DO_DB_PORT", "your-database-port")
}

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        return conn
    except Exception as e:
        app.logger.error(f"Failed to connect to database: {e}")
        raise

@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT NOW()")
        current_time = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jsonify({
            "message": "Successfully connected to Digital Ocean database.",
            "current_time": str(current_time)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/register", methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')  # Remember to hash passwords in production environments!
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cur.execute(sql, (username, email, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))  # Redirect to login page after successful signup
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        cur.execute(query, (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            # On successful login, redirect to dashboard.
            return redirect(url_for('dashboard'))
        else:
            return jsonify({"error": "Invalid credentials."}), 401
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/dashboard")
def dashboard():
    return "Welcome to your dashboard!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)