# htmx with Hono

## Setup

```html
<!-- In your layout -->
<script src="https://unpkg.com/htmx.org@2.0.4"></script>
```

## Core Pattern: Return HTML Fragments

htmx expects **HTML responses**, not JSON.

```typescript
// ❌ Wrong - JSON response
app.get('/api/users', async (c) => {
  const users = await getUsers()
  return c.json(users)  // htmx can't use this
})

// ✅ Correct - HTML fragment
app.get('/api/users', async (c) => {
  const users = await getUsers()
  return c.html(
    <ul>
      {users.map(u => <li>{u.name}</li>)}
    </ul>
  )
})
```

## Basic Interactions

### Click to Load

```typescript
// Button triggers GET, response replaces #content
app.get('/', (c) => c.html(
  <div>
    <button hx-get="/items" hx-target="#content">
      Load Items
    </button>
    <div id="content"></div>
  </div>
))

app.get('/items', async (c) => {
  const items = await getItems(c.env.DB)
  return c.html(
    <ul>
      {items.map(i => <li>{i.name}</li>)}
    </ul>
  )
})
```

### Form Submit

```typescript
app.get('/', (c) => c.html(
  <form hx-post="/users" hx-target="#result" hx-swap="innerHTML">
    <input name="name" placeholder="Name" required />
    <input name="email" type="email" placeholder="Email" required />
    <button type="submit">Create</button>
  </form>
  <div id="result"></div>
))

app.post('/users', async (c) => {
  const { name, email } = await c.req.parseBody()
  await c.env.DB
    .prepare('INSERT INTO users (name, email) VALUES (?, ?)')
    .bind(name, email)
    .run()

  return c.html(
    <div class="text-green-600">
      User {name} created successfully!
    </div>
  )
})
```

## Search with Debounce

```typescript
app.get('/', (c) => c.html(
  <div>
    <input
      type="search"
      name="q"
      placeholder="Search..."
      hx-get="/search"
      hx-trigger="input changed delay:300ms"
      hx-target="#results"
    />
    <div id="results"></div>
  </div>
))

app.get('/search', async (c) => {
  const q = c.req.query('q') || ''
  const { results } = await c.env.DB
    .prepare('SELECT * FROM items WHERE name LIKE ?')
    .bind(`%${q}%`)
    .all()

  return c.html(
    <ul>
      {results.map((item: any) => (
        <li>{item.name}</li>
      ))}
    </ul>
  )
})
```

## Infinite Scroll / Load More

```typescript
app.get('/items', async (c) => {
  const page = parseInt(c.req.query('page') || '1')
  const limit = 10
  const offset = (page - 1) * limit

  const { results } = await c.env.DB
    .prepare('SELECT * FROM items LIMIT ? OFFSET ?')
    .bind(limit, offset)
    .all()

  const hasMore = results.length === limit

  return c.html(
    <>
      {results.map((item: any) => (
        <div class="item">{item.name}</div>
      ))}
      {hasMore && (
        <button
          hx-get={`/items?page=${page + 1}`}
          hx-target="this"
          hx-swap="outerHTML"
        >
          Load More
        </button>
      )}
    </>
  )
})
```

## Delete with Confirmation

```typescript
// Item with delete button
const ItemRow = ({ item }: { item: any }) => (
  <tr id={`item-${item.id}`}>
    <td>{item.name}</td>
    <td>
      <button
        hx-delete={`/items/${item.id}`}
        hx-target={`#item-${item.id}`}
        hx-swap="outerHTML"
        hx-confirm="Are you sure?"
        class="text-red-500"
      >
        Delete
      </button>
    </td>
  </tr>
)

app.delete('/items/:id', async (c) => {
  const id = c.req.param('id')
  await c.env.DB
    .prepare('DELETE FROM items WHERE id = ?')
    .bind(id)
    .run()

  // Return empty to remove the row
  return c.body(null, 200)
})
```

## Inline Edit

```typescript
// Display mode
const ItemDisplay = ({ item }: { item: any }) => (
  <div id={`item-${item.id}`}>
    <span>{item.name}</span>
    <button
      hx-get={`/items/${item.id}/edit`}
      hx-target={`#item-${item.id}`}
      hx-swap="outerHTML"
    >
      Edit
    </button>
  </div>
)

// Edit mode
app.get('/items/:id/edit', async (c) => {
  const id = c.req.param('id')
  const item = await getItem(c.env.DB, id)

  return c.html(
    <form
      id={`item-${item.id}`}
      hx-put={`/items/${item.id}`}
      hx-target={`#item-${item.id}`}
      hx-swap="outerHTML"
    >
      <input name="name" value={item.name} />
      <button type="submit">Save</button>
      <button
        type="button"
        hx-get={`/items/${item.id}`}
        hx-target={`#item-${item.id}`}
        hx-swap="outerHTML"
      >
        Cancel
      </button>
    </form>
  )
})

app.put('/items/:id', async (c) => {
  const id = c.req.param('id')
  const { name } = await c.req.parseBody()
  await c.env.DB
    .prepare('UPDATE items SET name = ? WHERE id = ?')
    .bind(name, id)
    .run()

  const item = await getItem(c.env.DB, id)
  return c.html(<ItemDisplay item={item} />)
})
```

## Out-of-Band Swaps

Update multiple elements from one response:

```typescript
app.post('/items', async (c) => {
  const { name } = await c.req.parseBody()
  await c.env.DB
    .prepare('INSERT INTO items (name) VALUES (?)')
    .bind(name)
    .run()

  const count = await getItemCount(c.env.DB)

  return c.html(
    <>
      {/* Main response */}
      <div class="text-green-600">Item created!</div>

      {/* Out-of-band update */}
      <span id="item-count" hx-swap-oob="true">
        {count} items
      </span>
    </>
  )
})
```

## Detect htmx Requests

```typescript
app.get('/items', async (c) => {
  const isHtmx = c.req.header('HX-Request') === 'true'
  const items = await getItems(c.env.DB)

  if (isHtmx) {
    // Return fragment only
    return c.html(
      <ul>
        {items.map(i => <li>{i.name}</li>)}
      </ul>
    )
  }

  // Full page for direct navigation
  return c.html(
    <Layout>
      <h1>Items</h1>
      <ul>
        {items.map(i => <li>{i.name}</li>)}
      </ul>
    </Layout>
  )
})
```

## Loading States

```typescript
// Automatic loading indicator
<button hx-get="/slow" hx-indicator="#spinner">
  Load
</button>
<span id="spinner" class="htmx-indicator">Loading...</span>

// CSS
<style>
  .htmx-indicator { display: none; }
  .htmx-request .htmx-indicator { display: inline; }
  .htmx-request.htmx-indicator { display: inline; }
</style>
```

## Key Attributes Reference

| Attribute | Description |
|-----------|-------------|
| `hx-get` | GET request to URL |
| `hx-post` | POST request |
| `hx-put` | PUT request |
| `hx-delete` | DELETE request |
| `hx-target` | CSS selector for response target |
| `hx-swap` | How to swap: innerHTML, outerHTML, beforeend, etc |
| `hx-trigger` | Event that triggers request |
| `hx-confirm` | Confirmation dialog |
| `hx-indicator` | Loading indicator element |
| `hx-push-url` | Push URL to history |
| `hx-swap-oob` | Out-of-band swap |
