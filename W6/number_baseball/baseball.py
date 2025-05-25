import streamlit as st
import random
import requests
import json

# Ollama 설정
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"

# 정답 세팅 (세션에 저장)
if 'answer' not in st.session_state:
    st.session_state.answer = ''.join(random.sample('0123456789', 3))
    st.session_state.tries = []

# 숫자야구 판정 함수
def judge(guess, answer):
    strike = sum(g == a for g, a in zip(guess, answer))
    ball = sum(min(guess.count(d), answer.count(d)) for d in set(guess)) - strike
    return strike, ball

# Ollama로부터 자연어 피드백 받기
def get_gemma_feedback(guess, result):
    prompt = f"""너는 숫자야구 게임 도우미야.
정답은 비밀이고, 사용자가 {guess}를 입력했을 때 나온 결과는 {result} 이야.
이 결과를 바탕으로 사용자에게 재밌고 간단한 피드백을 줘.
"""
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })
    return response.json()['response'].strip()

# Streamlit UI
st.title("🎯 숫자야구 게임 (with Ollama Gemma 3)")

with st.form("guess_form"):
    guess = st.text_input("3자리 숫자를 입력하세요 (0~9, 중복 없이)", max_chars=3)
    submitted = st.form_submit_button("확인")

    if submitted:
        if len(guess) != 3 or not guess.isdigit() or len(set(guess)) != 3:
            st.error("⚠️ 올바른 3자리 숫자를 입력하세요. (중복 불가)")
        else:
            strike, ball = judge(guess, st.session_state.answer)
            result_text = f"{strike}스트라이크 {ball}볼"
            feedback = get_gemma_feedback(guess, result_text)
            st.session_state.tries.append((guess, result_text, feedback))

# 이전 결과 출력
for g, res, fb in reversed(st.session_state.tries):
    st.markdown(f"📌 **입력:** `{g}` → **결과:** {res}")
    st.info(fb)

# 승리 조건
if st.session_state.tries and st.session_state.tries[-1][1].startswith("3스트라이크"):
    st.success("🎉 정답입니다! 게임을 새로 시작하려면 페이지를 새로고침하세요.")
