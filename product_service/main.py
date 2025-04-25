from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

# Initialize Products
conn = sqlite3.connect('products.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
''')

# Insert products if not exist
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    products = [
        ('Laptop', 999.99), ('Smartphone', 499.99), ('Headphones', 199.99),
        ('Monitor', 299.99), ('Keyboard', 89.99), ('Mouse', 49.99),
        ('Webcam', 79.99), ('Speaker', 149.99), ('Printer', 179.99),
        ('Router', 129.99), ('Tablet', 399.99), ('Smartwatch', 299.99),
        ('Charger', 29.99), ('SSD', 129.99), ('GPU', 499.99),
        ('RAM', 89.99), ('CPU', 349.99), ('Motherboard', 249.99),
        ('Power Supply', 119.99), ('PC Case', 99.99)
    ]
    cursor.executemany("INSERT INTO products (name, price) VALUES (?,?)", products)
conn.commit()
conn.close()

@app.get("/products")
async def get_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return JSONResponse(content={"products": [{"id": p[0], "name": p[1], "price": p[2]} for p in products]})
