# Planner Node

File: `asterism/agent/nodes/planner/node.py`

Responsibilities:

- Build planning context from messages + tool schemas
- Call structured LLM output (`Plan`)
- Validate/enrich plan
- Write plan + usage to state

On failure, planner stores an error state for downstream handling.
