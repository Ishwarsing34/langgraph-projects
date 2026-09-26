
from agentic_chatbot_backend import chatbot
from langchain_core.messages import HumanMessage
import streamlit as st


CONFIG = {
    "configurable": {
        "thread_id": "thread-1"
    }
}


# Initialize message history
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


st.title("Agentic Chatbot with LangGraph")


# Load conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


# Get user input
user_input = st.chat_input("Type here")


if user_input:

    # Add user message to history
    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.text(user_input)

    # Invoke LangGraph chatbot
    response = chatbot.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        config=CONFIG
    )

    # Get AI response
    ai_message = response["messages"][-1].content

    # Add AI response to history
    st.session_state["message_history"].append({
        "role": "assistant",
        "content": ai_message
    })

    # Display AI response
    with st.chat_message("assistant"):
        st.text(ai_message)

