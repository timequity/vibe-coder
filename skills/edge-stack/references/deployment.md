# Deployment

## wrangler.toml

### Basic Configuration

```toml
name = "my-app"
main = "src/index.ts"
compatibility_date = "2024-01-01"

# D1 Database
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# KV Namespace (optional)
[[kv_namespaces]]
binding = "KV"
id = "xxxxxxxx"

# R2 Bucket (optional)
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

# Environment variables
[vars]
APP_ENV = "production"
```

### Environment-specific

```toml
name = "my-app"
main = "src/index.ts"
compatibility_date = "2024-01-01"

# Production (default)
[[d1_databases]]
binding = "DB"
database_name = "my-db-prod"
database_id = "prod-xxxx"

# Staging/Preview
[env.staging]
name = "my-app-staging"
[[env.staging.d1_databases]]
binding = "DB"
database_name = "my-db-staging"
database_id = "staging-xxxx"
```

## Commands

### Development

```bash
# Start local dev server
wrangler dev

# With local D1
wrangler dev --local --persist

# With remote D1 (careful!)
wrangler dev --remote
```

### Database

```bash
# Create database
wrangler d1 create my-db

# Run migration locally
wrangler d1 execute my-db --local --file=./schema.sql

# Run migration in production
wrangler d1 execute my-db --file=./schema.sql

# Interactive SQL
wrangler d1 execute my-db --command="SELECT * FROM users"

# Backup
wrangler d1 backup create my-db

# List backups
wrangler d1 backup list my-db
```

### Deploy

```bash
# Deploy to production
wrangler deploy

# Deploy to staging
wrangler deploy --env staging

# Tail logs
wrangler tail
```

## Secrets

```bash
# Set secret
wrangler secret put API_KEY
# (enter value interactively)

# List secrets
wrangler secret list

# Delete secret
wrangler secret delete API_KEY
```

Access in code:

```typescript
type Bindings = {
  DB: D1Database
  API_KEY: string  // Secret
}

app.get('/api', (c) => {
  const apiKey = c.env.API_KEY
  // Use secret...
})
```

## Custom Domains

### Via Dashboard

1. Go to Workers & Pages → your worker
2. Settings → Triggers → Custom Domains
3. Add domain (e.g., `api.example.com`)

### Via wrangler.toml

```toml
routes = [
  { pattern = "api.example.com/*", zone_name = "example.com" }
]
```

## GitHub Actions CI/CD

### .github/workflows/deploy.yml

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - run: pnpm install

      - name: Run migrations
        run: wrangler d1 execute my-db --file=./schema.sql
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}

      - name: Deploy
        run: wrangler deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### Get API Token

1. Go to Cloudflare Dashboard → Profile → API Tokens
2. Create Token → Edit Cloudflare Workers
3. Add to GitHub Secrets as `CLOUDFLARE_API_TOKEN`

## Project Structure

```
my-app/
├── src/
│   ├── index.ts          # Main app entry
│   ├── routes/
│   │   ├── api.ts        # API routes
│   │   └── pages.ts      # Page routes
│   ├── components/
│   │   ├── Layout.tsx    # Base layout
│   │   └── ui/           # UI components
│   └── lib/
│       └── db.ts         # Database helpers
├── schema.sql            # Database schema
├── wrangler.toml         # Cloudflare config
├── uno.config.ts         # UnoCSS config (if using build)
├── tsconfig.json
└── package.json
```

### package.json scripts

```json
{
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy",
    "db:migrate": "wrangler d1 execute my-db --file=./schema.sql",
    "db:migrate:local": "wrangler d1 execute my-db --local --file=./schema.sql",
    "db:studio": "wrangler d1 execute my-db --command=\".tables\"",
    "tail": "wrangler tail"
  }
}
```

## Cloudflare Pages (Alternative)

For apps with static assets:

```bash
# Create Pages project
pnpm create hono@latest my-app
# Select: cloudflare-pages
```

### wrangler.toml for Pages

```toml
name = "my-app"
pages_build_output_dir = "./dist"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "xxxxxxxx"
```

### Deploy Pages

```bash
# Build and deploy
wrangler pages deploy ./dist
```

## Monitoring

### Wrangler Tail

```bash
# Real-time logs
wrangler tail

# Filter errors
wrangler tail --status error

# JSON output
wrangler tail --format json
```

### Dashboard

- Workers & Pages → your worker → Analytics
- View requests, errors, CPU time
- Set up alerts for errors
