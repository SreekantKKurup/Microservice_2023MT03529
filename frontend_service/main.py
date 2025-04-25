from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SESSION = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/")
async def login_from_home(request: Request, username: str = Form(...), password: str = Form(...)):
    res = requests.post("http://localhost:8001/login", data={"username": username, "password": password})
    if res.status_code == 200:
        SESSION["user"] = username
        return RedirectResponse("/products", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": res.json()["message"]})


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    res = requests.post("http://localhost:8001/login", data={"username": username, "password": password})
    if res.status_code == 200:
        SESSION["user"] = username
        return RedirectResponse("/products", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": res.json()["message"]})


@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(request: Request, username: str = Form(...), password: str = Form(...)):
    res = requests.post("http://localhost:8001/register", data={"username": username, "password": password})
    if res.status_code == 200:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "error": res.json()["message"]})


@app.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    if "user" not in SESSION:
        return RedirectResponse("/", status_code=302)
    res = requests.get("http://localhost:8002/products")
    products = res.json()["products"]
    return templates.TemplateResponse("products.html", {"request": request, "products": products})

@app.post("/add_to_cart")
async def add_to_cart(product_id: int = Form(...)):
    username = SESSION.get("user")
    requests.post("http://localhost:8003/add_to_cart", data={"username": username, "product_id": product_id})
    return RedirectResponse("/products", status_code=302)

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    res = requests.post("http://localhost:8001/login", data={"username": username, "password": password})
    if res.status_code == 200:
        SESSION["user"] = username
        # Fetch products directly after successful login
        products_res = requests.get("http://localhost:8002/products")
        products = products_res.json()["products"]
        return templates.TemplateResponse("products.html", {"request": request, "products": products})
    return templates.TemplateResponse("login.html", {"request": request, "error": res.json()["message"]})

@app.get("/cart", response_class=HTMLResponse)
async def view_cart(request: Request):
    username = SESSION.get("user")
    res = requests.get(f"http://localhost:8003/view_cart?username={username}")
    product_ids = res.json()["cart"]
    
    product_details = []
    all_products = requests.get("http://localhost:8002/products").json()["products"]
    for pid in product_ids:
        for product in all_products:
            if product["id"] == pid:
                product_details.append(product)
                
    total = sum(item["price"] for item in product_details)
    return templates.TemplateResponse("cart.html", {"request": request, "products": product_details, "total": total})

@app.post("/clear_cart")
async def clear_cart():
    username = SESSION.get("user")
    if username:
        requests.post("http://localhost:8003/clear_cart", data={"username": username})
    return RedirectResponse("/cart", status_code=302)


@app.post("/pay")
async def simulate_payment(request: Request):
    username = SESSION.get("user")
    if not username:
        return RedirectResponse("/", status_code=302)
    
    # Here you can simulate "payment" success
    # Optionally you can call a payment microservice if you want
    requests.post("http://localhost:8003/clear_cart", data={"username": username})

    return templates.TemplateResponse("payment_success.html", {"request": request, "username": username})


@app.get("/logout")
async def logout():
    SESSION.clear()
    return RedirectResponse("/", status_code=302)
