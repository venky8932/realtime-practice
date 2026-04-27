import os
import time
import threading
import requests
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "appdb"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "password"),
}
NODEJS_URL = os.getenv("NODEJS_URL", "http://nodejs-service:3000")
CHECK_INTERVAL_SECONDS = 300

class UserCreate(BaseModel):
    name: str
    email: str


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()


def health_check_scheduler():
    # Every 5 minutes, check the local /health endpoint.
    # If the internal health check fails, exit so Kubernetes can restart the pod.
    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=10)
            if response.status_code != 200:
                raise RuntimeError(f"health check returned {response.status_code}")
            print("[fastapi] self health check passed")
        except Exception as exc:
            print("[fastapi] self health check failed:", exc)
            os._exit(1)


@app.on_event("startup")
def startup_event():
    init_db()
    thread = threading.Thread(target=health_check_scheduler, daemon=True)
    thread.start()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users")
def create_user(user: UserCreate):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;",
                    (user.name, user.email),
                )
                user_id = cursor.fetchone()[0]
                conn.commit()
                return {"id": user_id, "name": user.name, "email": user.email}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/users")
def list_users():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name, email, created_at FROM users ORDER BY id DESC;")
                rows = cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "created_at": row[3].isoformat(),
                    }
                    for row in rows
                ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/node-health")
def node_health():
    try:
        response = requests.get(f"{NODEJS_URL}/health", timeout=10)
        return {
            "node_status": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
            "status_code": response.status_code,
        }
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
