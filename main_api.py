import json
import openai
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from Ai_models.count_tokens_wtf import count_tokens
from data import db_session
from data.api_keys import API_keys
from data.users import User

from Ai_models.yandexgptlite import yandexgptlite_requst
from Ai_models.llama_lite import llama8b_requst
from Ai_models.llama_pro import llama70b_requst
from Ai_models.yandexgptpro import yandexgptpro_requst


db_session.global_init("db/users.db")
app = FastAPI()


class ChatRequest(BaseModel):
    model: str
    messages: list
    temperature: float
    max_tokens: int


def processing_message(message: list) -> list:
    try:
        if message[0]['role'] != 'system':
            return [False, 'Uncorrected request, maybe "system"?', ""]
        if message[1]['role'] != 'user':
            return [False, 'Uncorrected request, maybe "user"?', ""]
        if message[0]['content'] == '':
            return [False, 'Uncorrected request, empty content for system', ""]
        if message[1]['content'] == '':
            return [False, 'Uncorrected request, empty content for user', ""]
        return [True, message[0]['content'], message[1]['content']]
    except:
        return [False, 'Uncorrected request, not enough data', ""]


@app.get("/")
def read_root():
    return {"message": "Welcome, my API"}

@app.get("/api/v0/{api_keys}")
async def check_api_keys(api_keys: str, request: ChatRequest):
    db_sess = db_session.create_session()
    aboit_api_key = db_sess.query(API_keys).filter(API_keys.api_key == api_keys).first()
    if aboit_api_key:
        id_user = aboit_api_key.user_id
        user = db_sess.query(User).filter(User.id == id_user).first()
        count_tokens_user = int(user.count_tokes)
        if count_tokens_user > -10:
            flag, system_context, user_context = processing_message(request.messages)
            if flag:
                if request.model == "YandexGPT-lite":
                    if count_tokens_user < 0:
                        request.max_tokens = 10 + count_tokens_user
                    final_message = str(yandexgptlite_requst(system_context, user_context, request.max_tokens,
                                                                request.temperature))
                    count_tokens_user -= count_tokens(final_message) * 0.0002
                    count_tokens_user -= count_tokens(user_context) * 0.0002
                    user.count_tokes = count_tokens_user
                    db_sess.commit()
                    return {"message": final_message}
                elif request.model == "Llama-8b":
                    if count_tokens_user < 0:
                        request.max_tokens = 10 + count_tokens_user
                    final_message = str(llama8b_requst(system_context, user_context, request.max_tokens,
                                                                request.temperature))
                    count_tokens_user -= count_tokens(final_message) * 0.0002
                    count_tokens_user -= count_tokens(user_context) * 0.0002
                    user.count_tokes = count_tokens_user
                    db_sess.commit()
                    return {"message": final_message}
                elif request.model == "Llama-70b":
                    if count_tokens_user < 0:
                        request.max_tokens = 10 + count_tokens_user
                    final_message = str(llama70b_requst(system_context, user_context, request.max_tokens,
                                                                request.temperature))
                    count_tokens_user -= count_tokens(final_message) * 0.0012
                    count_tokens_user -= count_tokens(user_context) * 0.0012
                    user.count_tokes = count_tokens_user
                    db_sess.commit()
                    return {"message": final_message}
                elif request.model == "YandexGPT-pro":
                    if count_tokens_user < 0:
                        request.max_tokens = 10 + count_tokens_user
                    final_message = str(yandexgptpro_requst(system_context, user_context, request.max_tokens,
                                                                request.temperature))
                    count_tokens_user -= count_tokens(final_message) * 0.0012
                    count_tokens_user -= count_tokens(user_context) * 0.0012
                    user.count_tokes = count_tokens_user
                    db_sess.commit()
                    return {"message": final_message}
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"message": "Invalid Ai models"},
                    )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"message": system_context},
                )
        else:
            return JSONResponse(
                status_code=400,
                content={"message": "Not enough tokens for request, you need to up tokens in account"},
            )
    else:
        return JSONResponse(
            status_code=404,
            content={"message": "API key is invalid"},
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)