from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
import sqlite3
import jwt
import datetime
import os

app = FastAPI()

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")  # You should load this from env

# Create DB
conn = sqlite3.connect('auth.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')
conn.commit()
conn.close()

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return JSONResponse(content={"message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return JSONResponse(content={"message": "Username already exists"}, status_code=400)
    finally:
        conn.close()

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        payload = {
            "sub": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return JSONResponse(content={"message": "Login successful", "token": token})
    
    return JSONResponse(content={"message": "Invalid credentials"}, status_code=401)

