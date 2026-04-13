from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend Smart Blind Assistant OK"}