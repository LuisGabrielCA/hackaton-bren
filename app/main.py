from fastapi import FastAPI
from pydantic import BaseModel
from ai_agent import process_text

app = FastAPI()

class Text(BaseModel):
    mensagem: str

@app.post("/chat")
async def chat(text: Text):
    response = process_text(text.mensagem)
    return {"result": response}

@app.get("/healthcheck")
async def healthcheck():
    return {"result": "OK"}
