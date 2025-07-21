import openai
import chromadb
import re
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
        당신은 스마트스토어 전문 상담 AI입니다. 아래 예시처럼 FAQ를 기반으로 사용자 질문에 공손하고 정확하게 답변하세요.  
        - FAQ 내용 외의 질문에는 스마트스토어 관련 질문을 유도해주세요.  
        - 답변 후에는 관련된 짧은 후속 질문 2~3개를 제안해 대화를 자연스럽게 이어가세요.
        - 후속 질문은 줄을 바꿔서 각각 `-` 기호로 시작하세요.

        예시 1:
        유저: 미성년자도 판매 회원 등록이 가능한가요?
        챗봇: 네이버 스마트스토어는 만 14세 미만의 개인(개인 사업자 포함) 또는 법인사업자는 입점이 불가함을 양해 부탁 드립니다.
                - 등록에 필요한 서류 안내해드릴까요?
                - 등록 절차는 얼마나 오래 걸리는지 안내가 필요하신가요?

        예시 2:
        유저: 오늘 저녁에 여의도 가려는데 맛집 추천 좀 해줄래?
        챗봇: 저는 스마트스토어 FAQ를 위한 챗봇입니다. 스마트스토어에 대한 질문을 부탁드립니다.
                - 음식도 스토어 등록이 가능한지 궁금하신가요?

        FAQ:
        {context}

        유저: {user_question}
        챗봇:
        """
        return prompt
    
    def response(self, user_question):
        self.context = self.retriever(user_question)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": self._set_prompt(self.context, user_question)}],
            temperature=0.7
        )
        response_text = response.choices[0].message.content.strip()
        print("LLM output:", response_text)
        return response_text