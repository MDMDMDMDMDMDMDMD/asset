import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

load_dotenv()
mongo_uri = os.getenv("MONGODB_URI")

cluster = MongoClient(mongo_uri)
db = cluster.MockEGov
collection = db.Users

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, user_id: int = Form(...), username: str = Form(...), surname: str = Form(...)):
    # Проверка данных в MongoDB
    search_params = {
        "_id": user_id,
        "name": username,
        "surname": surname
    }
    result = collection.find_one(search_params)

    if result:
        return templates.TemplateResponse("landing.html", {"request": request, "username": username})
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error_message": "Invalid credentials"})


@app.get("/pup.html", response_class=HTMLResponse)
def read_pup_html(request: Request):
    return templates.TemplateResponse("pup.html", {"request": request})


@app.get("/buy_page", response_class=HTMLResponse)
def read_buy_page(request: Request, price: int = Query(...)):
    return templates.TemplateResponse("buy.html", {"request": request, "price": price})


@app.post("/calculate_fsum", response_class=HTMLResponse)
async def calculate_fsum(
    request: Request,
    risk: int = Form(...),
    active_recreation: str = Form(...),
    risk_level: int = Form(...),
    insurance_claims: str = Form(...),
):
    user_id_to_find = 190068729008
    query = {"_id": user_id_to_find}

    user_data = collection.find_one(query)

    if user_data:
        sex = user_data.get("sex")
        birth_date = user_data.get("birthDate")
        region = user_data.get("region")

        # Assign numerical values based on conditions
        sex_value = 2 if sex == "male" else 1  # 2 for male, 1 for female
        birth_year = birth_date.year if birth_date else None
        birth_date_value = 1 if birth_year and birth_year >= 2004 else (
            2 if birth_year and birth_year >= 1994 else (3 if birth_year and birth_year >= 1984 else None))
        region_value = 1 if region.lower() == "almaty" else 2  # 1 for Almaty, 2 for other regions

        fsum = 1000
        sport = 1
        riskwork = 1
        befor = 1

        # Calculate x
        x = sex_value + birth_date_value + region_value + sport + riskwork + befor

        # Apply conditions and update fsum
        if x < 10:
            fsum += 200
        elif x == 10:
            fsum += 400
        elif x > 10:
            fsum += 600

        # Multiply fsum by risk
        fsum *= 2 if risk == 1 else (4 if risk == 2 else (6 if risk == 3 else 1))

        # Now you can use fsum as needed
        return templates.TemplateResponse("pup.html", {"request": request, "fsum": fsum})
    else:
        return {"error": f"User with ID {user_id_to_find} not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)



