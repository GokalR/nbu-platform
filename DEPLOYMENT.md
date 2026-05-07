# Deployment Runbook

How to push code, deploy to Railway / Cloudflare Pages, and manage R2 buckets for the NBU AI Hub.

---

## 1. Repository

- **Remote**: `https://github.com/GokalR/nbu-platform.git`
- **Default branch**: `main`
- **Backup branches** (do not delete): `backup/fergana-pre-cleanup`, `backup/pre-samarkand`, `backup/step5-before-refactor`

### Pushing changes

```bash
git status                       # check what's about to ship
git add <specific files>         # avoid `git add .` — easy to commit secrets
git commit -m "<imperative summary>"
git push origin main             # triggers Railway + Cloudflare auto-deploy
```

> **Never** push to `GokalR/testing` — that repo has >100 MB video files and blocks pushes.

### Pre-push checklist

1. `.env` files are gitignored. Verify nothing in `git status` looks like a secret.
2. `bff_frontend/frontend/dist/` is gitignored — Pages builds its own.
3. `cerr_runs/` is gitignored — that's 1.4 GB of scraped JSON, lives in R2.
4. Run `npm run build` locally if you touched the frontend, to catch Vite errors before Pages does.

---

## 2. Railway (backends)

Two Railway services run from this repo:

| Service | Root dir | Builder | Start |
|---|---|---|---|
| **bff-backend** (main API) | `bff_frontend/backend/` | Dockerfile | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **cerr-platform** (CERR mock) | `region_analytics_platform_template/platform/` | Buildpack | `python server.py` (Procfile) |

Both auto-deploy on push to `main`.

### bff-backend env vars

Set in Railway → Variables tab.

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | auto | Provided by Railway PostgreSQL addon |
| `APP_ENV` | `production` | |
| `CORS_ORIGINS` | `https://nbu-platform.pages.dev,https://<custom-domain>` | comma-separated |
| `SECRET_KEY` | random 32+ chars | JWT signing |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6-20250627` | **full ID** — short names 404 |
| `OPENAI_API_KEY` | `sk-proj-...` | for Business Plan + AI Advisor |
| `OPENAI_MODEL` | `gpt-4o` | Business Plan |
| `RAG_MODEL` | `gpt-5.1` | AI Advisor |
| `VECTOR_STORE_ID` | `vs_...` | OpenAI Vector Store w/ regional docs |
| `LLM_PROVIDER` | `claude` or `openai` | Business Plan toggle |
| `VIDEO_BASE_URL` | `https://nbu-videos.devgokal.com` | R2 public URL |
| `CERR_DATA_ROOT` | (unused on this service) | — |

> All env values get `.strip()` in Python because Railway sometimes appends a trailing `\n`.

### cerr-platform env vars

| Variable | Value |
|---|---|
| `CERR_DATA_ROOT` | `https://cerr-data.devgokal.com` |

### Health checks

- `bff-backend`: `GET /health` (configured in `railway.json`, 120s timeout)
- `cerr-platform`: served at root path

### Reading logs

Railway dashboard → service → Deploy logs. Or `railway logs -s bff-backend` if CLI is configured.

### Manual redeploy

Railway → service → Deployments → click latest → "Redeploy". Useful after env-var changes.

---

## 3. Cloudflare Pages (frontend)

| Setting | Value |
|---|---|
| Project name | `nbu-platform` |
| Production branch | `main` |
| Root directory | `bff_frontend/frontend` |
| Build command | `npm run build` |
| Build output | `dist` |
| Node version | 20 |

### Frontend env vars (Pages → Settings → Environment variables)

| Variable | Production value |
|---|---|
| `VITE_API_URL` | `https://<bff-backend>.up.railway.app` |
| `VITE_CERR_BUNDLE_URL` | `https://<cerr-platform>.up.railway.app` |
| `VITE_YANDEX_MAPS_API_KEY` | (Yandex Maps JS API key) |

Changing any `VITE_*` var requires a **rebuild** — Cloudflare offers a one-click "Retry deployment".

### SPA routing

`bff_frontend/frontend/dist/_redirects` handles SPA fallback:

