// vite.config.js
import { defineConfig } from "file:///mnt/c/Users/User/Downloads/Projects/NBU/NBU_analytics/frontend/node_modules/vite/dist/node/index.js";
import vue from "file:///mnt/c/Users/User/Downloads/Projects/NBU/NBU_analytics/frontend/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { fileURLToPath, URL } from "node:url";
var __vite_injected_original_import_meta_url = "file:///mnt/c/Users/User/Downloads/Projects/NBU/NBU_analytics/frontend/vite.config.js";
var vite_config_default = defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", __vite_injected_original_import_meta_url)),
      "vue-i18n": "vue-i18n/dist/vue-i18n.esm-bundler.js"
    }
  },
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false
  },
  build: {
    rollupOptions: {
      output: {
        chunkFileNames: (chunkInfo) => {
          const name = (chunkInfo.name || "chunk").replace(/^_+/, "");
          return `assets/${name}-[hash].js`;
        },
        entryFileNames: "assets/[name]-[hash].js",
        assetFileNames: (assetInfo) => {
          const name = (assetInfo.name || "asset").replace(/^_+/, "");
          return `assets/${name}-[hash][extname]`;
        }
      }
    }
  },
  server: {
    port: 5173,
    open: true
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvbW50L2MvVXNlcnMvVXNlci9Eb3dubG9hZHMvUHJvamVjdHMvTkJVL05CVV9hbmFseXRpY3MvZnJvbnRlbmRcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIi9tbnQvYy9Vc2Vycy9Vc2VyL0Rvd25sb2Fkcy9Qcm9qZWN0cy9OQlUvTkJVX2FuYWx5dGljcy9mcm9udGVuZC92aXRlLmNvbmZpZy5qc1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vbW50L2MvVXNlcnMvVXNlci9Eb3dubG9hZHMvUHJvamVjdHMvTkJVL05CVV9hbmFseXRpY3MvZnJvbnRlbmQvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJ1xuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXG5pbXBvcnQgeyBmaWxlVVJMVG9QYXRoLCBVUkwgfSBmcm9tICdub2RlOnVybCdcblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW3Z1ZSgpXSxcbiAgcmVzb2x2ZToge1xuICAgIGFsaWFzOiB7XG4gICAgICAnQCc6IGZpbGVVUkxUb1BhdGgobmV3IFVSTCgnLi9zcmMnLCBpbXBvcnQubWV0YS51cmwpKSxcbiAgICAgICd2dWUtaTE4bic6ICd2dWUtaTE4bi9kaXN0L3Z1ZS1pMThuLmVzbS1idW5kbGVyLmpzJyxcbiAgICB9LFxuICB9LFxuICBkZWZpbmU6IHtcbiAgICBfX1ZVRV9JMThOX0ZVTExfSU5TVEFMTF9fOiB0cnVlLFxuICAgIF9fVlVFX0kxOE5fTEVHQUNZX0FQSV9fOiBmYWxzZSxcbiAgICBfX0lOVExJRllfUFJPRF9ERVZUT09MU19fOiBmYWxzZSxcbiAgfSxcbiAgYnVpbGQ6IHtcbiAgICByb2xsdXBPcHRpb25zOiB7XG4gICAgICBvdXRwdXQ6IHtcbiAgICAgICAgY2h1bmtGaWxlTmFtZXM6IChjaHVua0luZm8pID0+IHtcbiAgICAgICAgICBjb25zdCBuYW1lID0gKGNodW5rSW5mby5uYW1lIHx8ICdjaHVuaycpLnJlcGxhY2UoL15fKy8sICcnKVxuICAgICAgICAgIHJldHVybiBgYXNzZXRzLyR7bmFtZX0tW2hhc2hdLmpzYFxuICAgICAgICB9LFxuICAgICAgICBlbnRyeUZpbGVOYW1lczogJ2Fzc2V0cy9bbmFtZV0tW2hhc2hdLmpzJyxcbiAgICAgICAgYXNzZXRGaWxlTmFtZXM6IChhc3NldEluZm8pID0+IHtcbiAgICAgICAgICBjb25zdCBuYW1lID0gKGFzc2V0SW5mby5uYW1lIHx8ICdhc3NldCcpLnJlcGxhY2UoL15fKy8sICcnKVxuICAgICAgICAgIHJldHVybiBgYXNzZXRzLyR7bmFtZX0tW2hhc2hdW2V4dG5hbWVdYFxuICAgICAgICB9LFxuICAgICAgfSxcbiAgICB9LFxuICB9LFxuICBzZXJ2ZXI6IHtcbiAgICBwb3J0OiA1MTczLFxuICAgIG9wZW46IHRydWUsXG4gIH0sXG59KVxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUErVyxTQUFTLG9CQUFvQjtBQUM1WSxPQUFPLFNBQVM7QUFDaEIsU0FBUyxlQUFlLFdBQVc7QUFGbU0sSUFBTSwyQ0FBMkM7QUFJdlIsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUyxDQUFDLElBQUksQ0FBQztBQUFBLEVBQ2YsU0FBUztBQUFBLElBQ1AsT0FBTztBQUFBLE1BQ0wsS0FBSyxjQUFjLElBQUksSUFBSSxTQUFTLHdDQUFlLENBQUM7QUFBQSxNQUNwRCxZQUFZO0FBQUEsSUFDZDtBQUFBLEVBQ0Y7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLDJCQUEyQjtBQUFBLElBQzNCLHlCQUF5QjtBQUFBLElBQ3pCLDJCQUEyQjtBQUFBLEVBQzdCO0FBQUEsRUFDQSxPQUFPO0FBQUEsSUFDTCxlQUFlO0FBQUEsTUFDYixRQUFRO0FBQUEsUUFDTixnQkFBZ0IsQ0FBQyxjQUFjO0FBQzdCLGdCQUFNLFFBQVEsVUFBVSxRQUFRLFNBQVMsUUFBUSxPQUFPLEVBQUU7QUFDMUQsaUJBQU8sVUFBVSxJQUFJO0FBQUEsUUFDdkI7QUFBQSxRQUNBLGdCQUFnQjtBQUFBLFFBQ2hCLGdCQUFnQixDQUFDLGNBQWM7QUFDN0IsZ0JBQU0sUUFBUSxVQUFVLFFBQVEsU0FBUyxRQUFRLE9BQU8sRUFBRTtBQUMxRCxpQkFBTyxVQUFVLElBQUk7QUFBQSxRQUN2QjtBQUFBLE1BQ0Y7QUFBQSxJQUNGO0FBQUEsRUFDRjtBQUFBLEVBQ0EsUUFBUTtBQUFBLElBQ04sTUFBTTtBQUFBLElBQ04sTUFBTTtBQUFBLEVBQ1I7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
