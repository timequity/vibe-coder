# Cloudflare D1 Database

## Setup

### Create Database

```bash
# Create D1 database
wrangler d1 create my-db

# Output:
# [[d1_databases]]
# binding = "DB"
# database_name = "my-db"
# database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### wrangler.toml

```toml
name = "my-app"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### TypeScript Bindings

```typescript
type Bindings = {
  DB: D1Database
}

const app = new Hono<{ Bindings: Bindings }>()
```

## Schema & Migrations

### Create Schema File

```sql
-- schema.sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'active',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_items_user ON items(user_id);
CREATE INDEX idx_items_status ON items(status);
```

### Run Migration

```bash
# Local development
wrangler d1 execute my-db --local --file=./schema.sql

# Production
wrangler d1 execute my-db --file=./schema.sql
```

## Query Patterns

### SELECT

```typescript
// Single row
app.get('/users/:id', async (c) => {
  const id = c.req.param('id')
  const user = await c.env.DB
    .prepare('SELECT * FROM users WHERE id = ?')
    .bind(id)
    .first()

  if (!user) {
    return c.json({ error: 'Not found' }, 404)
  }
  return c.json(user)
})

// Multiple rows
app.get('/users', async (c) => {
  const { results } = await c.env.DB
    .prepare('SELECT * FROM users ORDER BY created_at DESC')
    .all()

  return c.json(results)
})

// With pagination
app.get('/items', async (c) => {
  const page = parseInt(c.req.query('page') || '1')
  const limit = 20
  const offset = (page - 1) * limit

  const { results } = await c.env.DB
    .prepare('SELECT * FROM items ORDER BY id DESC LIMIT ? OFFSET ?')
    .bind(limit, offset)
    .all()

  return c.json({ items: results, page })
})
```

### INSERT

```typescript
app.post('/users', async (c) => {
  const { email, name } = await c.req.json()

  const result = await c.env.DB
    .prepare('INSERT INTO users (email, name) VALUES (?, ?)')
    .bind(email, name)
    .run()

  return c.json({
    id: result.meta.last_row_id,
    email,
    name
  }, 201)
})

// With RETURNING (SQLite 3.35+)
app.post('/items', async (c) => {
  const { user_id, title, description } = await c.req.json()

  const item = await c.env.DB
    .prepare(`
      INSERT INTO items (user_id, title, description)
      VALUES (?, ?, ?)
      RETURNING *
    `)
    .bind(user_id, title, description)
    .first()

  return c.json(item, 201)
})
```

### UPDATE

```typescript
app.put('/items/:id', async (c) => {
  const id = c.req.param('id')
  const { title, description, status } = await c.req.json()

  const result = await c.env.DB
    .prepare(`
      UPDATE items
      SET title = ?, description = ?, status = ?
      WHERE id = ?
    `)
    .bind(title, description, status, id)
    .run()

  if (result.meta.changes === 0) {
    return c.json({ error: 'Not found' }, 404)
  }

  return c.json({ success: true })
})
```

### DELETE

```typescript
app.delete('/items/:id', async (c) => {
  const id = c.req.param('id')

  const result = await c.env.DB
    .prepare('DELETE FROM items WHERE id = ?')
    .bind(id)
    .run()

  if (result.meta.changes === 0) {
    return c.json({ error: 'Not found' }, 404)
  }

  return c.body(null, 204)
})
```

## Batch Operations

```typescript
// Multiple statements in one request
const results = await c.env.DB.batch([
  c.env.DB.prepare('SELECT COUNT(*) as count FROM users'),
  c.env.DB.prepare('SELECT COUNT(*) as count FROM items'),
])

const userCount = results[0].results[0].count
const itemCount = results[1].results[0].count
```

## Search

```typescript
app.get('/search', async (c) => {
  const q = c.req.query('q') || ''

  const { results } = await c.env.DB
    .prepare(`
      SELECT * FROM items
      WHERE title LIKE ? OR description LIKE ?
      ORDER BY created_at DESC
      LIMIT 50
    `)
    .bind(`%${q}%`, `%${q}%`)
    .all()

  return c.json(results)
})
```

## Transactions (Batch)

D1 uses batch for transaction-like behavior:

```typescript
app.post('/transfer', async (c) => {
  const { from_id, to_id, amount } = await c.req.json()

  try {
    await c.env.DB.batch([
      c.env.DB
        .prepare('UPDATE accounts SET balance = balance - ? WHERE id = ?')
        .bind(amount, from_id),
      c.env.DB
        .prepare('UPDATE accounts SET balance = balance + ? WHERE id = ?')
        .bind(amount, to_id),
    ])

    return c.json({ success: true })
  } catch (e) {
    return c.json({ error: 'Transfer failed' }, 500)
  }
})
```

## Free Tier Limits

| Resource | Limit |
|----------|-------|
| Reads | 5 million / day |
| Writes | 100,000 / day |
| Storage | 5 GB |
| Databases | 50 |
| Max DB size | 10 GB |

## Best Practices

1. **Use prepared statements** — Always use `.prepare()` with `.bind()` to prevent SQL injection
2. **Add indexes** — On columns used in WHERE, ORDER BY, JOIN
3. **Limit results** — Always use LIMIT, especially for user-facing queries
4. **Use batch** — Group related operations to reduce round-trips
5. **Handle errors** — D1 throws on constraint violations

```typescript
try {
  await c.env.DB.prepare('INSERT INTO users (email) VALUES (?)')
    .bind(email)
    .run()
} catch (e: any) {
  if (e.message.includes('UNIQUE constraint failed')) {
    return c.json({ error: 'Email already exists' }, 409)
  }
  throw e
}
```
