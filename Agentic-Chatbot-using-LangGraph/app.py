
from agentic_chatbot_backend import chatbot
from langchain_core.messages import HumanMessage
import streamlit as st


CONFIG = {
    "configurable": {
        "thread_id": "thread-1"
    }
}


if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


st.title("Agentic Chatbot with LangGraph")


for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type here")


if user_input:

    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.text(user_input)

    with st.chat_message("assistant"):

        def response_generator():
            for message, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=CONFIG,
                stream_mode="messages"
            ):
                if message.content:
                    yield message.content

        ai_message = st.write_stream(response_generator())

    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })

