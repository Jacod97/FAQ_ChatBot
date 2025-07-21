import openai
import chromadb
from dotenv import load_dotenv
load_dotenv()

class ChatBot:
    def __init__(self ,persist_path="./data/chroma"):
        self.chroma = chromadb.PersistentClient(path=persist_path)
        self.vector_db = self.chroma.get_or_create_collection(name="try1")
        
    def retriever(self, user_question):
        vector = openai.embeddings.create(
            input = user_question,
            model = "text-embedding-3-small"
        ).data[0].embedding

        result = self.vector_db.query(
            query_embeddings=[vector],
            n_results=3
        )

        chunks = [
            f"User : {q}\nChatBot : {meta['answer']}"
            for q,meta in zip(result['documents'][0], result['metadatas'][0])
        ]
        return "\n\n".join(chunks)
    
    def _set_prompt(self, context, user_question):
        prompt = f"""
        당신은 스마트스토어에 특화된 상담 AI입니다. 다음 지침을 따라 사용자 질문에 정확하고 친절하게 답변하세요.

        지침:
        - 아래 FAQ는 자주 묻는 질문들입니다. 반드시 이 FAQ에서 근거가 되는 내용만 바탕으로 답변하세요.
        - 사용자 질문이 스마트스토어와 무관하다면 관련 질문을 다시 요청하세요.
        - FAQ에 근거한 정답을 먼저 제공한 뒤, 사용자가 추가로 궁금해할 만한 항목 2~3가지를 짧고 공손한 질문 형식으로 제안해 후속 대화를 유도하세요.
        - 모든 답변은 공손하고 간결한 말투로 작성하세요.

        FAQ:
        {context}

        사용자 질문: {user_question}
        답변:
        """
        return prompt
    
    def response(self, user_question):
        self.context = self.retriever(user_question)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": self._set_prompt(self.context, user_question)}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()