# Streaming Responses

## Why Streaming?

- Better UX — show response as it generates
- Lower perceived latency
- Process large responses incrementally

## Python Streaming

### Basic
```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
```

### Async Streaming
```python
async def stream_response():
    stream = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Write a story"}],
        stream=True
    )

    async for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
```

### Collect Full Response
```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi"}],
    stream=True
)

full_response = ""
for chunk in stream:
    content = chunk.choices[0].delta.content or ""
    full_response += content
    print(content, end="", flush=True)

print(f"\n\nFull: {full_response}")
```

### With Tool Calls
```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Weather in Paris?"}],
    tools=[...],
    stream=True
)

tool_calls = []
for chunk in stream:
    delta = chunk.choices[0].delta

    if delta.tool_calls:
        for tc in delta.tool_calls:
            if tc.index >= len(tool_calls):
                tool_calls.append({"id": "", "function": {"name": "", "arguments": ""}})

            if tc.id:
                tool_calls[tc.index]["id"] = tc.id
            if tc.function.name:
                tool_calls[tc.index]["function"]["name"] = tc.function.name
            if tc.function.arguments:
                tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments
```

## Node.js Streaming

### Basic
```typescript
const stream = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Write a story" }],
  stream: true
});

for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content;
  if (content) {
    process.stdout.write(content);
  }
}
```

### Collect Full Response
```typescript
const stream = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Hi" }],
  stream: true
});

let fullResponse = "";
for await (const chunk of stream) {
  const content = chunk.choices[0]?.delta?.content || "";
  fullResponse += content;
  process.stdout.write(content);
}

console.log(`\n\nFull: ${fullResponse}`);
```

### Web API (Server-Sent Events)
```typescript
// Next.js API Route
export async function POST(req: Request) {
  const { messages } = await req.json();

  const stream = await client.chat.completions.create({
    model: "gpt-4o",
    messages,
    stream: true
  });

  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      for await (const chunk of stream) {
        const content = chunk.choices[0]?.delta?.content;
        if (content) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`));
        }
      }
      controller.enqueue(encoder.encode("data: [DONE]\n\n"));
      controller.close();
    }
  });

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "Connection": "keep-alive"
    }
  });
}
```

### Client-Side Consumption
```typescript
const response = await fetch("/api/chat", {
  method: "POST",
  body: JSON.stringify({ messages })
});

const reader = response.body!.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  const lines = text.split("\n");

  for (const line of lines) {
    if (line.startsWith("data: ") && line !== "data: [DONE]") {
      const data = JSON.parse(line.slice(6));
      console.log(data.content);
    }
  }
}
```

## Chunk Structure

```typescript
// Stream chunk shape
{
  id: "chatcmpl-xxx",
  object: "chat.completion.chunk",
  created: 1234567890,
  model: "gpt-4o",
  choices: [{
    index: 0,
    delta: {
      role?: "assistant",      // First chunk only
      content?: "Hello",       // Text content
      tool_calls?: [...]       // If calling tools
    },
    finish_reason: null | "stop" | "length" | "tool_calls"
  }]
}
```

## Best Practices

1. **Always check for content** — `delta.content` can be `null` or `undefined`
2. **Handle finish_reason** — Know when stream ends
3. **Use flush** — `flush=True` in Python, no buffering
4. **Error handling** — Wrap in try/catch, stream can fail mid-response
5. **Abort controller** — Allow users to cancel streaming

```typescript
const controller = new AbortController();

// User clicks cancel
cancelButton.onclick = () => controller.abort();

try {
  const stream = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [...],
    stream: true
  }, { signal: controller.signal });

  for await (const chunk of stream) {
    // ...
  }
} catch (error) {
  if (error.name === "AbortError") {
    console.log("Stream cancelled");
  }
}
```
