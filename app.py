import streamlit as st
import requests

st.title("스마트스토어 상담 챗봇")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 궁금한 점을 자유롭게 질문해 주세요."}
    ]

for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(msg["content"])

user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.spinner("답변 생성 중..."):
        try:
            res = requests.post(
                "http://localhost:8000/chat",
                json={"user_question": user_input},
                timeout=60
            )
            if res.status_code == 200:
                answer = res.text if isinstance(res.text, str) else res.json()["answer"]
            else:
                answer = "서버 오류가 발생했습니다."
        except Exception as e:
            answer = f"서버 연결 오류: {e}"
    st.session_state["messages"].append({"role": "assistant", "content": answer})
