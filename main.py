from fastapi import FastAPI, Request
from pydantic import BaseModel
from chatbot import ChatBot
import uvicorn

# 사용자 요청을 위한 Pydantic 모델 정의
class QueryRequest(BaseModel):
    user_question: str

# FastAPI 앱 생성
app = FastAPI()

# ChatBot 인스턴스 생성
bot = ChatBot(persist_path="./data/chroma")

@app.post("/chat")
async def chat(request: QueryRequest):
    answer = bot.response(request.user_question)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
