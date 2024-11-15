import streamlit as st
import time
from dotenv import load_dotenv
import os

from rag.prompt import prompting
from rag.retrieval import retrieve_and_answer
from crawlingAndVectorDB.csvToFaiss import laptop_data_to_faiss
import openai


# 환경변수 불러오기
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
csv_path = os.getenv("csv_path")
faiss_path = os.getenv("faiss_path")

# 노트북 데이터를 Faiss DB화
# laptop_data_to_faiss(csv_path, faiss_path)

# web제목
st.title('컴퓨터 사양 비교 챗봇')

# 사이트설명
st.write("""이 챗봇은 여러 컴퓨터 제품의 사양을 비교하고, 가격 및 특성을 설명해줍니다. 원하는 컴퓨터의 사양을 질문해보세요!""")

# 타자기 효과 함수
def stream_response(text):
    output = ""
    placeholder = st.empty()
    for char in text:
        output += char
        placeholder.markdown(
            f"<div style='text-align: left; background-color: #f0f0f0; color: #333; padding: 10px; border-radius: 10px;'>"
            f"{output}</div>", 
            unsafe_allow_html=True
        )
        time.sleep(0.03)

# 세션 상태에 메시지 기록이 없으면 빈 리스트로 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 내용 출력
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(
                f"<div style='display: flex; justify-content: flex-end;'>"
                f"<div style='text-align: right; background-color: #4CAF50; color: #ffffff; padding: 10px; "
                f"border-radius: 15px 15px 0px 15px; width: fit-content; margin-bottom: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);'>"
                f"<span style='font-weight: bold;'>User:</span> {msg['content']}</div></div>", 
                unsafe_allow_html=True
            )
    else:
        with st.chat_message("assistant"):
            st.markdown(
                f"<div style='text-align: left; background-color: #f0f0f0; color: #333; padding: 10px; border-radius: 10px;'>"
                f"{msg['content']}</div>", 
                unsafe_allow_html=True
            )

# 사용자 질문 받기
if question := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(
            f"<div style='display: flex; justify-content: flex-end;'>"
            f"<div style='text-align: right; background-color: #4CAF50; color: #ffffff; padding: 10px; "
            f"border-radius: 15px 15px 0px 15px; width: fit-content; margin-bottom: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);'>"
            f"<span style='font-weight: bold;'>User:</span> {question}</div></div>", 
            unsafe_allow_html=True
        )
    
    # 진행 상황을 보여주는 함수
    progress = st.progress(0)
    st.write("정보를 검색 중입니다...")

    # 응답 함수 호출 및 진행 상황 표시
    retriever = retrieve_and_answer(faiss_path=faiss_path)
    response = prompting(retriever, question=question)

    # 진행 상태 업데이트
    for i in range(100):
        progress.progress(i + 1)
        time.sleep(0.1)

    # 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

    # 새 응답에만 타자기 효과 적용
    with st.chat_message("assistant"):
        stream_response(response)
