# ReceivX — Real-Time MSME Receivables Intelligence

> **Tagline:** Get ahead of delayed payments before they become working-capital problems.

ReceivX is a full-stack financial technology application built from the ground up to solve the liquidity squeeze faced by Indian Micro, Small, and Medium Enterprises (MSMEs). By connecting invoice tracking with a deterministic delay risk engine, automated lifecycle event tracking, and simulated TReDS invoice discounting, ReceivX unlocks real-time visibility into working capital health.

---

## 🌟 Live Demo & Repositories

- **Live Production URL:** [https://receivx.vercel.app](https://receivx.vercel.app)
- **API Health Endpoint:** [https://receivx.vercel.app/api/health](https://receivx.vercel.app/api/health)
- **GitHub Repository:** [https://github.com/atharvanavgire10/receivx](https://github.com/atharvanavgire10/receivx)
- **Architecture Overview:** [https://receivx.vercel.app/architecture](https://receivx.vercel.app/architecture)

---

## 💡 Real-World Problem

In India's manufacturing and supply chain economy, MSMEs are standardly subject to 30–60 day credit terms. In practice, buyer payment delays routinely stretch to 75–120+ days. This locks vital working capital, strains payroll and vendor commitments, and risks operational paralysis. MSMEs often discover payment issues only after invoices become severely delinquent.

---

## 🚀 The Solution

ReceivX empowers MSME business owners and credit managers to:
1. **Track Invoices & Receivables:** Full lifecycle monitoring from issuance to settlement.
2. **Predict & Detect Delays in Real Time:** A rule-based risk engine scores invoices 0–100 with clear, human-readable explanations.
3. **Simulate Institutional Financing (TReDS):** Seamlessly evaluate invoice discounting options (10.4%–11.1% APR) to bridge cash-flow gaps.
4. **Audit Complete Lifecycles:** Immutable event stream tracking every invoice transition with timestamps.
5. **Interactive Recruiter Demo:** Experience a complete 10-step lifecycle progression in 20–30 seconds with a single click.

---

## 🏗️ Architecture

```
                  ┌─────────────────────────────────────┐
                  │    React 19 + Vite (Frontend)       │
                  └──────────────────┬──────────────────┘
                                     │ HTTPS
                                     ▼
                  ┌─────────────────────────────────────┐
                  │        Vercel Edge Network          │
                  │   (/api/* rewritten to index.py)    │
                  └──────────────────┬──────────────────┘
                                     │ WSGI / Serverless
                                     ▼
                  ┌─────────────────────────────────────┐
                  │    Flask Python 3.14 API Service    │
                  └───────┬─────────────────────┬───────┘
                          │                     │
                          ▼                     ▼
             ┌──────────────────────┐  ┌───────────────────┐
             │ Deterministic Risk   │  │ Simulation Engine │
             │ Engine (rules.py)    │  │ (simulation.py)   │
             └──────────┬───────────┘  └────────┬──────────┘
                        │                       │
                        └───────────┬───────────┘
                                    │ SQLAlchemy 2.0
                                    ▼
                  ┌─────────────────────────────────────┐
                  │  PostgreSQL (Vercel Postgres) /     │
                  │  Fallback Storage Engine            │
                  └─────────────────────────────────────┘
```

### Architecture Highlights:
- **Unified Single-Project Deployment:** React/Vite SPA and Python Flask serverless functions live in a single repository and deploy as one Vercel project.
- **Zero Heavy Infrastructure:** No persistent Redis, Celery, Kafka, or WebSockets required. Real-time reactivity is achieved via **Database Events + API Simulation + Frontend Polling**.
- **Transparent & Testable:** Pure Python deterministic rules instead of black-box AI/LLM hallucinations.

---

## 🛠️ Tech Stack

| Layer | Technology | Rationale |
|---|---|---|
| **Frontend** | React 19, React Router 7, Vite 6 | Lightning-fast build times, modern hooks, declarative routing |
| **Styling** | Vanilla CSS (Custom Design System) | Zero Tailwind bloat; bespoke dark-mode fintech UI |
| **Backend** | Python 3.14, Flask 3.1, Flask-CORS | Lightweight serverless micro-framework running on Vercel |
| **ORM / Data** | SQLAlchemy 2.0, psycopg 3.3 | Enterprise-grade SQL abstraction with connection pooling |
| **Database** | PostgreSQL (Vercel-compatible) | Relational integrity for financial accounts and audit events |
| **Testing** | Pytest 9.1 | Automated test suite covering models, risk rules, and API endpoints |
| **Deployment**| Vercel | Single-URL unified edge deployment |

---

## 📊 Database Schema

1. **`companies`**: MSME company profile (`id`, `name`, `industry`, `created_at`).
2. **`buyers`**: Corporate buyers (`id`, `company_id`, `name`, `industry`, `payment_terms_days`, `average_delay_days`, `reliability_score`, `created_at`).
3. **`invoices`**: Financial receivables (`id`, `company_id`, `buyer_id`, `invoice_number`, `amount`, `issued_at`, `due_at`, `status`, `risk_score`, `risk_level`, `created_at`).
   - *Statuses:* `DRAFT`, `ISSUED`, `ACCEPTED`, `DUE`, `OVERDUE`, `DISPUTED`, `PAID`.
4. **`payments`**: Payment transactions (`id`, `invoice_id`, `amount`, `payment_date`, `status`, `reference`).
5. **`invoice_events`**: Audit and lifecycle stream (`id`, `invoice_id`, `event_type`, `message`, `metadata`, `created_at`).
6. **`financing_requests`**: TReDS bids and factoring status (`id`, `invoice_id`, `status`, `financier`, `discount_rate`, `settlement_amount`, `created_at`).

---

## ⚙️ Deterministic Risk Engine

Risk scores range from **0 to 100**, categorized into four distinct levels:
- `0–29`: **LOW**
- `30–59`: **MEDIUM**
- `60–79`: **HIGH**
- `80–100`: **CRITICAL**

### Scoring Factors:
1. **Buyer Historical Delay:** Up to +30 points based on average past settlement lag.
2. **Maturity / Overdue Window:** Up to +25 points as due date approaches or passes.
3. **Invoice Exposure Size:** Up to +15 points for large exposures (>₹5L / >₹8L).
4. **Buyer Reliability Rating:** Up to +20 points when past payment reliability drops.
5. **Concurrent Overdue Invoices:** Up to +15 points if the buyer has other unpaid delinquent invoices.

Every calculated score returns explicit human-readable reasons (e.g., *"Buyer historically pays 18 days late"*, *"Invoice is 5 days overdue"*).

---

## 🔌 API Endpoints

### Platform Endpoints
- `GET /api/health` — Service health & database connectivity
- `GET /api/dashboard` — Aggregated metrics (Outstanding, At-Risk, Overdue, Total, Financing count)
- `GET /api/invoices` — List all invoices with buyer details and risk indicators
- `GET /api/invoices/<id>` — Detailed invoice view with risk reasons, events, payments & financing
- `GET /api/buyers` — List registered buyers with reliability scores and invoice volume
- `GET /api/buyers/<id>` — Buyer profile and complete invoice history
- `GET /api/events` — Live stream of invoice lifecycle events (limit 50)
- `GET /api/events/<invoice_id>` — Event history for a specific invoice
- `GET /api/financing/<invoice_id>` — Financing opportunities and TReDS discount quotes

### Simulation Endpoints
- `POST /api/simulation/run` — Executes end-to-end 10-step lifecycle simulation
- `POST /api/simulation/payment-delay` — Triggers payment delay and recalculates risk on active invoice
- `POST /api/simulation/payment` — Simulates RTGS settlement and settles outstanding invoice
- `POST /api/simulation/financing` — Simulates TReDS factoring request and discount approval
- `POST /api/simulation/reset` — Re-initializes clean baseline synthetic seed dataset

---

## 💻 Local Setup & Development

### Prerequisites
- Node.js >= 18
- Python >= 3.10
- Git

### 1. Clone Repository
```bash
git clone https://github.com/atharvanavgire10/receivx.git
cd receivx
```

### 2. Backend Setup
```bash
python -m pip install -r requirements.txt
cp .env.example .env
```

### 3. Frontend Setup
```bash
npm install
npm run dev
```

### 4. Run Test Suite
```bash
py -m pytest -v
```

---

## 🚀 Vercel Deployment

ReceivX deploys as a single unified project on Vercel:

1. Install Vercel CLI:
```bash
npm i -g vercel
```
2. Deploy directly:
```bash
vercel --prod
```
3. Set Environment Variable:
   - `DATABASE_URL` (PostgreSQL connection string).

---

## ⚠️ Important Disclaimer

> **ReceivX is a portfolio engineering implementation using synthetic data. It does NOT connect to the Reserve Bank of India (RBI), commercial banks, or production TReDS platforms (RXIL, M1xchange, Invoicemart). All company profiles, invoices, bids, and financial figures are synthetic.**

---

## 📄 License

MIT License — built for portfolio demonstration and MSME receivables intelligence research.
