import { useState, useEffect } from 'react';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function Demo() {
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const loadData = async () => {
    try {
      const [evts, dash] = await Promise.all([api.events(), api.dashboard()]);
      setEvents(evts);
      setMetrics(dash.metrics);
    } catch (e) {
      setMessage('Error loading data: ' + e.message);
    }
  };

  useEffect(() => { loadData(); }, []);

  const runAction = async (action) => {
    setLoading(true);
    setMessage('');
    try {
      await api.simulate(action);
      setMessage(`✓ ${action} completed`);
      await loadData();
    } catch (e) {
      setMessage(`Error: ${e.message}`);
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="page-header">
        <h1>🚀 ReceivX Interactive Demo</h1>
        <p>Experience the complete receivables lifecycle. Simulation endpoints available in Phase 2.</p>
      </div>

      <div className="demo-controls">
        <button className="btn btn-primary" disabled={loading} onClick={() => runAction('run')}>🚀 Run Full Demo</button>
        <button className="btn btn-danger" disabled={loading} onClick={() => runAction('payment-delay')}>⚠ Simulate Payment Delay</button>
        <button className="btn btn-success" disabled={loading} onClick={() => runAction('payment')}>💰 Simulate Payment</button>
        <button className="btn btn-warning" disabled={loading} onClick={() => runAction('financing')}>🏦 Simulate Financing</button>
        <button className="btn btn-secondary" disabled={loading} onClick={() => runAction('reset')}>↻ Reset Demo</button>
      </div>

      {message && <div className="card" style={{ marginBottom: '1rem', padding: '0.75rem 1rem', fontSize: '0.88rem' }}>{message}</div>}

      {metrics && (
        <div className="metrics-grid">
          <div className="metric-card"><div className="label">Outstanding</div><div className="value">{fmt(metrics.outstanding_amount)}</div></div>
          <div className="metric-card"><div className="label">At Risk</div><div className="value" style={{ color: 'var(--yellow)' }}>{fmt(metrics.at_risk_amount)}</div></div>
          <div className="metric-card"><div className="label">Overdue</div><div className="value" style={{ color: 'var(--red)' }}>{fmt(metrics.overdue_amount)}</div></div>
          <div className="metric-card"><div className="label">Financing</div><div className="value" style={{ color: 'var(--purple)' }}>{metrics.financing_opportunities}</div></div>
        </div>
      )}

      <div className="card">
        <div className="card-header"><h2>Live Event Stream</h2></div>
        <div className="event-feed">
          {events.length === 0 && <p className="empty">No events yet. Run a simulation to see events.</p>}
          {events.map(e => (
            <div key={e.id} className="event-feed-item">
              <span className="etime">{new Date(e.created_at).toLocaleTimeString('en-IN')}</span>
              <span className="etype">{e.event_type}</span>
              <span>{e.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
