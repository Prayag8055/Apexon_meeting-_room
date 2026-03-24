import { useState, useEffect, useCallback } from 'react';
import { getUsers, createUser, getBookings, getUserBookings, getRooms } from '../api';
import { PageHeader, EmptyState, Input, Select, Button } from '../components/ui';
import BookingCard from '../components/BookingCard';

const DEPARTMENTS = ['', 'Engineering', 'Design', 'Product', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Legal', 'Support', 'Other'];

function UserForm({ onSave, onCancel }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [dept, setDept] = useState('');
  const [role, setRole] = useState('employee');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Name is required.'); return; }
    if (!email.includes('@')) { setError('Valid email required.'); return; }
    if (password.length < 4) { setError('Password must be at least 4 characters.'); return; }
    onSave({ name: name.trim(), email: email.trim(), password, department: dept, role });
  };

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-[#1e2a45] mb-4 relative">
      <div className="absolute top-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-indigo-500 to-transparent" />
      <h3 className="text-base font-bold text-slate-100 mb-4">👤 Register New User</h3>
      {error && <div className="mb-3 px-4 py-2 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-400 text-sm">❌ {error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <Input label="Full Name" value={name} onChange={e => setName(e.target.value)} placeholder="Alex Johnson" />
          <Input label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="user@apexon.com" />
        </div>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min 4 chars" />
          <Select label="Department" value={dept} onChange={e => setDept(e.target.value)}
            options={DEPARTMENTS.map(d => ({ value: d, label: d || 'Select...' }))} />
          <Select label="Role" value={role} onChange={e => setRole(e.target.value)}
            options={[{ value: 'employee', label: 'Employee' }, { value: 'admin', label: 'Admin' }]} />
        </div>
        <div className="flex gap-2">
          <Button type="submit">✅ Register User</Button>
          <Button variant="secondary" type="button" onClick={onCancel}>✖ Cancel</Button>
        </div>
      </form>
    </div>
  );
}

function UserCard({ user, bookingCount, onView }) {
  const initials = user.name?.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2) || '?';
  const colors = [
    ['6366f1', '8b5cf6'], ['10b981', '34d399'], ['f59e0b', 'fbbf24'],
    ['06b6d4', '22d3ee'], ['f43f5e', 'fb7185'], ['8b5cf6', 'c084fc'],
  ];
  const idx = user.name ? [...user.name].reduce((s, c) => s + c.charCodeAt(0), 0) % colors.length : 0;
  const [c1, c2] = colors[idx];

  return (
    <div className="bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-[#1e2a45] rounded-2xl p-5 text-center transition-all hover:border-[#2d3f6b] hover:-translate-y-1 hover:shadow-[0_20px_60px_rgba(0,0,0,0.5)]">
      <div className="w-14 h-14 rounded-full mx-auto mb-3 flex items-center justify-center text-lg font-bold text-white"
        style={{ background: `linear-gradient(135deg, #${c1}, #${c2})` }}>
        {initials}
      </div>
      <div className="text-sm font-bold text-slate-100">{user.name}</div>
      <div className="text-xs text-slate-500 truncate" title={user.email}>{user.email}</div>
      <div className={`text-[0.68rem] font-bold uppercase tracking-wider mt-1 ${user.role === 'admin' ? 'text-indigo-400' : 'text-slate-500'}`}>
        {user.role === 'admin' ? '🛡️ Admin' : '👤 Employee'}
      </div>
      <div className="text-xs text-indigo-400 mt-1">{user.department || 'No department'}</div>
      <div className="mt-3">
        <div className="text-lg font-bold text-indigo-400">{bookingCount}</div>
        <div className="text-[0.6rem] text-slate-600 uppercase tracking-wider">Bookings</div>
      </div>
      <button onClick={() => onView(user)}
        className="w-full mt-3 py-2 rounded-xl text-xs font-semibold border border-[#1e2a45] text-slate-400 hover:border-indigo-500 hover:text-indigo-300 transition-all">
        View Bookings →
      </button>
    </div>
  );
}

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [bookingCounts, setBookingCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [userBookings, setUserBookings] = useState([]);
  const [rooms, setRooms] = useState([]);

  const reload = useCallback(() => {
    setLoading(true);
    Promise.all([getUsers(), getBookings()])
      .then(([u, b]) => {
        setUsers(u);
        const counts = {};
        b.forEach(bk => { if (bk.status === 'confirmed') counts[bk.user_id] = (counts[bk.user_id] || 0) + 1; });
        setBookingCounts(counts);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(reload, [reload]);

  const handleCreate = async (data) => {
    try { await createUser(data); setShowForm(false); reload(); }
    catch (e) { alert(e.detail || e.message); }
  };

  const handleViewBookings = async (u) => {
    setSelectedUser(u);
    try {
      const [bks, rms] = await Promise.all([getUserBookings(u.user_id), getRooms()]);
      setUserBookings(bks);
      setRooms(rms);
    } catch { setUserBookings([]); }
  };

  const filtered = search
    ? users.filter(u => [u.name, u.email, u.department].some(f => f?.toLowerCase().includes(search.toLowerCase())))
    : users;

  const depts = new Set(users.map(u => u.department).filter(Boolean));
  const roomMap = Object.fromEntries(rooms.map(r => [r.room_id, r.name]));

  if (loading) return <div className="text-center py-20 text-slate-500">Loading...</div>;

  return (
    <div className="animate-fade-up">
      <div className="flex items-start justify-between mb-6">
        <PageHeader title="👥 Team Members" subtitle="Manage team members and their booking history" />
        <Button onClick={() => setShowForm(!showForm)}>＋ Register User</Button>
      </div>

      {showForm && <UserForm onSave={handleCreate} onCancel={() => setShowForm(false)} />}

      {/* Search */}
      <div className="mb-4">
        <input type="text" value={search} onChange={e => setSearch(e.target.value)}
          placeholder="🔍 Search users by name, email, or department..."
          className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 outline-none" />
      </div>

      {/* Summary */}
      <div className="flex gap-6 mb-5 px-4 py-3 bg-[#0f1420] border border-[#1e2a45] rounded-xl">
        <span className="text-xs text-slate-500"><span className="text-slate-100 font-bold">{filtered.length}</span> team members</span>
        <span className="text-xs text-slate-500"><span className="text-indigo-400 font-bold">{depts.size}</span> departments</span>
      </div>

      {/* User grid */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {filtered.map(u => (
          <UserCard key={u.user_id} user={u} bookingCount={bookingCounts[u.user_id] || 0} onView={handleViewBookings} />
        ))}
      </div>

      {filtered.length === 0 && <EmptyState icon="👤" text="No users found." />}

      {/* User bookings drawer */}
      {selectedUser && (
        <div className="animate-fade-in">
          <div className="h-px bg-gradient-to-r from-transparent via-[#1e2a45] to-transparent mb-6" />
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-sm font-bold">
                {selectedUser.name?.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2)}
              </div>
              <div>
                <div className="text-base font-bold text-slate-100">Bookings for {selectedUser.name}</div>
                <div className="text-xs text-slate-500">{selectedUser.email} · {selectedUser.department}</div>
              </div>
            </div>
            <Button variant="secondary" onClick={() => setSelectedUser(null)}>✖ Close</Button>
          </div>
          {userBookings.length === 0 ? (
            <EmptyState icon="📭" text="No bookings for this user." />
          ) : (
            userBookings.map(b => (
              <BookingCard key={b.booking_id} booking={b} roomName={roomMap[b.room_id] || ''} userName={selectedUser.name} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
