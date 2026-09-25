import { Outlet, NavLink } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>Receiv<span>X</span></h1>
          <p>MSME Receivables Intelligence</p>
        </div>
        <nav>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'active' : ''}>📊 Dashboard</NavLink>
          <NavLink to="/invoices" className={({ isActive }) => isActive ? 'active' : ''}>📄 Invoices</NavLink>
          <NavLink to="/buyers" className={({ isActive }) => isActive ? 'active' : ''}>🏢 Buyers</NavLink>
          <NavLink to="/demo" className={({ isActive }) => isActive ? 'active' : ''}>🚀 Demo</NavLink>
          <NavLink to="/architecture" className={({ isActive }) => isActive ? 'active' : ''}>🏗️ Architecture</NavLink>
        </nav>
      </aside>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
