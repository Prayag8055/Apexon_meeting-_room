import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { login, register } from '../api';

const DEPARTMENTS = ['', 'Engineering', 'Design', 'Product', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Legal', 'Support', 'Other'];

export default function LoginPage() {
  const { user, loginUser } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('login');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Login fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Register fields
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regDept, setRegDept] = useState('');

  if (user) { navigate('/', { replace: true }); return null; }

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) { setError('Please enter both email and password.'); return; }
    setLoading(true);
    try {
      const u = await login(email.trim(), password);
      loginUser(u);
      navigate('/');
    } catch (err) {
      setError(err.status === 401 ? 'Invalid email or password.' : (err.detail || err.message));
    } finally { setLoading(false); }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (!regName.trim()) { setError('Full name is required.'); return; }
    if (!regEmail.trim() || !regEmail.includes('@')) { setError('Valid email is required.'); return; }
    if (!regPassword || regPassword.length < 4) { setError('Password must be at least 4 characters.'); return; }
    setLoading(true);
    try {
      const u = await register({ name: regName.trim(), email: regEmail.trim(), password: regPassword, department: regDept });
      loginUser(u);
      navigate('/');
    } catch (err) {
      setError(err.status === 409 ? 'Email already registered. Please login.' : (err.detail || err.message));
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#080b14] via-[#0a0f1e] to-[#080b14]">
      <div className="w-full max-w-md animate-fade-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 text-2xl mb-3">
            🏢
          </div>
          <h1 className="text-2xl font-extrabold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Apexon RoomBook
          </h1>
          <p className="text-sm text-slate-500 mt-1">Meeting Room Booking System</p>
        </div>

        {/* Card */}
        <div className="bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-[#1e2a45] rounded-2xl p-6">
          {/* Tabs */}
          <div className="flex gap-1 mb-6 bg-[#080b14] rounded-xl p-1">
            {['login', 'register'].map(t => (
              <button
                key={t}
                onClick={() => { setTab(t); setError(''); }}
                className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                  tab === t
                    ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/15 text-indigo-400'
                    : 'text-slate-500 hover:text-slate-300'
                }`}
              >
                {t === 'login' ? '🔑 Login' : '📝 Register'}
              </button>
            ))}
          </div>

          {error && (
            <div className="mb-4 px-4 py-2.5 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-400 text-sm">
              ❌ {error}
            </div>
          )}

          {tab === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="you@apexon.com"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 outline-none transition-all" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 outline-none transition-all" />
              </div>
              <button type="submit" disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-bold text-sm hover:from-indigo-600 hover:to-purple-600 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-500/25 disabled:opacity-50">
                {loading ? '⏳ Signing in...' : '🔑 Sign In'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Full Name</label>
                  <input type="text" value={regName} onChange={e => setRegName(e.target.value)}
                    placeholder="Alex Johnson"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Email</label>
                  <input type="email" value={regEmail} onChange={e => setRegEmail(e.target.value)}
                    placeholder="you@apexon.com"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 outline-none transition-all" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Password</label>
                  <input type="password" value={regPassword} onChange={e => setRegPassword(e.target.value)}
                    placeholder="Min 4 characters"
                    className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 outline-none transition-all" />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Department</label>
                  <select value={regDept} onChange={e => setRegDept(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none transition-all">
                    <option value="">Select...</option>
                    {DEPARTMENTS.filter(Boolean).map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
              </div>
              <button type="submit" disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-bold text-sm hover:from-indigo-600 hover:to-purple-600 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-500/25 disabled:opacity-50">
                {loading ? '⏳ Creating account...' : '📝 Create Account'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
