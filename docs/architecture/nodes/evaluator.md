# Evaluator Node

File: `asterism/agent/nodes/evaluator/node.py`

Responsibilities:

- Evaluate execution results and current progress
- Decide whether to `continue`, `replan`, or `finalize`
- Skip LLM evaluation when safe (completed linear plan fast-path)
- Emit fallback evaluation if LLM evaluation fails
