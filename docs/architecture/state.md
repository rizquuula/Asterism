# Agent State

File: `asterism/agent/state/agent_state.py`

`AgentState` fields:

- `session_id`, `trace_id`, `workspace_root`
- `messages`
- `plan`, `current_task_index`
- `execution_results`, `evaluation_result`
- `final_response`, `error`
- `llm_usage`

This typed state is passed and updated by every graph node.
