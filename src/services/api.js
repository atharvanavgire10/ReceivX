const BASE = '/api';

async function request(url) {
  const res = await fetch(`${BASE}${url}`);
  const json = await res.json();
  if (!json.success) throw new Error(json.error || 'API error');
  return json.data;
}

async function post(url, body = {}) {
  const res = await fetch(`${BASE}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!json.success) throw new Error(json.error || 'API error');
  return json.data;
}

export const api = {
  health: () => request('/health'),
  dashboard: () => request('/dashboard'),
  invoices: () => request('/invoices'),
  invoice: (id) => request(`/invoices/${id}`),
  buyers: () => request('/buyers'),
  buyer: (id) => request(`/buyers/${id}`),
  events: () => request('/events'),
  invoiceEvents: (id) => request(`/events/${id}`),
  financing: (id) => request(`/financing/${id}`),
  // Simulation endpoints (Phase 2)
  simulate: (action, body) => post(`/simulation/${action}`, body),
};
