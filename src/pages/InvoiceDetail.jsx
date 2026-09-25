import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function InvoiceDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.invoice(id).then(setData).catch(e => setError(e.message));
  }, [id]);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!data) return <div className="loading">Loading invoice…</div>;

  const { invoice: inv, buyer, events, payments, financing } = data;

  return (
    <div>
      <div className="page-header">
        <h1>{inv.invoice_number}</h1>
        <p>
          <span className={`badge badge-${inv.status.toLowerCase()}`}>{inv.status}</span>
          {' '}
          <span className={`badge badge-${inv.risk_level.toLowerCase()}`}>{inv.risk_score} {inv.risk_level}</span>
        </p>
      </div>

      <div className="detail-grid">
        <div className="card">
          <h2 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem' }}>Invoice Details</h2>
          <div className="detail-row"><span className="lbl">Amount</span><span>{fmt(inv.amount)}</span></div>
          <div className="detail-row"><span className="lbl">Issued</span><span>{new Date(inv.issued_at).toLocaleDateString('en-IN')}</span></div>
          <div className="detail-row"><span className="lbl">Due Date</span><span>{new Date(inv.due_at).toLocaleDateString('en-IN')}</span></div>
          <div className="detail-row"><span className="lbl">Status</span><span className={`badge badge-${inv.status.toLowerCase()}`}>{inv.status}</span></div>
          <div className="detail-row"><span className="lbl">Risk Score</span><span>{inv.risk_score}/100</span></div>
          <div className="detail-row"><span className="lbl">Risk Level</span><span className={`badge badge-${inv.risk_level.toLowerCase()}`}>{inv.risk_level}</span></div>
        </div>

        <div className="card">
          <h2 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem' }}>Buyer</h2>
          {buyer && (
            <>
              <div className="detail-row"><span className="lbl">Name</span><Link to={`/buyers/${buyer.id}`}>{buyer.name}</Link></div>
              <div className="detail-row"><span className="lbl">Industry</span><span>{buyer.industry}</span></div>
              <div className="detail-row"><span className="lbl">Payment Terms</span><span>{buyer.payment_terms_days} days</span></div>
              <div className="detail-row"><span className="lbl">Avg Delay</span><span>{buyer.average_delay_days} days</span></div>
              <div className="detail-row"><span className="lbl">Reliability</span><span>{buyer.reliability_score}%</span></div>
            </>
          )}
        </div>
      </div>

      {/* Risk Reasons placeholder */}
      {inv.risk_score > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem' }}>⚠ Risk Analysis</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Risk score: {inv.risk_score} ({inv.risk_level}). Detailed risk reasons available in Phase 2.
          </p>
        </div>
      )}

      {/* Payments */}
      {payments.length > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <h2 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem' }}>Payments</h2>
          <table>
            <thead><tr><th>Amount</th><th>Date</th><th>Status</th><th>Reference</th></tr></thead>
            <tbody>
              {payments.map(p => (
                <tr key={p.id}>
                  <td>{fmt(p.amount)}</td>
                  <td>{new Date(p.payment_date).toLocaleDateString('en-IN')}</td>
                  <td><span className="badge badge-paid">{p.status}</span></td>
                  <td style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>{p.reference}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Financing */}
      {financing.length > 0 && (
        <div className="card" style={{ marginBottom: '1.25rem' }}>
          <div className="financing-label">🏦 Financing Status <span className="sim">Simulated</span></div>
          {financing.map(f => (
            <div key={f.id} className="financing-card">
              <div className="financier">{f.financier}</div>
              <div className="detail-row"><span className="lbl">Status</span><span className={`badge badge-${f.status === 'ELIGIBLE' ? 'issued' : 'paid'}`}>{f.status}</span></div>
              <div className="detail-row"><span className="lbl">Discount Rate</span><span className="rate">{f.discount_rate}%</span></div>
              <div className="detail-row"><span className="lbl">Settlement</span><span>{fmt(f.settlement_amount)}</span></div>
            </div>
          ))}
        </div>
      )}

      {/* Event Timeline */}
      <div className="card">
        <h2 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.75rem' }}>Event Timeline</h2>
        {events.length === 0 ? (
          <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>No events recorded.</p>
        ) : (
          <div className="timeline">
            {events.map(e => (
              <div key={e.id} className="timeline-item">
                <div className="event-type">{e.event_type}</div>
                <div className="msg">{e.message}</div>
                <div className="time">{new Date(e.created_at).toLocaleString('en-IN')}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
