import streamlit as st
import requests
from streamlit_chat import message

st.title("스마트스토어 상담 챗봇")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "안녕하세요! 궁금한 점을 자유롭게 질문해 주세요."}
    ]

# 메시지 출력
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        message(msg["content"], is_user=True, key=str(hash(msg["content"]) + 1))
    else:
        message(msg["content"], is_user=False, key=str(hash(msg["content"])))

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("메시지를 입력하세요", key="input")
    send = st.form_submit_button("전송")

if send and user_input:
    # 사용자 메시지 추가
    st.session_state["messages"].append({"role": "user", "content": user_input})

    # 서버에 질문 보내기
    with st.spinner("답변 생성 중..."):
        try:
            res = requests.post(
                "http://localhost:8000/chat",
                json={"user_question": user_input},
                timeout=60
            )
            if res.status_code == 200:
                answer = res.json()["answer"]
            else:
                answer = "서버 오류가 발생했습니다."
        except Exception as e:
            answer = f"서버 연결 오류: {e}"

    # 챗봇 응답 추가
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    # rerun은 필요 없음! clear_on_submit 덕분에 자동 초기화됨
