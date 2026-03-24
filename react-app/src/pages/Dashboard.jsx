import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { getStats, getRooms, getBookings, getRoomAvailability, createBooking } from '../api';
import { StatCard, PageHeader, SectionHeader, EmptyState } from '../components/ui';
import BookingCard from '../components/BookingCard';
import { format } from 'date-fns';

export default function Dashboard() {
  const { user, isAdmin } = useAuth();
  const [stats, setStats] = useState({});
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  // Instant book state
  const [ibRoom, setIbRoom] = useState('');
  const [ibDate, setIbDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [ibSlots, setIbSlots] = useState([]);
  const [ibLoading, setIbLoading] = useState(false);
  const [ibSelected, setIbSelected] = useState(null);
  const [ibTitle, setIbTitle] = useState('');
  const [ibBooking, setIbBooking] = useState(false);
  const [ibMsg, setIbMsg] = useState({ type: '', text: '' });

  const reload = () => {
    setLoading(true);
    Promise.all([getStats(), getRooms(), getBookings()])
      .then(([s, r, b]) => { setStats(s); setRooms(r); setBookings(b); if (!ibRoom && r.length) setIbRoom(r[0].room_id); })
      .finally(() => setLoading(false));
  };

  useEffect(reload, []);

  // Load slots when room/date changes
  useEffect(() => {
    if (!ibRoom) return;
    setIbLoading(true);
    setIbSelected(null);
    setIbMsg({ type: '', text: '' });
    getRoomAvailability(ibRoom, ibDate)
      .then(data => {
        let free = (data.slots || []).filter(s => s.is_available);
        const today = format(new Date(), 'yyyy-MM-dd');
        if (ibDate === today) {
          const now = format(new Date(), 'HH:mm');
          free = free.filter(s => s.start_time.slice(11, 16) >= now);
        }
        setIbSlots(free);
      })
      .catch(() => setIbSlots([]))
      .finally(() => setIbLoading(false));
  }, [ibRoom, ibDate]);

  const handleInstantBook = async () => {
    if (!ibSelected) return;
    setIbBooking(true);
    setIbMsg({ type: '', text: '' });
    try {
      await createBooking({
        title: ibTitle.trim() || 'Meeting',
        room_id: ibRoom,
        user_id: user.user_id,
        start_time: ibSelected.start_time,
        end_time: ibSelected.end_time,
        notes: '',
      });
      const rName = rooms.find(r => r.room_id === ibRoom)?.name || '';
      setIbMsg({ type: 'success', text: `Booked! ${rName} at ${ibSelected.start_time.slice(11, 16)}` });
      setIbSelected(null);
      setIbTitle('');
      reload();
    } catch (e) {
      setIbMsg({ type: 'error', text: e.status === 409 ? 'Slot just got taken.' : (e.detail || e.message) });
    } finally { setIbBooking(false); }
  };

  const firstName = user?.name?.split(' ')[0] || '';
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const todayStr = format(new Date(), 'EEEE, MMMM d, yyyy');
  const todayIso = format(new Date(), 'yyyy-MM-dd');
  const nowStr = format(new Date(), 'HH:mm');

  const activeRooms = rooms.filter(r => r.status === 'active');
  const roomMap = Object.fromEntries(rooms.map(r => [r.room_id, r.name]));
  const myBookings = bookings.filter(b => b.user_id === user?.user_id).sort((a, b) => b.created_at?.localeCompare(a.created_at)).slice(0, 6);
  const upcoming = bookings
    .filter(b => b.status === 'confirmed' && b.start_time?.slice(0, 10) === todayIso && b.start_time?.slice(11, 16) >= nowStr)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
    .slice(0, 8);

  if (loading) return <div className="text-center py-20 text-slate-500">Loading...</div>;

  return (
    <div className="animate-fade-up">
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">{greeting}, {firstName} 👋</h1>
        <p className="text-sm text-slate-500 mt-1">{todayStr}</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Active Rooms" value={stats.active_rooms || 0} icon="🏢" color="#818cf8" />
        <StatCard label="Total Bookings" value={stats.total_bookings || 0} icon="📅" color="#34d399" />
        <StatCard label="Today's Meetings" value={stats.today_bookings || 0} icon="✅" color="#fbbf24" />
        {isAdmin
          ? <StatCard label="Team Members" value={stats.total_users || 0} icon="👥" color="#67e8f9" />
          : <StatCard label="My Bookings" value={myBookings.filter(b => b.status === 'confirmed').length} icon="📋" color="#67e8f9" />
        }
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Left: Instant Book + My Bookings */}
        <div className="col-span-3">
          <SectionHeader title="⚡ Instant Book" />
          <div className="bg-gradient-to-br from-indigo-500/8 to-purple-500/5 border border-indigo-500/20 rounded-2xl p-5 mb-6">
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Room</label>
                <select value={ibRoom} onChange={e => setIbRoom(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none">
                  {activeRooms.map(r => <option key={r.room_id} value={r.room_id}>{r.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Date</label>
                <input type="date" value={ibDate} onChange={e => setIbDate(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none" />
              </div>
            </div>

            {ibMsg.text && (
              <div className={`mb-3 px-4 py-2 rounded-xl text-sm ${
                ibMsg.type === 'success' ? 'bg-emerald-500/8 border border-emerald-500/20 text-emerald-400'
                  : 'bg-rose-500/8 border border-rose-500/20 text-rose-400'
              }`}>{ibMsg.type === 'success' ? '✅' : '❌'} {ibMsg.text}</div>
            )}

            {ibLoading ? (
              <div className="text-center py-4 text-slate-500 text-sm">Loading slots...</div>
            ) : ibSlots.length === 0 ? (
              <div className="text-center py-4 text-slate-500 text-sm">No available slots. Try another room or date.</div>
            ) : (
              <>
                <div className="text-xs text-slate-500 mb-2">🟢 {ibSlots.length} slots available — click to book</div>
                <div className="grid grid-cols-6 gap-1.5 mb-3">
                  {ibSlots.slice(0, 18).map((slot, i) => {
                    const t = slot.start_time.slice(11, 16);
                    const picked = ibSelected?.start_time === slot.start_time;
                    return (
                      <button key={i} onClick={() => setIbSelected(slot)}
                        className={`py-1.5 rounded-lg text-xs font-bold transition-all ${
                          picked
                            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white scale-105'
                            : 'bg-[#0a0f1e] border border-[#1e2a45] text-slate-400 hover:border-indigo-500 hover:text-indigo-300'
                        }`}>
                        {t}
                      </button>
                    );
                  })}
                </div>
              </>
            )}

            {ibSelected && (
              <div className="animate-fade-in">
                <div className="px-4 py-2.5 rounded-xl bg-emerald-500/8 border border-emerald-500/20 mb-3">
                  <span className="text-sm font-semibold text-emerald-400">
                    📅 {roomMap[ibRoom]} · {ibDate} · {ibSelected.start_time.slice(11, 16)} – {ibSelected.end_time.slice(11, 16)}
                  </span>
                </div>
                <div className="flex gap-3 items-end">
                  <div className="flex-1">
                    <input type="text" value={ibTitle} onChange={e => setIbTitle(e.target.value)}
                      placeholder="Meeting title (optional)"
                      className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 outline-none" />
                  </div>
                  <button onClick={handleInstantBook} disabled={ibBooking}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold text-sm hover:from-emerald-600 hover:to-teal-600 transition-all disabled:opacity-50 whitespace-nowrap">
                    {ibBooking ? '⏳...' : '✅ Confirm'}
                  </button>
                  <button onClick={() => setIbSelected(null)}
                    className="px-3 py-2.5 rounded-xl border border-[#1e2a45] text-slate-400 text-sm hover:border-rose-500 hover:text-rose-400 transition-all">
                    ✖
                  </button>
                </div>
              </div>
            )}
          </div>

          <SectionHeader title="📋 My Recent Bookings" />
          {myBookings.length === 0 ? (
            <EmptyState icon="📭" text="No bookings yet. Use Instant Book above!" />
          ) : (
            myBookings.map(b => (
              <BookingCard key={b.booking_id} booking={b} roomName={roomMap[b.room_id] || ''} userName={user?.name || ''} />
            ))
          )}
        </div>

        {/* Right: Upcoming + Room Status */}
        <div className="col-span-2">
          <SectionHeader title="🕐 Upcoming Today" />
          {upcoming.length === 0 ? (
            <EmptyState icon="🎉" text="No more meetings today!" />
          ) : (
            <div className="space-y-2">
              {upcoming.map(b => {
                const sT = b.start_time?.slice(11, 16);
                const eT = b.end_time?.slice(11, 16);
                const isMine = b.user_id === user?.user_id;
                return (
                  <div key={b.booking_id}
                    className={`flex items-start gap-3 p-3 bg-[#0f1420] border border-[#1e2a45] rounded-xl transition-all hover:border-[#2d3f6b] hover:translate-x-1 ${isMine ? 'border-l-2 border-l-indigo-500' : ''}`}>
                    <div className="text-xs font-bold text-indigo-400 min-w-[40px] text-center pt-0.5">{sT}</div>
                    <div className="w-2.5 h-2.5 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex-shrink-0 mt-1" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-slate-100 truncate">{b.title}</div>
                      <div className="text-[0.7rem] text-slate-600 mt-0.5">
                        🏢 {roomMap[b.room_id] || ''} · {sT}–{eT}{isMine ? ' · 👤 You' : ''}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="mt-6">
            <SectionHeader title="🏢 Rooms" />
            <div className="space-y-1.5">
              {rooms.slice(0, 10).map(r => (
                <div key={r.room_id} className="flex items-center gap-3 px-3 py-2 bg-[#0f1420] border border-[#1e2a45] rounded-xl">
                  <div className={`w-2 h-2 rounded-full ${r.status === 'active' ? 'bg-emerald-400' : 'bg-slate-600'}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-slate-100 truncate">{r.name}</div>
                    <div className="text-[0.65rem] text-slate-600">👥 {r.capacity} seats</div>
                  </div>
                  <div className={`text-[0.65rem] font-bold uppercase ${r.status === 'active' ? 'text-indigo-400' : 'text-slate-600'}`}>
                    {r.status}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
