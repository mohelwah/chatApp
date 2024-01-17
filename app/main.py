from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from .db.base import engine, Base
from .db.repository.message_repository import add_message_to_db
import pydantic
from pydantic import BaseModel
from typing import Any

app = FastAPI()

Base.metadata.create_all(bind=engine)


class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="API status code")
    msg: str = pydantic.Field("success", description="API status message")
    data: Any = pydantic.Field(None, description="API data")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }


async def document():
    return RedirectResponse(url="/docs")


app.get("/", response_model=BaseResponse, summary="swagger")(document)


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
