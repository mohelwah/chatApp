from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.db.utlis import create_tables, reset_tables
from .db.repository.message_repository import add_message_to_db
import pydantic
from pydantic import BaseModel
from typing import Any
from .utils import get_model_worker_config
from .schemas import BaseResponse
from .chat import chat_stream
from .webui_pages.utils import ApiRequest

app = FastAPI()

reset_tables()
create_tables()


async def document():
    return RedirectResponse(url="/docs")


app.get("/", response_model=BaseResponse, summary="swagger")(document)

app.post("/chat", response_model=BaseResponse, summary="chat")(chat_stream)


@app.post("/message")
def add_message():
    chat_type = "test"
    query = "test query"
    respone = "test response"
    # converation_id:str, chat_type, query, response=''
    message_id = add_message_to_db(
        converation_id="1234",
        chat_type="llm_chat",
        query=query,
    )

    return {"data": {message_id}}


@app.post("/test")
def test():
    api_request = ApiRequest()
    return {"Api request is done"}


@app.post("/test_apiRequest")
def test():
    api_request = ApiRequest()
    get_return = api_request.get("/test")
    return {"Api request is done ": get_return}
