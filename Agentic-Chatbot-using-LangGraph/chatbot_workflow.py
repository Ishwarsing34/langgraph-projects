from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

llm = ChatOpenAI()




class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]



def chat_node(state:ChatState):

    messages = state['messages']
    response = llm.invoke(messages)

    return {'messages' : [response]}


checkpoint = MemorySaver()

graph = StateGraph(ChatState)



graph.add_node('chat_node', chat_node)




graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

thread_id="1"

chatbot = graph.compile(checkpointer=checkpoint)

initial_state = {
   
'messages': [HumanMessage(content='What is Object oriented programming?' )]
}

config = {'configurable' : {'thread_id' : thread_id}}
response = chatbot.invoke(initial_state , config=config)

print(response['messages'][-1].content)