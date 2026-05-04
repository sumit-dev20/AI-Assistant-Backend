import streamlit as st
from app import chat, extract_text_from_response

st.set_page_config(page_title="AI Memory Chatbot", page_icon="🧠")

st.title("🧠 AI Chatbot with Memory")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat(user_input)
            assistant_reply = extract_text_from_response(response)

            st.markdown(assistant_reply)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
