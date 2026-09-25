import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [invoices, setInvoices] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.dashboard().then(setData).catch(e => setError(e.message));
    api.invoices().then(setInvoices).catch(() => {});
  }, []);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!data) return <div className="loading">Loading dashboard…</div>;

  const m = data.metrics;
  const recent = invoices.slice(0, 10);

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>{data.company?.name}</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="label">Outstanding Receivables</div>
          <div className="value">{fmt(m.outstanding_amount)}</div>
          <div className="sub">{m.outstanding_count} invoices</div>
        </div>
        <div className="metric-card">
          <div className="label">At-Risk Receivables</div>
          <div className="value" style={{ color: 'var(--yellow)' }}>{fmt(m.at_risk_amount)}</div>
          <div className="sub">{m.at_risk_count} invoices</div>
        </div>
        <div className="metric-card">
          <div className="label">Overdue Amount</div>
          <div className="value" style={{ color: 'var(--red)' }}>{fmt(m.overdue_amount)}</div>
          <div className="sub">{m.overdue_count} invoices</div>
        </div>
        <div className="metric-card">
          <div className="label">Total Invoices</div>
          <div className="value">{m.total_invoices}</div>
        </div>
        <div className="metric-card">
          <div className="label">Financing Opportunities</div>
          <div className="value" style={{ color: 'var(--purple)' }}>{m.financing_opportunities}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Recent Invoices</h2>
          <Link to="/invoices" className="btn btn-secondary" style={{ fontSize: '0.8rem', padding: '0.35rem 0.8rem' }}>View All</Link>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Invoice</th><th>Buyer</th><th>Amount</th><th>Due Date</th><th>Status</th><th>Risk</th></tr>
            </thead>
            <tbody>
              {recent.map(inv => (
                <tr key={inv.id}>
                  <td><Link to={`/invoices/${inv.id}`}>{inv.invoice_number}</Link></td>
                  <td>{inv.buyer_name}</td>
                  <td>{fmt(inv.amount)}</td>
                  <td>{new Date(inv.due_at).toLocaleDateString('en-IN')}</td>
                  <td><span className={`badge badge-${inv.status.toLowerCase()}`}>{inv.status}</span></td>
                  <td><span className={`badge badge-${inv.risk_level.toLowerCase()}`}>{inv.risk_score} {inv.risk_level}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
