# Chat Completions API

## Endpoint

```
POST https://api.openai.com/v1/chat/completions
```

## Request Body

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "System instructions"},
    {"role": "user", "content": "User message"},
    {"role": "assistant", "content": "Previous assistant response"},
    {"role": "user", "content": "Follow-up question"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

## Message Roles

| Role | Purpose |
|------|---------|
| `system` | High-level instructions, persona |
| `user` | User input |
| `assistant` | Model's previous responses |
| `tool` | Tool/function call results |

## Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | required | Model ID (gpt-4o, gpt-4o-mini, etc.) |
| `messages` | array | required | Conversation messages |
| `temperature` | float | 1.0 | Randomness (0-2) |
| `max_tokens` | int | model max | Max output tokens |
| `top_p` | float | 1.0 | Nucleus sampling |
| `stream` | bool | false | Enable streaming |
| `stop` | string/array | null | Stop sequences |
| `n` | int | 1 | Number of completions |
| `presence_penalty` | float | 0 | Penalize repeated topics (-2 to 2) |
| `frequency_penalty` | float | 0 | Penalize repeated tokens (-2 to 2) |
| `response_format` | object | null | JSON mode: `{"type": "json_object"}` |

## Response

```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677858242,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text here"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 7,
    "total_tokens": 20
  }
}
```

## finish_reason Values

| Value | Meaning |
|-------|---------|
| `stop` | Natural completion or hit stop sequence |
| `length` | Hit max_tokens limit |
| `tool_calls` | Model wants to call a tool |
| `content_filter` | Content flagged by moderation |

## Streaming

Request with `"stream": true`. Response is SSE:

```
data: {"id":"chatcmpl-xxx","choices":[{"delta":{"role":"assistant"}}]}
data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":"Hello"}}]}
data: {"id":"chatcmpl-xxx","choices":[{"delta":{"content":" world"}}]}
data: {"id":"chatcmpl-xxx","choices":[{"finish_reason":"stop"}]}
data: [DONE]
```

## Tool Calling (Function Calling)

```json
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "What's the weather in Paris?"}],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City name"}
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

Tool call response:
```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_abc123",
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"location\": \"Paris\"}"
        }
      }]
    },
    "finish_reason": "tool_calls"
  }]
}
```

Submit tool result:
```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "What's the weather in Paris?"},
    {"role": "assistant", "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "call_abc123", "content": "22°C, sunny"}
  ]
}
```

## JSON Mode

Force valid JSON output:
```json
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "List 3 colors as JSON array"}],
  "response_format": {"type": "json_object"}
}
```

Note: Prompt must mention "JSON" for this to work reliably.
