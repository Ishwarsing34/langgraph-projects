from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph.message import add_messages

llm = ChatOpenAI()




class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]



def chat_node(state:ChatState):

    messages = state['messages']
    response = llm.invoke(messages)

    return {'messages' : [response]}




graph = StateGraph(ChatState)



graph.add_node('chat_node', chat_node)




graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)



chatbot = graph.compile()

initial_state = {
'messages': [HumanMessage(content='What is Object oriented programming?' )]
}

response = chatbot.invoke(initial_state)

print(response['messages'][-1].content)