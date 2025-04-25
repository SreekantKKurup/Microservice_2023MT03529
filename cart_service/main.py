from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

# Create DB
conn = sqlite3.connect('cart.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    product_id INTEGER NOT NULL
)
''')
conn.commit()
conn.close()

@app.post("/add_to_cart")
async def add_to_cart(username: str = Form(...), product_id: int = Form(...)):
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cart (username, product_id) VALUES (?,?)", (username, product_id))
    conn.commit()
    conn.close()
    return JSONResponse(content={"message": "Product added to cart"})

@app.post("/clear_cart")
async def clear_cart(username: str = Form(...)):
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return JSONResponse(content={"message": "Cart cleared"})

@app.get("/view_cart")
async def view_cart(username: str):
    conn = sqlite3.connect('cart.db')
    cursor = conn.cursor()
    cursor.execute("SELECT product_id FROM cart WHERE username=?", (username,))
    products = cursor.fetchall()
    conn.close()
    return JSONResponse(content={"cart": [p[0] for p in products]})
