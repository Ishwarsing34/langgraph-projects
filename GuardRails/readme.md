# Section 1: What are Guardrails?

Guardrails are safety mechanisms that control what goes into and comes out of an Al agent. They sit around your agent pipeline and ensure the agent:

. only processes safe, appropriate inputs
. only performs approved actions
. only returns validated, compliant outputs

# Guardrails help you build safe, compliant Al applications by validating and filtering content at key points in your agent's execution.

They are implemented as middleware that intercepts execution:

. Before the agent starts (input guardrails)
· After it completes (output guardrails)
. Around model and tool calls