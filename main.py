from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from chatbot import ChatBot
import uvicorn
import openai

class QueryRequest(BaseModel):
    user_question: str

app = FastAPI()

bot = ChatBot()

def llm_stream(prompt):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        stream=True
    )
    for chunk in response:
        delta = chunk.choices[0].delta
        if hasattr(delta, "content") and delta.content:
            yield delta.content

@app.post("/chat")
async def chat(request: QueryRequest):
    prompt = bot.get_prompt(request.user_question)
    return StreamingResponse(llm_stream(prompt), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
