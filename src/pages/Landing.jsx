import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div className="landing">
      <h1>Receiv<span>X</span></h1>
      <p className="tagline">Real-Time MSME Receivables Intelligence</p>
      <p className="subtitle">
        Get ahead of delayed payments before they become working-capital problems.
        Track invoices, detect risk, and explore financing — all in real time.
      </p>
      <div className="actions">
        <Link to="/demo" className="btn btn-primary">🚀 Launch Interactive Demo</Link>
        <Link to="/architecture" className="btn btn-secondary">🏗️ View Architecture</Link>
      </div>
      <footer>
        ReceivX is a portfolio project using synthetic data. It does not connect to RBI, banks, or production TReDS systems.
      </footer>
    </div>
  );
}
