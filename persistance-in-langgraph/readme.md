# persistance in langGraph


Persistence in LangGraph is a built-in layer that automatically saves and restores the
state of your agent or graph workflow over time. It works by using a
checkpointer to automatically capture snapshots of the graph's state
at every step, organizing them into unique, retrievable threads.