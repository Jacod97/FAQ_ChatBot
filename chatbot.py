import openai
import chromadb

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
    
    def _set_prompt(self,context, user_question):
        prompt = f"""
        당신은 상담 AI입니다.
        다음의 지시 사항을 참고하여 사용자의 질문에 정확하고 친절하게 답변해주세요.

        지시 사항:
        - 아래 FAQ는 자주 묻는 질문들입니다.
        - 반드시 아래 FAQ에서 근거가 되는 부분만 사용하여 답변하세요.
        - 스마트 스토어와 관련이 없는 질문일 경우, 관련 질문을 다시 요청해주세요.

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