from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

import psycopg2
import psycopg2.extensions

load_dotenv()

app = Flask(__name__)

DB_NAME = os.getenv("POSTGRES_DB", "docker-learn")

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "[password redacted]"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", 5432),
}


print(DB_CONFIG)


def create_database_if_not_exists():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{DB_NAME}"')

    cur.close()
    conn.close()


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_tables_if_not_exists():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )

    conn.commit()
    cur.close()
    conn.close()


@app.route("/", methods=["POST"])
def entry():
    payload = request.get_json(force=True)
    email = payload.get("email")

    if not email:
        return jsonify({"error": "email_required"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT id, email, created_at
            FROM users
            WHERE email = %s
            """,
            (email,),
        )

        user = cur.fetchone()

        if not user:
            cur.execute(
                """
                INSERT INTO users (email)
                VALUES (%s)
                RETURNING id, email, created_at
                """,
                (email,),
            )
            conn.commit()
            user = cur.fetchone()

            return (
                jsonify(
                    {
                        "status": "created",
                        "user": {
                            "id": user[0],
                            "email": user[1],
                            "created_at": user[2].isoformat(),
                        },
                    }
                ),
                201,
            )

        return (
            jsonify(
                {
                    "status": "exists",
                    "user": {
                        "id": user[0],
                        "email": user[1],
                        "created_at": user[2].isoformat(),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": "database_error", "details": str(e)}), 500

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    create_database_if_not_exists()
    create_tables_if_not_exists()
    app.run(debug=False)
