# Finalizer Node

File: `asterism/agent/nodes/finalizer/node.py`

Responsibilities:

- Build execution trace for transparency
- Return structured error response when tasks fail
- Call LLM to synthesize successful final response
- Persist `final_response` and usage in state
