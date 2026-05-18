import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../AuthContext';
import { getStats, getRooms, getBookings, getRoomAvailability, createBooking } from '../api';
import { StatCard, PageHeader, SectionHeader, EmptyState } from '../components/ui';
import BookingCard from '../components/BookingCard';
import { format } from 'date-fns';
import { useLocation } from "../LocationContext";


export default function Dashboard() {
  const { location } = useLocation();
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


  const [ibStart, setIbStart] = useState(null);
  const [ibEnd, setIbEnd] = useState(null)


  const reload = () => {
    setLoading(true);
    Promise.all([getStats(), getRooms(), getBookings()])
      .then(([s, r, b]) => { setStats(s); setRooms(r); setBookings(b); if (!ibRoom && r.length) setIbRoom(r[0].room_id); })
      .finally(() => setLoading(false));
  };

  useEffect(reload, []);

  const cityRooms = useMemo(() => {
    return rooms.filter(r => r.location === location);
  }, [rooms, location]);


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
    // ✅ Guard: both start & end required
    if (!ibStart || !ibEnd) return;

    // ✅ Guard: end must be after start
    if (new Date(ibEnd) <= new Date(ibStart)) {
      setIbMsg({
        type: "error",
        text: "End time must be after start time.",
      });
      return;
    }

    setIbBooking(true);
    setIbMsg({ type: "", text: "" });

    try {
      await createBooking({
        title: ibTitle.trim() || "Meeting",
        room_id: ibRoom,
        user_id: user.user_id,
        start_time: ibStart,   // ✅ HH:MM IST → ISO
        end_time: ibEnd,       // ✅ HH:MM IST → ISO
        notes: "",
      });

      const rName =
        cityRooms.find(r => r.room_id === ibRoom)?.name || "";

      setIbMsg({
        type: "success",
        text: `Booked! ${rName} · ${ibStart.slice(11, 16)}–${ibEnd.slice(11, 16)}`,
      });

      // ✅ Reset state
      setIbStart(null);
      setIbEnd(null);
      setIbTitle("");

      reload();
    } catch (e) {
      setIbMsg({
        type: "error",
        text:
          e?.status === 409
            ? "Time slot conflict. Please try a different range."
            : (e?.detail || e?.message || "Booking failed"),
      });
    } finally {
      setIbBooking(false);
    }
  };

  const firstName = user?.name?.split(' ')[0] || '';
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
  const todayStr = format(new Date(), 'EEEE, MMMM d, yyyy');
  const todayIso = format(new Date(), 'yyyy-MM-dd');
  const nowStr = format(new Date(), 'HH:mm');

  const activeRooms = cityRooms.filter(r => r.status === 'active');
  const roomMap = Object.fromEntries(cityRooms.map(r => [r.room_id, r.name]));
  const myBookings = bookings.filter(b => b.user_id === user?.user_id).sort((a, b) => b.created_at?.localeCompare(a.created_at)).slice(0, 6);
  const upcoming = bookings
    .filter(b => b.status === 'confirmed' && b.start_time?.slice(0, 10) === todayIso && b.start_time?.slice(11, 16) >= nowStr)
    .sort((a, b) => a.start_time.localeCompare(b.start_time))
    .slice(0, 8);


  const buildDateTime = (date, time) => `${date}T${time}:00`;

  if (loading) return <div className="text-center py-20 text-slate-500">Loading...</div>;

  return (
    <div className="animate-fade-up">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">
          {greeting}, {firstName} 👋
        </h1>
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
        {/* LEFT */}
        <div className="col-span-3">
          <SectionHeader title="⚡ Instant Book" />

          <div className="bg-gradient-to-br from-indigo-500/8 to-purple-500/5 border border-indigo-500/20 rounded-2xl p-5 mb-6">
            {/* Room & Date */}
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1.5">Room</label>
                <select
                  value={ibRoom}
                  onChange={e => {
                    setIbRoom(e.target.value);
                    setIbStart(null);
                    setIbEnd(null);
                  }}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm"
                >
                  {activeRooms.map(r => (
                    <option key={r.room_id} value={r.room_id}>{r.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase mb-1.5">Date</label>
                <input
                  type="date"
                  value={ibDate}
                  onChange={e => {
                    setIbDate(e.target.value);
                    setIbStart(null);
                    setIbEnd(null);
                  }}
                  className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm"
                />
              </div>
            </div>

            {/* Messages */}
            {ibMsg.text && (
              <div className={`mb-3 px-4 py-2 rounded-xl text-sm ${ibMsg.type === 'success'
                ? 'bg-emerald-500/8 border border-emerald-500/20 text-emerald-400'
                : 'bg-rose-500/8 border border-rose-500/20 text-rose-400'
                }`}>
                {ibMsg.type === 'success' ? '✅' : '❌'} {ibMsg.text}
              </div>
            )}

            {/* Slots */}
            {ibLoading ? (
              <div className="text-center py-4 text-slate-500 text-sm">Loading slots...</div>
            ) : ibSlots.length === 0 ? (
              <div className="text-center py-4 text-slate-500 text-sm">
                No available slots. Try another room or date.
              </div>
            ) : (
              <>
                {/* Time Picker */}
                <div className="grid grid-cols-2 gap-6 mb-4">

                  {/* START TIME */}
                  <div className="bg-[#0b1224] border border-[#1e2a45] rounded-2xl p-4">
                    <div className="text-sm font-semibold text-slate-400 mb-2">
                      Start Time
                    </div>

                    <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#070c1a] border border-[#1e2a45] mb-3">
                      <span className="text-slate-500">🕒</span>
                      <input
                        type="time"
                        value={ibStart ? ibStart.slice(11, 16) : ""}
                        onChange={e =>
                          setIbStart(buildDateTime(ibDate, e.target.value))
                        }
                        className="bg-transparent w-full text-slate-100 text-sm outline-none"
                      />
                    </div>
                  </div>

                  {/* END TIME */}
                  <div className="bg-[#0b1224] border border-[#1e2a45] rounded-2xl p-4">
                    <div className="text-sm font-semibold text-slate-400 mb-2">
                      End Time
                    </div>

                    <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#070c1a] border border-[#1e2a45] mb-3">
                      <span className="text-slate-500">🕒</span>
                      <input
                        type="time"
                        value={ibEnd ? ibEnd.slice(11, 16) : ""}
                        onChange={e =>
                          setIbEnd(buildDateTime(ibDate, e.target.value))
                        }
                        className="bg-transparent w-full text-slate-100 text-sm outline-none"
                      />
                    </div>
                  </div>

                </div>
              </>
            )}

            {/* Confirm */}
            {ibStart && ibEnd && (
              <div className="animate-fade-in">
                <div className="px-4 py-2.5 rounded-xl bg-emerald-500/8 border border-emerald-500/20 mb-3">
                  <span className="text-sm font-semibold text-emerald-400">
                    📅 {roomMap[ibRoom]} · {ibDate} · {ibStart.slice(11, 16)} – {ibEnd.slice(11, 16)}
                  </span>
                </div>

                <div className="flex gap-3 items-end">
                  <input
                    type="text"
                    value={ibTitle}
                    onChange={e => setIbTitle(e.target.value)}
                    placeholder="Meeting title (optional)"
                    className="flex-1 px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm"
                  />

                  <button
                    onClick={handleInstantBook}
                    disabled={ibBooking}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold text-sm disabled:opacity-50"
                  >
                    {ibBooking ? '⏳...' : '✅ Confirm'}
                  </button>

                  <button
                    onClick={() => {
                      setIbStart(null);
                      setIbEnd(null);
                    }}
                    className="px-3 py-2.5 rounded-xl border border-[#1e2a45] text-slate-400 text-sm"
                  >
                    ✖
                  </button>
                </div>
              </div>
            )}
          </div>

          <SectionHeader title="📋 My Recent Bookings" />
          {myBookings.length === 0
            ? <EmptyState icon="📭" text="No bookings yet. Use Instant Book above!" />
            : myBookings.map(b => (
              <BookingCard
                key={b.booking_id}
                booking={b}
                roomName={roomMap[b.room_id] || ''}
                userName={user?.name || ''}
              />
            ))
          }
        </div>

        {/* RIGHT */}
        <div className="col-span-2">
          <SectionHeader title="🕐 Upcoming Today" />
          {upcoming.length === 0
            ? <EmptyState icon="🎉" text="No more meetings today!" />
            : upcoming.map(b => (
              <div key={b.booking_id} className="p-3 bg-[#0f1420] border border-[#1e2a45] rounded-xl mb-2">
                <div className="text-sm font-semibold text-slate-100">{b.title}</div>
                <div className="text-xs text-slate-500">
                  🏢 {roomMap[b.room_id]} · {b.start_time.slice(11, 16)}–{b.end_time.slice(11, 16)}
                </div>
              </div>
            ))
          }
        </div>
      </div>
    </div>
  );
}
