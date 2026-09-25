import { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function Demo() {
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [activeStep, setActiveStep] = useState('');
  const pollingRef = useRef(null);

  const loadData = async () => {
    try {
      const [evts, dash] = await Promise.all([api.events(), api.dashboard()]);
      setEvents(evts);
      setMetrics(dash.metrics);
    } catch (e) {
      console.error('Polling error:', e);
    }
  };

  useEffect(() => {
    loadData();
    // Frontend polling every 3 seconds for real-time reactivity
    pollingRef.current = setInterval(loadData, 3000);
    return () => clearInterval(pollingRef.current);
  }, []);

  const runSimulation = async (action, label) => {
    setLoading(true);
    setActiveStep(label);
    setStatusMessage(`Executing ${label} on database…`);
    try {
      const res = await api.simulate(action);
      setStatusMessage(`✓ ${label} succeeded: ${res?.invoice_number || 'State updated'}`);
      await loadData();
    } catch (e) {
      setStatusMessage(`Error during ${label}: ${e.message}`);
    }
    setLoading(false);
    setActiveStep('');
  };

  const runFullDemoSequence = async () => {
    setLoading(true);
    setActiveStep('Run Full Demo');
    setStatusMessage('Initiating 10-step full receivables lifecycle simulation...');
    try {
      const res = await api.simulate('run');
      setStatusMessage(`✓ Full Demo Completed! Target ${res.invoice_number}: Accepted → Delayed → Risk Detected → Factored → Settled`);
      await loadData();
    } catch (e) {
      setStatusMessage(`Full Demo Error: ${e.message}`);
    }
    setLoading(false);
    setActiveStep('');
  };

  return (
    <div>
      <div className="page-header">
        <h1>ReceivX Interactive Demo</h1>
        <p>Experience the complete receivables lifecycle in real time.</p>
      </div>

      <div className="demo-controls">
        <button
          className="btn btn-primary"
          disabled={loading}
          onClick={runFullDemoSequence}
        >
          🚀 {loading && activeStep === 'Run Full Demo' ? 'Running Sequence…' : 'Run Full Demo'}
        </button>

        <button
          className="btn btn-danger"
          disabled={loading}
          onClick={() => runSimulation('payment-delay', 'Simulate Payment Delay')}
        >
          ⚠ Simulate Payment Delay
        </button>

        <button
          className="btn btn-success"
          disabled={loading}
          onClick={() => runSimulation('payment', 'Simulate Payment')}
        >
          💰 Simulate Payment
        </button>

        <button
          className="btn btn-warning"
          disabled={loading}
          onClick={() => runSimulation('financing', 'Check Financing')}
        >
          🏦 Check Financing
        </button>

        <button
          className="btn btn-secondary"
          disabled={loading}
          onClick={() => runSimulation('reset', 'Reset Demo')}
        >
          ↻ Reset Demo
        </button>
      </div>

      {statusMessage && (
        <div className="card" style={{ marginBottom: '1.25rem', borderColor: 'var(--accent)', background: 'rgba(59,130,246,0.06)' }}>
          <p style={{ fontSize: '0.9rem', color: 'var(--text)' }}>
            <strong>Status:</strong> {statusMessage}
          </p>
        </div>
      )}

      {metrics && (
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="label">Outstanding Receivables</div>
            <div className="value">{fmt(metrics.outstanding_amount)}</div>
            <div className="sub">{metrics.outstanding_count} invoices</div>
          </div>
          <div className="metric-card">
            <div className="label">At-Risk Receivables</div>
            <div className="value" style={{ color: 'var(--yellow)' }}>{fmt(metrics.at_risk_amount)}</div>
            <div className="sub">{metrics.at_risk_count} invoices</div>
          </div>
          <div className="metric-card">
            <div className="label">Overdue Amount</div>
            <div className="value" style={{ color: 'var(--red)' }}>{fmt(metrics.overdue_amount)}</div>
            <div className="sub">{metrics.overdue_count} overdue</div>
          </div>
          <div className="metric-card">
            <div className="label">Financing Opportunities</div>
            <div className="value" style={{ color: 'var(--purple)' }}>{metrics.financing_opportunities}</div>
            <div className="sub">Eligible / Active</div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2>LIVE EVENT STREAM</h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--green)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--green)', display: 'inline-block' }}></span>
            Real-time Polling Active (3s)
          </span>
        </div>
        <div className="event-feed">
          {events.length === 0 ? (
            <p className="empty">No events yet. Trigger an action above to observe financial state changes.</p>
          ) : (
            events.map(e => (
              <div key={e.id} className="event-feed-item">
                <span className="etime">{new Date(e.created_at).toLocaleTimeString('en-IN')}</span>
                <span className="etype">{e.event_type}</span>
                <span style={{ color: 'var(--text-muted)' }}>{e.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
