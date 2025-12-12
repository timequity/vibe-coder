# Python SDK

## Installation

```bash
pip install openai
```

## Client Initialization

### Sync Client
```python
from openai import OpenAI

# From environment (recommended)
client = OpenAI()

# Explicit config
client = OpenAI(
    api_key="sk-...",
    organization="org-...",
    project="proj-...",
    timeout=60.0,
    max_retries=3
)
```

### Async Client
```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello"}]
    )
```

## Chat Completions

### Basic
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

### With Parameters
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku"}],
    temperature=0.7,
    max_tokens=100,
    top_p=1.0,
    frequency_penalty=0,
    presence_penalty=0
)
```

### JSON Mode
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "List 3 colors as JSON"}],
    response_format={"type": "json_object"}
)
data = json.loads(response.choices[0].message.content)
```

## Tool Calling

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Weather in Paris?"}],
    tools=tools
)

# Check for tool calls
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    # Execute function, then continue conversation
```

## Embeddings

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello world"
)
vector = response.data[0].embedding  # List[float]

# Multiple inputs
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=["Text 1", "Text 2", "Text 3"]
)
vectors = [d.embedding for d in response.data]
```

## Images

### Generation
```python
response = client.images.generate(
    model="dall-e-3",
    prompt="A futuristic city",
    size="1024x1024",  # or 1792x1024, 1024x1792
    quality="standard",  # or "hd"
    n=1
)
image_url = response.data[0].url
```

### Variations (DALL-E 2)
```python
with open("image.png", "rb") as f:
    response = client.images.create_variation(
        model="dall-e-2",
        image=f,
        n=1,
        size="1024x1024"
    )
```

## Audio

### Transcription (Speech-to-Text)
```python
with open("audio.mp3", "rb") as f:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        response_format="text"  # or "json", "srt", "vtt"
    )
print(transcript)
```

### Translation (to English)
```python
with open("french_audio.mp3", "rb") as f:
    translation = client.audio.translations.create(
        model="whisper-1",
        file=f
    )
```

### Text-to-Speech
```python
response = client.audio.speech.create(
    model="tts-1",  # or "tts-1-hd"
    voice="alloy",  # alloy, echo, fable, onyx, nova, shimmer
    input="Hello, world!"
)
response.stream_to_file("output.mp3")
```

## Error Handling

```python
from openai import (
    OpenAI,
    APIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    BadRequestError
)

client = OpenAI()

try:
    response = client.chat.completions.create(...)
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limited - retry with backoff")
except BadRequestError as e:
    print(f"Bad request: {e.message}")
except APIConnectionError:
    print("Connection failed")
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Timeout & Retries

```python
client = OpenAI(
    timeout=60.0,      # Request timeout in seconds
    max_retries=3      # Auto-retry on failures
)

# Per-request timeout
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    timeout=30.0
)
```

## Response Objects

```python
response = client.chat.completions.create(...)

# Access fields
response.id           # "chatcmpl-xxx"
response.model        # "gpt-4o-2024-08-06"
response.created      # Unix timestamp
response.choices      # List of choices
response.usage.prompt_tokens
response.usage.completion_tokens
response.usage.total_tokens

# First choice
choice = response.choices[0]
choice.message.role      # "assistant"
choice.message.content   # Response text
choice.finish_reason     # "stop", "length", "tool_calls"
```
