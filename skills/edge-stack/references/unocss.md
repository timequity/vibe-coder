# UnoCSS Setup

## Options

### 1. CDN Runtime (Simplest)

No build step, instant development:

```html
<script src="https://cdn.jsdelivr.net/npm/@unocss/runtime"></script>
```

Works immediately with Tailwind-like classes:

```html
<div class="text-2xl font-bold text-blue-500 p-4 rounded-lg shadow">
  Hello World
</div>
```

### 2. Build-time Generation (Production)

Better performance, smaller bundles.

```bash
pnpm add -D unocss @unocss/preset-uno @unocss/preset-icons
```

#### uno.config.ts

```typescript
import { defineConfig, presetUno, presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetIcons({
      scale: 1.2,
      cdn: 'https://esm.sh/'
    })
  ],
  shortcuts: {
    'btn': 'px-4 py-2 rounded-lg font-medium transition-colors',
    'btn-primary': 'btn bg-blue-500 text-white hover:bg-blue-600',
    'btn-secondary': 'btn bg-gray-200 text-gray-800 hover:bg-gray-300',
    'input-base': 'px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none',
    'card': 'bg-white rounded-lg shadow-md p-4',
  },
  theme: {
    colors: {
      brand: {
        50: '#eff6ff',
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
      }
    }
  }
})
```

### 3. Server-Side Generation

Generate CSS at request time:

```typescript
import { createGenerator } from '@unocss/core'
import presetUno from '@unocss/preset-uno'

const uno = createGenerator({
  presets: [presetUno()]
})

// In your Hono middleware
app.use('*', async (c, next) => {
  await next()

  // Only process HTML responses
  const contentType = c.res.headers.get('Content-Type')
  if (!contentType?.includes('text/html')) return

  const html = await c.res.text()
  const { css } = await uno.generate(html)

  const newHtml = html.replace(
    '</head>',
    `<style>${css}</style></head>`
  )

  return c.html(newHtml)
})
```

## Common Utilities

### Layout

```html
<!-- Flexbox -->
<div class="flex items-center justify-between gap-4">
<div class="flex flex-col">

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">

<!-- Container -->
<div class="container mx-auto px-4">
```

### Spacing

```html
<!-- Padding -->
<div class="p-4">        <!-- all sides -->
<div class="px-4 py-2">  <!-- horizontal/vertical -->
<div class="pt-4 pb-2">  <!-- top/bottom -->

<!-- Margin -->
<div class="m-4">
<div class="mx-auto">    <!-- center horizontally -->
<div class="mt-4 mb-2">
```

### Typography

```html
<h1 class="text-3xl font-bold">
<p class="text-gray-600 text-sm">
<span class="font-medium text-blue-500">
<p class="leading-relaxed">
```

### Colors

```html
<!-- Text -->
<span class="text-gray-900">
<span class="text-blue-500">

<!-- Background -->
<div class="bg-white">
<div class="bg-gray-100">
<div class="bg-blue-500">

<!-- Border -->
<div class="border border-gray-200">
<div class="border-2 border-blue-500">
```

### Sizing

```html
<div class="w-full">
<div class="w-1/2">
<div class="w-64">       <!-- 16rem -->
<div class="max-w-md">
<div class="h-screen">
<div class="min-h-[200px]">
```

### Effects

```html
<!-- Shadows -->
<div class="shadow">
<div class="shadow-md">
<div class="shadow-lg">

<!-- Rounded -->
<div class="rounded">
<div class="rounded-lg">
<div class="rounded-full">

<!-- Opacity -->
<div class="opacity-50">
```

### Responsive

```html
<!-- Mobile first -->
<div class="w-full md:w-1/2 lg:w-1/3">
<div class="text-sm md:text-base lg:text-lg">
<div class="hidden md:block">
<div class="block md:hidden">
```

### States

```html
<!-- Hover -->
<button class="bg-blue-500 hover:bg-blue-600">

<!-- Focus -->
<input class="focus:ring-2 focus:ring-blue-500">

<!-- Active -->
<button class="active:scale-95">

<!-- Disabled -->
<button class="disabled:opacity-50 disabled:cursor-not-allowed">
```

## Icons (with @unocss/preset-icons)

```typescript
// uno.config.ts
import { presetIcons } from 'unocss'

export default defineConfig({
  presets: [
    presetIcons({
      scale: 1.2,
      cdn: 'https://esm.sh/'
    })
  ]
})
```

```html
<!-- Usage: i-{collection}-{icon} -->
<span class="i-lucide-search"></span>
<span class="i-lucide-user"></span>
<span class="i-lucide-settings"></span>
<span class="i-mdi-github"></span>

<!-- With size and color -->
<span class="i-lucide-check text-green-500 text-2xl"></span>
```

Browse icons: https://icones.js.org/

## Custom Shortcuts

```typescript
// uno.config.ts
export default defineConfig({
  shortcuts: {
    // Components
    'btn': 'px-4 py-2 rounded-lg font-medium transition-colors cursor-pointer',
    'btn-primary': 'btn bg-blue-500 text-white hover:bg-blue-600',
    'btn-danger': 'btn bg-red-500 text-white hover:bg-red-600',

    // Form
    'input': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none',
    'label': 'block text-sm font-medium text-gray-700 mb-1',

    // Layout
    'card': 'bg-white rounded-lg shadow-md p-6',
    'page': 'min-h-screen bg-gray-50 py-8',
    'container-sm': 'max-w-2xl mx-auto px-4',
  }
})
```

Usage:

```html
<div class="page">
  <div class="container-sm">
    <div class="card">
      <label class="label">Email</label>
      <input class="input" type="email" />
      <button class="btn-primary mt-4">Submit</button>
    </div>
  </div>
</div>
```
