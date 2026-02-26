# Workflow

## 1) Planner
Creates a structured `Plan` from user intent and available MCP tools.

## 2) Executor
Runs planned tasks (LLM or MCP), including linear-plan batching and optional parallel dispatch for independent tasks.

## 3) Evaluator
Decides one of: continue, replan, finalize. Uses fast-path finalize for successful completed linear plans.

## 4) Finalizer
Builds execution trace and synthesizes the final user-facing answer.
