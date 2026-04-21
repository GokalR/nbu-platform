import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'

// Public maps under /maps/*/index.html hold a Yandex Maps API key. We keep the
// source file with a __YANDEX_MAPS_API_KEY__ placeholder so the real key never
// lands in git; this plugin replaces it in-flight (dev) and at copy-time (build).
function yandexMapKeyPlugin(apiKey) {
  const placeholder = '__YANDEX_MAPS_API_KEY__'
  const key = apiKey || ''
  return {
    name: 'rs-yandex-key',
    transformIndexHtml: {
      order: 'pre',
      handler: (html) => html.split(placeholder).join(key),
    },
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (!req.url || !req.url.includes('/maps/') || !req.url.includes('index.html')) return next()
        const rel = req.url.split('?')[0]
        const abs = path.join(server.config.publicDir, rel.replace(/^\/+/, ''))
        fs.readFile(abs, 'utf8', (err, src) => {
          if (err) return next()
          res.setHeader('Content-Type', 'text/html; charset=utf-8')
          res.end(src.split(placeholder).join(key))
        })
      })
    },
    closeBundle() {
      // Replace placeholder in copied public assets after build
      const outDir = path.resolve(process.cwd(), 'dist', 'maps')
      if (!fs.existsSync(outDir)) return
      const walk = (dir) => {
        for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
          const full = path.join(dir, entry.name)
          if (entry.isDirectory()) walk(full)
          else if (entry.isFile() && entry.name.endsWith('.html')) {
            const src = fs.readFileSync(full, 'utf8')
            if (src.includes(placeholder)) {
              fs.writeFileSync(full, src.split(placeholder).join(key))
            }
          }
        }
      }
      walk(outDir)
    },
  }
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const yandexKey = env.VITE_YANDEX_MAPS_API_KEY || ''
  return {
  plugins: [vue(), yandexMapKeyPlugin(yandexKey)],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'vue-i18n': 'vue-i18n/dist/vue-i18n.esm-bundler.js',
    },
  },
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
  test: {
    environment: 'happy-dom',
    globals: true,
  },
  build: {
    rollupOptions: {
      output: {
        chunkFileNames: (chunkInfo) => {
          const name = (chunkInfo.name || 'chunk').replace(/^_+/, '')
          return `assets/${name}-[hash].js`
        },
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const name = (assetInfo.name || 'asset').replace(/^_+/, '')
          return `assets/${name}-[hash][extname]`
        },
      },
    },
  },
  server: {
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
  }
})
