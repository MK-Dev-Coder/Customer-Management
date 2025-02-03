import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

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
        return jsonify({
            "error": "Database connection failed.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # The Flask app will run on http://0.0.0.0:5000 by default.
    app.run(host="0.0.0.0", port=5000)