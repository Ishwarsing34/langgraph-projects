# Persistance in LangGraph


Persistence in LangGraph is a built-in layer that automatically saves and restores the
state of your agent or graph workflow over time. It works by using a
checkpointer to automatically capture snapshots of the graph's state
at every step, organizing them into unique, retrievable threads.

# speciality of persistance

It can save the information of Intermediate state along with final state also it has a fault tolerance means suppose your app crashes then when you restart the app it will be resumed from where it crashed

