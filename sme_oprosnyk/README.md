# Business Questionnaire Platform

Full-stack bilingual (Russian + Uzbek) business questionnaire application.

- **Backend**: FastAPI + pandas + openpyxl
- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS

---

## Local development

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # edit FRONTEND_URL if needed
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # set VITE_API_URL=http://localhost:8000
npm run dev
# App available at http://localhost:5173
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /questions | All categories and questions |
| POST | /submissions | Save a completed questionnaire |
| GET | /download-responses | Download responses.xlsx |

---

## Editing questions

Edit `backend/app/data/questions.xlsx` (created automatically on first run):

| Column | Description |
|--------|-------------|
| category_id | Unique key, e.g. `trade` |
| category_ru | Category name in Russian |
| category_uz | Category name in Uzbek |
| category_icon | lucide-react icon name |
| question_id | Unique question key |
| question_text_ru | Question in Russian |
| question_text_uz | Question in Uzbek |
| question_type | `text`, `number`, `select`, `textarea`, `radio`, `checkbox` |
| options_ru | Semicolon-separated options (Russian) |
| options_uz | Semicolon-separated options (Uzbek) |

---

## Deployment

### Backend — Render

1. Push `backend/` to GitHub.
2. Create a new **Web Service** on Render.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add env var: `FRONTEND_URL=https://your-frontend.vercel.app`

### Backend — Railway

Same as Render; Railway auto-detects uvicorn.

### Frontend — Vercel

1. Push `frontend/` to GitHub.
2. Import project on Vercel.
3. Add env var: `VITE_API_URL=https://your-backend.onrender.com`
4. Framework preset: **Vite**. Build: `npm run build`. Output: `dist`.

---

## Environment variables

### Backend `.env`
```
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend `.env.local`
```
VITE_API_URL=https://your-backend.onrender.com
```
