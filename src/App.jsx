import { Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Invoices from './pages/Invoices';
import InvoiceDetail from './pages/InvoiceDetail';
import Buyers from './pages/Buyers';
import BuyerDetail from './pages/BuyerDetail';
import Demo from './pages/Demo';
import Architecture from './pages/Architecture';
import Layout from './components/Layout';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/invoices" element={<Invoices />} />
        <Route path="/invoices/:id" element={<InvoiceDetail />} />
        <Route path="/buyers" element={<Buyers />} />
        <Route path="/buyers/:id" element={<BuyerDetail />} />
        <Route path="/demo" element={<Demo />} />
        <Route path="/architecture" element={<Architecture />} />
      </Route>
    </Routes>
  );
}
