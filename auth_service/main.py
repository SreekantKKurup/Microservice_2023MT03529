from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
from jose import JWTError, jwt
from datetime import datetime, timedelta

app = FastAPI()

# Database setup (creating users table if it doesn't exist)
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

# JWT settings
SECRET_KEY = "supersecretkey"  # Keep it secret, replace with something more secure in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Function to create a JWT token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Register route
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        return JSONResponse(content={"message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return JSONResponse(content={"message": "Username already exists"}, status_code=400)
    finally:
        conn.close()

# Login route with JWT Token generation
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('auth.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        # If user is found and credentials match, create JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user[1]}, expires_delta=access_token_expires  # user[1] is the username
        )
        return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

