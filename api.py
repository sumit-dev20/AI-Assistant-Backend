from fastapi import FastAPI
from pydantic import BaseModel
from app import chat, extract_text_from_response

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"response": "server is live"}


@app.post("/chat")
def chat_api(req: ChatRequest):
    raw_response = chat(req.message)

    clean_text = extract_text_from_response(raw_response)

    return {"response": clean_text}
