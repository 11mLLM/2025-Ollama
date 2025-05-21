import streamlit as st
from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Gemma 모델
llm = Ollama(model="gemma3:latest")

st.set_page_config(page_title="뭐 만들어 먹지?", page_icon="🍽️")
st.title("🍚 뭐 만들어 먹지?")

if "ingredient" not in st.session_state:
    st.session_state.ingredient = ""
if "dishes" not in st.session_state:
    st.session_state.dishes = []
if "selected_dish" not in st.session_state:
    st.session_state.selected_dish = None

# 재료 입력
def get_dish_recommendations():
    st.session_state.selected_dish = None
    ingredient = st.session_state.ingredient

    if ingredient.strip() == "":
        st.warning("재료를 입력해주세요.")
        return

    prompt_template = PromptTemplate.from_template(
        "다음 재료를 써서 간단하게 만들 수 있는 한국 음식 5가지를 추천해줘: {ingredient}. 각 음식은 한 줄로만 알려줘."
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(ingredient)

    st.session_state.dishes = [
        dish.strip("-• \n") for dish in response.strip().split("\n") if dish.strip()
    ]

st.text_input(
    "재료를 입력하세요 (예: 사과, 당근)",
    key="ingredient",
    on_change=get_dish_recommendations,
)

# 음식 리스트 출력 및 선택
if st.session_state.dishes and not st.session_state.selected_dish:
    st.subheader(f"🧑‍🍳 '{st.session_state.ingredient}'(으)로 만들 수 있는 음식들:")
    dish_choice = st.radio("음식을 하나 선택하세요:", st.session_state.dishes)

    if st.button("레시피 보기"):
        st.session_state.selected_dish = dish_choice

# 레시피 출력
if st.session_state.selected_dish:
    st.subheader(f"📋 '{st.session_state.selected_dish}'의 레시피")

    recipe_prompt = PromptTemplate.from_template(
        "한국 요리 '{dish}'의 상세한 레시피를 단계별로 설명해줘. 간단명료하게 부탁해."
    )
    recipe_chain = LLMChain(llm=llm, prompt=recipe_prompt)
    recipe = recipe_chain.run(st.session_state.selected_dish)

    st.markdown(recipe)
