import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { healthCheck } from '../api';
import { useState, useEffect } from 'react';
import {
  LayoutDashboard, CalendarDays, Building2, Users, LogOut,
} from 'lucide-react';
import { Navbar } from "./Navbar";
import logo from "../assets/Apexon_id6ht3QYLO_0.png";

const NAV = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard', sub: 'Overview & stats', adminOnly: false },
  { to: '/bookings', icon: CalendarDays, label: 'Bookings', sub: 'Book rooms', adminOnly: false },
  { to: '/rooms', icon: Building2, label: 'Rooms', sub: 'Manage spaces', adminOnly: true },
  { to: '/users', icon: Users, label: 'Users', sub: 'Team members', adminOnly: true },
];

export default function Layout({ children }) {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const [apiOk, setApiOk] = useState(true);
  const [location, setLocation] = useState("Pune");


  useEffect(() => {
    healthCheck().then(d => setApiOk(d?.status === 'ok'));
    const t = setInterval(() => healthCheck().then(d => setApiOk(d?.status === 'ok')), 30000);
    return () => clearInterval(t);
  }, []);

  const initials = user?.name?.split(' ').map(p => p[0]).join('').toUpperCase().slice(0, 2) || '?';

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div className="flex h-screen overflow-hidden bg-[#080b14]">

      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 flex flex-col border-r border-[#1e2a45] bg-gradient-to-b from-[#0a0f1e] to-[#080b14]">
        {/* Logo */}
        <div className="px-5 pt-6 pb-4 border-b border-[#1e2a45]">
          <div className="flex items-center gap-3">
            <img
              src={logo}
              alt="Apexon Logo"
              className="w-full max-w-[160px] h-auto object-contain opacity-90"
            />
          </div>
          <div className="leading-tight">
            <h1 className="text-base mt-4 font-semibold text-slate-500">
              RoomBook
            </h1>
            <p className="text-[0.65rem] tracking-[0.2em] text-slate-500 uppercase">
              Meeting Room Manager
            </p>
          </div>
        </div>

        {/* User info */}
        <div className="mx-3 mt-4 mb-2 p-3 rounded-xl bg-indigo-500/5 border border-indigo-500/15">
          <div className="flex items-center gap-3">

            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-xs font-bold">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-semibold text-slate-100 truncate">{user?.name}</div>
              <div className="text-[0.65rem] text-slate-500">
                {isAdmin ? '🛡️ Admin' : '👤 Employee'}
              </div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <div className="px-3 mt-2">
          <div className="text-[0.65rem] uppercase tracking-widest text-slate-600 font-semibold px-3 py-2">
            Navigation
          </div>
          <nav className="space-y-0.5">
            {NAV.filter(n => !n.adminOnly || isAdmin).map(n => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${isActive
                    ? 'bg-gradient-to-r from-indigo-500/15 to-purple-500/10 text-indigo-400 border border-indigo-500/20'
                    : 'text-slate-500 hover:bg-indigo-500/5 hover:text-indigo-300 border border-transparent'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <n.icon size={18} />
                    <div className="flex-1">
                      <div className="leading-tight">{n.label}</div>
                      <div className="text-[0.6rem] opacity-50 font-normal">{n.sub}</div>
                    </div>
                    {isActive && <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />}
                  </>
                )}
              </NavLink>
            ))}
          </nav>
        </div>

        <div className="flex-1" />

        {/* Health */}
        <div className="px-3 mb-2">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium ${apiOk ? 'bg-emerald-500/8 border border-emerald-500/20 text-emerald-400'
            : 'bg-rose-500/8 border border-rose-500/20 text-rose-400'
            }`}>
            <div className={`w-2 h-2 rounded-full ${apiOk ? 'bg-emerald-400 animate-blink' : 'bg-rose-400'}`} />
            {apiOk ? 'API Connected' : 'API Unreachable'}
          </div>
        </div>

        {/* Logout */}
        <div className="px-3 mb-4">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm text-slate-500 hover:text-rose-400 hover:bg-rose-500/5 border border-transparent hover:border-rose-500/20 transition-all"
          >
            <LogOut size={16} /> Logout
          </button>
        </div>

        <div className="px-5 pb-4 text-[0.65rem] text-slate-700">v4.0 · Apexon Room Booking</div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <Navbar
          selectedLocation={location}
          onLocationChange={setLocation}
        />
        <div className="max-w-[1400px] mx-auto px-8 py-6">
          {children}
        </div>
      </main>
    </div>
  );
}
