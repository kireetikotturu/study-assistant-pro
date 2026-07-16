# Study Assistant Pro

A full-stack AI study assistant with authentication, MongoDB Atlas storage, and a
Stripe-powered Free → Pro subscription upgrade. This is the "pro" evolution of the
original Gradio + Gemini Study Assistant.

- **Free plan:** 5 questions/day, "Friendly" persona (short, simple answers)
- **Pro plan:** unlimited questions, "Academic" persona (detailed, in-depth answers)

## Stack

| Layer     | Tech |
|-----------|------|
| Backend   | FastAPI, PostgreSQL on Neon (via SQLAlchemy async + asyncpg), JWT auth, Stripe (test mode), Gemini API |
| Frontend  | React (Vite), React Router, Axios |
| Auth      | Email/password signup & login, bcrypt-hashed passwords, JWT bearer tokens |
| Payments  | Stripe Checkout (subscription mode, test keys) |

## Project structure

```
study-assistant-pro/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── config.py            # env-based settings
│   │   ├── database.py          # SQLAlchemy engine, session, User ORM model
│   │   ├── models.py            # Pydantic request/response models
│   │   ├── auth.py               # password hashing + JWT
│   │   └── routes/
│   │       ├── auth_routes.py         # /auth/signup, /auth/login
│   │       ├── subscription_routes.py # /subscription/create-checkout-session, /webhook, /me
│   │       └── chat_routes.py         # /chat/ask (Gemini, persona-gated)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/ (Login, Signup, Chat, UpgradeSuccess, UpgradeCancelled)
    │   ├── AuthContext.jsx
    │   ├── ProtectedRoute.jsx
    │   ├── api.js
    │   └── App.jsx
    └── .env.example
```

## 1. Neon Postgres setup

1. Create a free account at https://neon.tech and create a new project
2. On the project dashboard, go to **Connection Details** and copy the connection string
3. Rewrite the `postgresql://` prefix to `postgresql+asyncpg://` (SQLAlchemy's async driver needs this),
   and make sure `?ssl=require` (or `?sslmode=require`) is appended
4. Paste it into `backend/.env` as `DATABASE_URL`
5. That's it — no manual table creation needed. The `users` table is created automatically the
   first time the FastAPI app starts (see `init_db()` in `app/database.py`)

## 2. Stripe test-mode setup

1. Sign up at https://dashboard.stripe.com (test mode is on by default)
2. Create a Product with a recurring monthly Price (e.g. $5/month) → copy the **Price ID** (`price_...`)
3. Copy your test **Secret key** (`sk_test_...`) from Developers → API keys
4. For webhooks locally, install the [Stripe CLI](https://stripe.com/docs/stripe-cli) and run:
   ```bash
   stripe listen --forward-to localhost:8000/subscription/webhook
   ```
   This prints a `whsec_...` signing secret — put it in `.env` as `STRIPE_WEBHOOK_SECRET`.
5. Test payments with Stripe's test card: `4242 4242 4242 4242`, any future expiry, any CVC.

## 3. Gemini API key

Get one free at https://aistudio.google.com/apikey

## 4. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in DATABASE_URL, STRIPE_*, GEMINI_API_KEY, JWT_SECRET_KEY
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for interactive Swagger API docs.

## 5. Frontend setup

```bash
cd frontend
npm install
cp .env.example .env           # VITE_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:5173`.

## How the subscription flow works

1. User clicks **Upgrade to Pro** → frontend calls `POST /subscription/create-checkout-session`
2. Backend creates (or reuses) a Stripe Customer, creates a Checkout Session, returns the `checkout_url`
3. Frontend redirects the browser to Stripe's hosted checkout page
4. User pays with a test card → Stripe redirects back to `/upgrade-success`
5. In the background, Stripe sends a `checkout.session.completed` webhook event to
   `POST /subscription/webhook`, which flips the user's `plan` to `"pro"` in Postgres
6. If the user later cancels their subscription in Stripe, a `customer.subscription.deleted`
   webhook event flips them back to `"free"`

## Notes for interviews / resume

- Passwords are never stored in plain text — `passlib[bcrypt]` hashes them before insert
- JWTs are signed with `python-jose` and verified on every protected route via a FastAPI dependency
- Stripe webhook signatures are verified (`stripe.Webhook.construct_event`) so the plan can't be
  spoofed by hitting the webhook URL directly
- Free-tier rate limiting is tracked per-user per-day directly on the `users` row (no extra infra needed)
- The `users` table is a real relational schema (SQLAlchemy ORM model) — a natural jumping-off point
  to talk about normalization, indexing (`email` is indexed + unique), and why a foreign key to a
  separate `subscriptions` table would be the next iteration for a production system
