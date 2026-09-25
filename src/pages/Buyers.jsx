import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

function fmt(n) {
  return '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

export default function Buyers() {
  const [buyers, setBuyers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.buyers().then(setBuyers).catch(e => setError(e.message));
  }, []);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!buyers.length) return <div className="loading">Loading buyers…</div>;

  return (
    <div>
      <div className="page-header">
        <h1>Buyers</h1>
        <p>{buyers.length} registered buyers</p>
      </div>
      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Name</th><th>Industry</th><th>Terms</th><th>Avg Delay</th><th>Reliability</th><th>Invoices</th><th>Outstanding</th><th>Total Value</th></tr>
            </thead>
            <tbody>
              {buyers.map(b => (
                <tr key={b.id}>
                  <td><Link to={`/buyers/${b.id}`}>{b.name}</Link></td>
                  <td>{b.industry}</td>
                  <td>{b.payment_terms_days}d</td>
                  <td>{b.average_delay_days}d</td>
                  <td>
                    <span className={`badge ${b.reliability_score >= 80 ? 'badge-low' : b.reliability_score >= 60 ? 'badge-medium' : 'badge-critical'}`}>
                      {b.reliability_score}%
                    </span>
                  </td>
                  <td>{b.invoice_count}</td>
                  <td>{b.outstanding_count}</td>
                  <td>{fmt(b.total_value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
