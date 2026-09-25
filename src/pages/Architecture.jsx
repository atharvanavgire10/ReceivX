export default function Architecture() {
  return (
    <div>
      <div className="page-header">
        <h1>🏗️ Architecture</h1>
        <p>How ReceivX is built</p>
      </div>

      <div className="arch-flow">
        <div className="arch-node">React + Vite (Frontend)</div>
        <div className="arch-arrow">↓</div>
        <div className="arch-node">Vercel Edge Network</div>
        <div className="arch-arrow">↓</div>
        <div className="arch-node">Flask Serverless API (/api/*)</div>
        <div className="arch-arrow">↓</div>
        <div className="arch-node">PostgreSQL (Vercel Postgres)</div>
        <div className="arch-arrow">↓</div>
        <div className="arch-node" style={{ borderColor: 'var(--yellow)' }}>Deterministic Risk Engine</div>
        <div className="arch-arrow">↓</div>
        <div className="arch-node" style={{ borderColor: 'var(--green)' }}>Simulation / Event Engine</div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem' }}>
        <div className="card arch-section">
          <h3>Flask Serverless API</h3>
          <p>Python Flask runs as a Vercel serverless function. Every /api/* request routes to a single Flask app. SQLAlchemy manages database operations with parameterized queries.</p>
        </div>
        <div className="card arch-section">
          <h3>PostgreSQL Database</h3>
          <p>Persistent relational database stores companies, buyers, invoices, payments, events, and financing requests. Schema created on cold start. Seed data is idempotent.</p>
        </div>
        <div className="card arch-section">
          <h3>Deterministic Risk Engine</h3>
          <p>Rule-based scoring system evaluates buyer payment history, invoice proximity to due date, amount, reliability score, and overdue patterns. No ML or AI — fully testable and transparent.</p>
        </div>
        <div className="card arch-section">
          <h3>Event System</h3>
          <p>Every invoice lifecycle transition creates a persistent database event. Events power the timeline view, live feed, and audit trail. No message queues — just PostgreSQL.</p>
        </div>
        <div className="card arch-section">
          <h3>Simulation Engine</h3>
          <p>API-triggered simulation modifies real database state. Frontend polls for changes. No WebSockets, no Redis — Vercel-compatible architecture using database events + polling.</p>
        </div>
        <div className="card arch-section">
          <h3>Synthetic Data</h3>
          <p>All data is synthetic. ReceivX does not connect to RBI, banks, or production TReDS systems. Financing flows are simulated demonstrations only.</p>
        </div>
      </div>
    </div>
  );
}
