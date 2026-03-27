# Multi-Stock Frontend (Vercel)

This folder contains the standalone Next.js frontend used for live demo deployment on Vercel.

## What this frontend uses

- Framework: Next.js 14
- Styling: Tailwind CSS
- Data source: `public/data/frontend_data.json`
- Cart and checkout state: browser localStorage
- No backend API required for demo mode

## Local run

```bash
npm install
npm run dev
```

Open http://localhost:3000 (or the next free port shown by Next.js).

## Build check

```bash
npm run build
```

## Vercel deploy

1. Push repository to GitHub.
2. Import the repository in Vercel.
3. Set Root Directory to `frontend-vercel`.
4. Deploy.

No Render setup is required for this demo frontend.
