# Error Handling

## Error Response Format

```json
{
  "error": {
    "message": "Human readable error message",
    "type": "error_type",
    "param": "parameter_name",
    "code": "error_code"
  }
}
```

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Fix request parameters |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check permissions/org |
| 404 | Not Found | Check endpoint/model |
| 429 | Rate Limited | Retry with backoff |
| 500 | Server Error | Retry |
| 503 | Service Unavailable | Retry |

## Common Error Codes

| Code | Description |
|------|-------------|
| `invalid_api_key` | API key invalid or expired |
| `insufficient_quota` | Out of credits |
| `rate_limit_exceeded` | Too many requests |
| `context_length_exceeded` | Input too long |
| `invalid_request_error` | Malformed request |
| `model_not_found` | Model doesn't exist |

## Retry Strategy

```python
import time
import random

def call_with_retry(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait = (2 ** attempt) + random.random()
            time.sleep(wait)
        except (APIError, ServiceUnavailableError):
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    raise Exception("Max retries exceeded")
```

## Rate Limit Headers

Response headers show limits:
```
x-ratelimit-limit-requests: 500
x-ratelimit-limit-tokens: 30000
x-ratelimit-remaining-requests: 499
x-ratelimit-remaining-tokens: 29500
x-ratelimit-reset-requests: 200ms
x-ratelimit-reset-tokens: 1s
```

## Handling 429 (Rate Limit)

1. Check `Retry-After` header
2. Use exponential backoff: 1s, 2s, 4s, 8s...
3. Add jitter to prevent thundering herd
4. Consider request queuing

## Context Length Errors

When `context_length_exceeded`:
1. Truncate older messages
2. Summarize conversation history
3. Use model with larger context
4. Split into multiple requests

## Best Practices

1. **Always handle errors** — don't assume success
2. **Log error details** — for debugging
3. **Use timeouts** — prevent hanging requests
4. **Implement circuit breakers** — for sustained failures
5. **Monitor rate limit headers** — proactive throttling
6. **Have fallback models** — gpt-4o-mini if gpt-4o fails
