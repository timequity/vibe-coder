---
name: openai-api
description: |
  OpenAI REST API integration guide. Use when: making direct HTTP calls to OpenAI API,
  understanding API structure without SDK, debugging API requests, learning request/response
  formats, handling errors and rate limits. Covers: authentication, Chat Completions,
  Embeddings, Images (DALL-E), Audio (Whisper/TTS), error handling, streaming.
---

# OpenAI REST API

Direct HTTP integration with OpenAI API. For SDK usage, see `openai-sdk` skill.

## Base URL & Authentication

```
Base URL: https://api.openai.com/v1
```

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{...}'
```

Optional headers:
- `OpenAI-Organization: org-xxx` — for multi-org accounts
- `OpenAI-Project: proj-xxx` — for project-specific billing

## Core Endpoints

| Endpoint | Method | Use Case |
|----------|--------|----------|
| `/chat/completions` | POST | Text generation, chat |
| `/embeddings` | POST | Vector embeddings |
| `/images/generations` | POST | DALL-E image creation |
| `/audio/transcriptions` | POST | Whisper speech-to-text |
| `/audio/speech` | POST | TTS text-to-speech |
| `/models` | GET | List available models |

## Quick Reference

### Chat Completions (most common)

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

Response structure:
```json
{
  "id": "chatcmpl-xxx",
  "choices": [{
    "message": {"role": "assistant", "content": "Hi! How can I help?"},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18}
}
```

### Embeddings

```bash
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "text-embedding-3-small", "input": "Hello world"}'
```

### Streaming

Add `"stream": true` to request. Response is SSE:
```
data: {"choices":[{"delta":{"content":"Hello"}}]}
data: {"choices":[{"delta":{"content":" world"}}]}
data: [DONE]
```

## References

- **[authentication.md](references/authentication.md)** — API keys, organization/project IDs
- **[chat-completions.md](references/chat-completions.md)** — Full Chat Completions API
- **[models.md](references/models.md)** — Model list, capabilities, pricing tiers
- **[errors.md](references/errors.md)** — Error codes, retry strategies, rate limits

## Official Documentation

For latest/complete docs, fetch:
- `https://cdn.openai.com/API/docs/txt/llms-api-reference.txt`
- `https://cdn.openai.com/API/docs/txt/llms-guides.txt`
