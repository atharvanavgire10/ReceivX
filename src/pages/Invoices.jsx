import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.invoices().then(setInvoices).catch(e => setError(e.message));
  }, []);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!invoices.length) return <div className="loading">Loading invoices…</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Invoices</h1>
        <p>{invoices.length} total invoices</p>
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Invoice</th><th>Buyer</th><th>Amount</th><th>Issued</th><th>Due Date</th><th>Status</th><th>Risk</th></tr>
            </thead>
            <tbody>
              {invoices.map(inv => (
                <tr key={inv.id}>
                  <td><Link to={`/invoices/${inv.id}`}>{inv.invoice_number}</Link></td>
                  <td>{inv.buyer_name}</td>
                  <td>{fmt(inv.amount)}</td>
                  <td>{new Date(inv.issued_at).toLocaleDateString('en-IN')}</td>
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
