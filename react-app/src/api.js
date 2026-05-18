const BASE = '/api';

class APIError extends Error {
  constructor(status, message, detail = '') {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

async function request(method, path, body = null, params = null) {
  let url = `${BASE}${path}`;
  if (params) {
    const sp = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => { if (v != null && v !== '') sp.set(k, v); });
    const qs = sp.toString();
    if (qs) url += `?${qs}`;
  }
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    throw new APIError(res.status, data?.error || res.statusText, data?.detail || '');
  }
  return data;
}

// Auth
export const login = (email, password) => request('POST', '/auth/login', { email, password });
export const register = (payload) => request('POST', '/auth/register', payload);

// Health & Stats
export const healthCheck = () => request('GET', '/health').catch(() => ({ status: 'error' }));
export const getStats = () => request('GET', '/stats').catch(() => ({}));

// Rooms
export const getRooms = (params) => request('GET', '/rooms', null, params);
export const createRoom = (payload) => request('POST', '/rooms', payload);
export const updateRoom = (id, payload) => request('PUT', `/rooms/${id}`, payload);
export const deactivateRoom = (id) => request('DELETE', `/rooms/${id}`);
export const getRoomAvailability = (id, date) => request('GET', `/rooms/${id}/availability`, null, { date });

// Bookings
export const getBookings = (params) => request('GET', '/bookings', null, params);
export const createBooking = (payload) => request('POST', '/bookings', payload);
export const updateBooking = (id, payload) => request('PUT', `/bookings/${id}`, payload);
export const cancelBooking = (id) => request('DELETE', `/bookings/${id}`);

// Users
export const getUsers = () => request('GET', '/users');
export const createUser = (payload) => request('POST', '/users', payload);
export const getUserBookings = (id) => request('GET', `/users/${id}/bookings`);

// Check-in/Check-out
export const checkInBooking = (id) => request('POST', `/bookings/${id}/checkin`);
export const checkOutBooking = (id) => request('POST', `/bookings/${id}/checkout`);

export { APIError };
