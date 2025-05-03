import json
import openai

from pydantic import BaseModel
from fastapi import FastAPI
from data import db_session
from data.api_keys import API_keys

from Ai_models.yandexgpt_test_work import yandexgptlite_requst


db_session.global_init("db/users.db")
app = FastAPI()


class ChatRequest(BaseModel):
    model: str
    messages: list
    temperature: float
    max_tokens: int


@app.get("/")
def read_root():
    return {"message": "Welcome, my API"}

@app.get("/api/v0/{api_keys}")
async def check_api_keys(api_keys: str, request: ChatRequest):
    db_sess = db_session.create_session()
    user = db_sess.query(API_keys).filter(API_keys.api_key == api_keys).first()
    if user:
        if request.model == "YandexGPT-lite":
            return {"message": str(yandexgptlite_requst(str(request.messages[1]["content"])))}
        else:
            return {"error": "Invalid Ai models"}
    else:
        return {"error": "API key is invalid"}

