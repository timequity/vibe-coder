# Authentication

## API Key

Get from: https://platform.openai.com/api-keys

```bash
export OPENAI_API_KEY="sk-..."
```

Header format:
```
Authorization: Bearer $OPENAI_API_KEY
```

## Organization ID (Optional)

For accounts with multiple organizations:
```
OpenAI-Organization: org-xxxxxxxxxxxxxxxxxxxxxxxx
```

Get from: https://platform.openai.com/account/organization

## Project ID (Optional)

For project-specific billing/tracking:
```
OpenAI-Project: proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

## Complete Headers Example

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "OpenAI-Organization: org-xxx" \
  -H "OpenAI-Project: proj-xxx" \
  -d '{...}'
```

## Environment Variables

SDKs auto-read these:
- `OPENAI_API_KEY` — Required
- `OPENAI_ORG_ID` — Optional
- `OPENAI_PROJECT_ID` — Optional

## Security

- Never commit API keys to git
- Use environment variables or secret managers
- Rotate keys if exposed
- Use project-scoped keys for production