```
/:path([^.]*)        /index.html        200
```

API calls do NOT go through Cloudflare proxy — `services/api.js` prepends `VITE_API_URL` directly to each `/api/*` request.

### Custom domain

Pages → Custom domains → Add. CNAME `nbu-platform.pages.dev`. SSL is auto.

---

## 4. Cloudflare R2 (object storage)

### Buckets

| Bucket | Public domain | Contents |
|---|---|---|
| `nbu-cerr-data` | `cerr-data.devgokal.com` | CERR scraped JSON (1.4 GB) |
| `nbu-edu-videos` | `nbu-videos.devgokal.com` | MP4 course videos + thumbnails |

### Uploading CERR data

Use [upload_to_r2.py](upload_to_r2.py) at the repo root:

```bash
export AWS_ACCESS_KEY_ID="<r2-access-key>"
export AWS_SECRET_ACCESS_KEY="<r2-secret>"
python upload_to_r2.py
```

The script is idempotent — it skips files already present at the same size, so it's safe to re-run after a network blip. Endpoint hardcoded to `https://ef8577cf87d4e1bcf38b212576d87ba2.r2.cloudflarestorage.com` (account ID baked in).

R2 credentials: Cloudflare dashboard → R2 → Manage R2 API Tokens. Use a token scoped to the specific bucket.

### Uploading videos

Same pattern, but bucket = `nbu-edu-videos`. No bundled script — use `aws s3 cp` with the R2 endpoint, or rclone.

### CORS for buckets

Public buckets need CORS allowing `GET` from the Pages domain. Set on bucket → Settings → CORS Policy.

---

## 5. PostgreSQL (Railway)

- Provisioned as a Railway add-on attached to `bff-backend`.
- `DATABASE_URL` is injected automatically.
- `bff_frontend/backend/app/main.py` runs `Base.metadata.create_all()` on startup — **only creates new tables, does not modify existing columns**.

### Schema changes (manual ALTER)

Connect via Railway's PostgreSQL public proxy (Connect tab → Public network):

```bash
psql "postgresql://postgres:<pwd>@<proxy-host>:<port>/railway"
```

Then run your `ALTER TABLE` / `CREATE INDEX` statements directly. Save the SQL alongside the code change so it's reproducible.

### Backups

Railway takes daily snapshots. To export manually: `pg_dump $DATABASE_URL > backup.sql`.

---

## 6. Putting it all together — typical deploy

```bash
# 1. Make changes locally, test
cd bff_frontend/backend && uvicorn app.main:app --reload  # in one terminal
cd bff_frontend/frontend && npm run dev                    # in another

# 2. Commit
git add bff_frontend/...
git commit -m "feat(rs): add zone heatmap to step 5"

# 3. Push — triggers BOTH Railway (backend) and Cloudflare Pages (frontend)
git push origin main

# 4. Watch deploys
#    Railway: dashboard → bff-backend → Deployments
#    Pages:   dashboard → nbu-platform → Deployments

# 5. Verify
curl https://<railway-url>/health           # backend up?
open https://nbu-platform.pages.dev         # frontend serving the new build?
```

---

## 7. Rollback

| Layer | How |
|---|---|
| Frontend | Pages → Deployments → previous deploy → "Rollback to this deployment" |
| Backend | Railway → Deployments → previous → "Redeploy" |
| Code | `git revert <sha> && git push` |
| Schema | manual `ALTER TABLE` to undo (no migration tool yet) |

---

## 8. Things that have bitten us

- **bcrypt 4.1+** breaks passlib. Pin to `4.0.1`.
- **`claude-sonnet-4-6`** (short ID) returns 404. Always use the full dated ID.
- **Railway env vars** can carry trailing newlines — `.strip()` defensively.
- **`create_all()`** silently ignores added columns. Always write an explicit `ALTER`.
- **Cloudflare Pages 200-rewrites to remote hosts** are rejected — that's why we proxy via `VITE_API_URL` instead of `_redirects`.
- **>100 MB files** in git break GitHub pushes. Keep videos and CERR JSON in R2.
