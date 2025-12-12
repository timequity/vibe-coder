# OpenAI Models

## Recommended Models (2025)

| Model | Context | Best For | Cost |
|-------|---------|----------|------|
| `gpt-4o` | 128K | General purpose, multimodal | $$ |
| `gpt-4o-mini` | 128K | Fast, cheap, most tasks | $ |
| `o1` | 128K | Complex reasoning | $$$$ |
| `o1-mini` | 128K | Coding, math reasoning | $$$ |
| `gpt-4-turbo` | 128K | Legacy, stable | $$$ |

## Model Capabilities

### GPT-4o Family
- Multimodal (text + images)
- Function calling
- JSON mode
- Streaming
- Vision

### o1 Family (Reasoning)
- Extended thinking
- Complex problem solving
- Math and coding
- No streaming support
- No function calling

## Embeddings Models

| Model | Dimensions | Use Case |
|-------|------------|----------|
| `text-embedding-3-small` | 1536 | Cost-effective |
| `text-embedding-3-large` | 3072 | Higher quality |
| `text-embedding-ada-002` | 1536 | Legacy |

## Image Models

| Model | Capabilities |
|-------|--------------|
| `dall-e-3` | Best quality, 1024x1024, 1792x1024 |
| `dall-e-2` | Faster, variations, edits |
| `gpt-image-1` | Latest, edit/inpaint support |

## Audio Models

| Model | Type | Use |
|-------|------|-----|
| `whisper-1` | STT | Transcription, translation |
| `tts-1` | TTS | Fast speech synthesis |
| `tts-1-hd` | TTS | High quality speech |

## Rate Limits by Tier

| Tier | RPM | TPM | Description |
|------|-----|-----|-------------|
| Free | 3 | 40K | Trial |
| Tier 1 | 500 | 30K-200K | $5+ paid |
| Tier 2 | 5K | 450K-2M | $50+ paid |
| Tier 3 | 5K | 800K-4M | $100+ paid |
| Tier 4 | 10K | 2M-10M | $250+ paid |
| Tier 5 | 10K | 30M-150M | $1000+ paid |

RPM = Requests per minute, TPM = Tokens per minute

## List Models API

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Response:
```json
{
  "data": [
    {"id": "gpt-4o", "object": "model", "owned_by": "openai"},
    {"id": "gpt-4o-mini", "object": "model", "owned_by": "openai"}
  ]
}
```

## Model Snapshots

Production apps should pin to snapshots:
- `gpt-4o-2024-08-06` instead of `gpt-4o`
- `gpt-4o-mini-2024-07-18` instead of `gpt-4o-mini`

Unpinned aliases update automatically (may change behavior).
