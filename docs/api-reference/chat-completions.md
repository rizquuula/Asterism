# Chat Completions

`POST /v1/chat/completions`

OpenAI-compatible endpoint for running Asterism agent workflows.

## Request Body

```json
{
  "model": "llmgateway/psn/Nusa-Max",
  "messages": [{"role": "user", "content": "Summarize this repository"}],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1000,
  "session_id": "optional-session-id"
}
```

## Non-Streaming Response

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "llmgateway/psn/Nusa-Max",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "..."},
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
}
```

## Streaming Response (SSE)

Set `"stream": true` to receive `text/event-stream` chunks (`chat.completion.chunk`) and a terminal `[DONE]` event.

## Notes

- Stateless by default per request.
- `session_id` can be used for tracing/checkpoint thread IDs.
- Supports standard OpenAI chat roles: `system`, `user`, `assistant`, `tool`.
