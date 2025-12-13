# Hono Framework

## Project Setup

```bash
pnpm create hono@latest my-app
# Select: cloudflare-workers

cd my-app
pnpm install
```

## Type-Safe Bindings

```typescript
import { Hono } from 'hono'

// Define environment bindings
type Bindings = {
  DB: D1Database
  KV: KVNamespace
  BUCKET: R2Bucket
  API_KEY: string
}

// Type-safe app
const app = new Hono<{ Bindings: Bindings }>()

app.get('/', (c) => {
  // c.env is fully typed
  const db = c.env.DB
  const apiKey = c.env.API_KEY
  return c.text('Hello')
})

export default app
```

## Routing

```typescript
// Basic routes
app.get('/users', handler)
app.post('/users', handler)
app.put('/users/:id', handler)
app.delete('/users/:id', handler)

// Path parameters
app.get('/users/:id', (c) => {
  const id = c.req.param('id')
  return c.json({ id })
})

// Query parameters
app.get('/search', (c) => {
  const q = c.req.query('q')
  const page = c.req.query('page') || '1'
  return c.json({ q, page })
})

// Route groups
const api = new Hono()
api.get('/users', listUsers)
api.post('/users', createUser)

app.route('/api', api)
```

## Middleware

```typescript
import { cors } from 'hono/cors'
import { logger } from 'hono/logger'
import { secureHeaders } from 'hono/secure-headers'
import { compress } from 'hono/compress'

// Built-in middleware
app.use('*', logger())
app.use('*', secureHeaders())
app.use('*', compress())
app.use('/api/*', cors())

// Custom middleware
app.use('*', async (c, next) => {
  const start = Date.now()
  await next()
  const ms = Date.now() - start
  c.header('X-Response-Time', `${ms}ms`)
})

// Auth middleware
const auth = async (c, next) => {
  const token = c.req.header('Authorization')
  if (!token) {
    return c.json({ error: 'Unauthorized' }, 401)
  }
  // Verify token...
  await next()
}

app.use('/api/admin/*', auth)
```

## JSX Templates

```typescript
import { Hono } from 'hono'
import { html } from 'hono/html'

// Using html tagged template
app.get('/', (c) => {
  return c.html(html`
    <html>
      <body>
        <h1>Hello</h1>
      </body>
    </html>
  `)
})

// Using JSX (needs tsconfig adjustment)
// tsconfig.json: "jsx": "react-jsx", "jsxImportSource": "hono/jsx"

const Page = ({ title, children }: { title: string, children: any }) => (
  <html>
    <head><title>{title}</title></head>
    <body>{children}</body>
  </html>
)

app.get('/', (c) => {
  return c.html(
    <Page title="Home">
      <h1>Welcome</h1>
    </Page>
  )
})
```

## Request Handling

```typescript
// JSON body
app.post('/users', async (c) => {
  const body = await c.req.json()
  return c.json({ received: body })
})

// Form data
app.post('/upload', async (c) => {
  const body = await c.req.parseBody()
  const file = body['file']
  return c.json({ filename: file.name })
})

// Headers
app.get('/headers', (c) => {
  const userAgent = c.req.header('User-Agent')
  const custom = c.req.header('X-Custom-Header')
  return c.json({ userAgent, custom })
})
```

## Response Helpers

```typescript
// JSON
return c.json({ data: 'value' })
return c.json({ error: 'Not found' }, 404)

// HTML
return c.html('<h1>Hello</h1>')
return c.html(<Page>Content</Page>)

// Text
return c.text('Plain text')

// Redirect
return c.redirect('/new-location')
return c.redirect('/new-location', 301)

// Headers
c.header('X-Custom', 'value')
c.header('Cache-Control', 'max-age=3600')

// Status
return c.body(null, 204)
```

## Error Handling

```typescript
import { HTTPException } from 'hono/http-exception'

// Throw HTTP errors
app.get('/users/:id', async (c) => {
  const user = await getUser(c.req.param('id'))
  if (!user) {
    throw new HTTPException(404, { message: 'User not found' })
  }
  return c.json(user)
})

// Global error handler
app.onError((err, c) => {
  console.error(err)
  if (err instanceof HTTPException) {
    return c.json({ error: err.message }, err.status)
  }
  return c.json({ error: 'Internal Server Error' }, 500)
})

// 404 handler
app.notFound((c) => {
  return c.json({ error: 'Not Found' }, 404)
})
```

## Validation with Zod

```typescript
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const userSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().min(0).optional()
})

app.post(
  '/users',
  zValidator('json', userSchema),
  async (c) => {
    const data = c.req.valid('json')
    // data is typed as { name: string, email: string, age?: number }
    return c.json({ created: data })
  }
)
```

## Static Files (Pages)

```typescript
// For Cloudflare Pages with static assets
import { Hono } from 'hono'
import { serveStatic } from 'hono/cloudflare-pages'

const app = new Hono()

// Serve static files from /public
app.use('/static/*', serveStatic({ root: './' }))

// Or specific file
app.get('/favicon.ico', serveStatic({ path: './favicon.ico' }))
```
