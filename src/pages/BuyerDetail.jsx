import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function BuyerDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.buyer(id).then(setData).catch(e => setError(e.message));
  }, [id]);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!data) return <div className="loading">Loading buyer…</div>;

  const { buyer, invoices, stats } = data;

  return (
    <div>
      <div className="page-header">
        <h1>{buyer.name}</h1>
        <p>{buyer.industry}</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="label">Total Invoices</div>
          <div className="value">{stats.invoice_count}</div>
        </div>
        <div className="metric-card">
          <div className="label">Total Value</div>
          <div className="value">{fmt(stats.total_value)}</div>
        </div>
        <div className="metric-card">
          <div className="label">Outstanding</div>
          <div className="value" style={{ color: 'var(--yellow)' }}>{stats.outstanding_count}</div>
          <div className="sub">{fmt(stats.outstanding_amount)}</div>
        </div>
        <div className="metric-card">
          <div className="label">Avg Delay</div>
          <div className="value">{buyer.average_delay_days} days</div>
        </div>
        <div className="metric-card">
          <div className="label">Reliability</div>
          <div className="value" style={{ color: buyer.reliability_score >= 80 ? 'var(--green)' : buyer.reliability_score >= 60 ? 'var(--yellow)' : 'var(--red)' }}>
            {buyer.reliability_score}%
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2>Invoices</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Invoice</th><th>Amount</th><th>Due</th><th>Status</th><th>Risk</th></tr>
            </thead>
            <tbody>
              {invoices.map(inv => (
                <tr key={inv.id}>
                  <td><Link to={`/invoices/${inv.id}`}>{inv.invoice_number}</Link></td>
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
