# Executor Node

File: `asterism/agent/nodes/executor/node.py`

Responsibilities:

- Execute current task from plan
- Validate dependencies before execution
- Support linear-plan batch execution in a single pass
- Support parallel dispatch (`Send`) for independent tasks
- Append `TaskResult` entries and advance task index
