# Node.js SDK

## Installation

```bash
npm install openai
# or
yarn add openai
# or
pnpm add openai
```

## Client Initialization

```typescript
import OpenAI from "openai";

// From environment (recommended)
const client = new OpenAI();

// Explicit config
const client = new OpenAI({
  apiKey: "sk-...",
  organization: "org-...",
  project: "proj-...",
  timeout: 60000,  // ms
  maxRetries: 3
});
```

## Chat Completions

### Basic
```typescript
const response = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [
    { role: "system", content: "You are helpful." },
    { role: "user", content: "Hello!" }
  ]
});

console.log(response.choices[0].message.content);
```

### With Parameters
```typescript
const response = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Write a haiku" }],
  temperature: 0.7,
  max_tokens: 100,
  top_p: 1,
  frequency_penalty: 0,
  presence_penalty: 0
});
```

### JSON Mode
```typescript
const response = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "List 3 colors as JSON" }],
  response_format: { type: "json_object" }
});

const data = JSON.parse(response.choices[0].message.content!);
```

## Tool Calling

```typescript
const tools: OpenAI.ChatCompletionTool[] = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get weather for location",
      parameters: {
        type: "object",
        properties: {
          location: { type: "string" }
        },
        required: ["location"]
      }
    }
  }
];

const response = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Weather in Paris?" }],
  tools
});

const toolCalls = response.choices[0].message.tool_calls;
if (toolCalls) {
  const args = JSON.parse(toolCalls[0].function.arguments);
  // Execute function, continue conversation
}
```

## Embeddings

```typescript
const response = await client.embeddings.create({
  model: "text-embedding-3-small",
  input: "Hello world"
});

const vector = response.data[0].embedding;

// Multiple inputs
const response = await client.embeddings.create({
  model: "text-embedding-3-small",
  input: ["Text 1", "Text 2", "Text 3"]
});
```

## Images

### Generation
```typescript
const response = await client.images.generate({
  model: "dall-e-3",
  prompt: "A futuristic city",
  size: "1024x1024",
  quality: "standard",
  n: 1
});

const imageUrl = response.data[0].url;
```

## Audio

### Transcription
```typescript
import fs from "fs";

const transcript = await client.audio.transcriptions.create({
  model: "whisper-1",
  file: fs.createReadStream("audio.mp3")
});

console.log(transcript.text);
```

### Text-to-Speech
```typescript
const response = await client.audio.speech.create({
  model: "tts-1",
  voice: "alloy",
  input: "Hello, world!"
});

const buffer = Buffer.from(await response.arrayBuffer());
fs.writeFileSync("output.mp3", buffer);
```

## Error Handling

```typescript
import OpenAI, {
  APIError,
  APIConnectionError,
  RateLimitError,
  AuthenticationError,
  BadRequestError
} from "openai";

try {
  const response = await client.chat.completions.create({...});
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log("Invalid API key");
  } else if (error instanceof RateLimitError) {
    console.log("Rate limited - retry with backoff");
  } else if (error instanceof BadRequestError) {
    console.log(`Bad request: ${error.message}`);
  } else if (error instanceof APIConnectionError) {
    console.log("Connection failed");
  } else if (error instanceof APIError) {
    console.log(`API error ${error.status}: ${error.message}`);
  }
}
```

## TypeScript Types

```typescript
import OpenAI from "openai";

// Message types
type Message = OpenAI.ChatCompletionMessageParam;
type SystemMessage = OpenAI.ChatCompletionSystemMessageParam;
type UserMessage = OpenAI.ChatCompletionUserMessageParam;

// Response types
type ChatCompletion = OpenAI.ChatCompletion;
type Choice = OpenAI.ChatCompletion.Choice;

// Building messages
const messages: Message[] = [
  { role: "system", content: "You are helpful" },
  { role: "user", content: "Hi" }
];
```

## Edge Runtime (Vercel, Cloudflare)

```typescript
// Works in edge runtimes
import OpenAI from "openai";

export const runtime = "edge";

export async function POST(req: Request) {
  const client = new OpenAI();

  const response = await client.chat.completions.create({
    model: "gpt-4o",
    messages: [{ role: "user", content: "Hello" }]
  });

  return Response.json(response);
}
```

## Response Objects

```typescript
const response = await client.chat.completions.create({...});

// Access fields
response.id;           // "chatcmpl-xxx"
response.model;        // "gpt-4o-2024-08-06"
response.created;      // Unix timestamp
response.choices;      // Choice[]
response.usage?.prompt_tokens;
response.usage?.completion_tokens;
response.usage?.total_tokens;

// First choice
const choice = response.choices[0];
choice.message.role;      // "assistant"
choice.message.content;   // Response text (nullable)
choice.finish_reason;     // "stop" | "length" | "tool_calls"
```
