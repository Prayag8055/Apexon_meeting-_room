import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '../AuthContext';
import { getRooms, getUsers, getBookings, cancelBooking, updateBooking, checkInBooking, checkOutBooking } from '../api';
import { PageHeader, SectionHeader, EmptyState } from '../components/ui';
import RoomCard from '../components/RoomCard';
import SlotPicker from '../components/SlotPicker';
import BookingCard from '../components/BookingCard';
import { format } from 'date-fns';
import { useLocation } from "../LocationContext";

export default function BookingsPage() {
  const { location } = useLocation();
  const { user, isAdmin } = useAuth();
  const [rooms, setRooms] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Room selection for booking
  const [selectedRoom, setSelectedRoom] = useState(null);

  // Cancel confirm
  const [cancelTarget, setCancelTarget] = useState(null);

  // Reschedule
  const [rescheduleTarget, setRescheduleTarget] = useState(null);
  const [rescheduleData, setRescheduleData] = useState({ date: '', start: '', end: '', title: '' });
  const [rescheduleError, setRescheduleError] = useState('');

  // Filters
  const [filterDate, setFilterDate] = useState('');
  const [filterRoom, setFilterRoom] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [capacityFilter, setCapacityFilter] = useState("any");
  const [amenityFilters, setAmenityFilters] = useState([]);

  const AMENITIES = [
    "Projector",
    "Wifi",
    "AC",
    "Whiteboard",
    "Coffee Bar",
    "Video Call",
    "TV",
  ];

  const reload = useCallback(() => {
    setLoading(true);
    Promise.all([
      getRooms(),
      getBookings(isAdmin ? {} : { user_id: user?.user_id }),
      isAdmin ? getUsers() : Promise.resolve([user]),
    ])
      .then(([r, b, u]) => { setRooms(r); setBookings(b); setUsers(u); })
      .finally(() => setLoading(false));
  }, [isAdmin, user]);

  // Check‑in / check‑out handlers now live inside the component so they can call `reload`
  const handleCheckIn = async (booking) => {
    try {
      await checkInBooking(booking.booking_id);
      reload();
    } catch (e) {
      alert(e.detail || e.message);
    }
  };

  const handleCheckOut = async (booking) => {
    try {
      await checkOutBooking(booking.booking_id);
      reload();
    } catch (e) {
      alert(e.detail || e.message);
    }
  };

  useEffect(reload, [reload]);

  const cityRooms = useMemo(() => {
    return rooms.filter(r => r.location === location);
  }, [rooms, location]);

  const activeRooms = cityRooms.filter(r => r.status === 'active' || r.status === '');
  const roomMap = Object.fromEntries(cityRooms.map(r => [r.room_id, r.name]));
  const userMap = Object.fromEntries(users.map(u => [u.user_id, u.name]));

  // Filtered bookings
  let filtered = [...bookings];
  if (filterDate) filtered = filtered.filter(b => b.start_time?.slice(0, 10) === filterDate);
  if (filterRoom) filtered = filtered.filter(b => b.room_id === filterRoom);
  if (filterStatus) filtered = filtered.filter(b => b.status === filterStatus);

  const confirmedN = filtered.filter(b => b.status === 'confirmed').length;
  const cancelledN = filtered.filter(b => b.status === 'cancelled').length;

  const handleCancel = async () => {
    if (!cancelTarget) return;
    try {
      await cancelBooking(cancelTarget.booking_id);
      setCancelTarget(null);
      reload();
    } catch (e) {
      alert(e.detail || e.message);
    }
  };

  const handleReschedule = async () => {
    if (!rescheduleTarget) return;
    setRescheduleError('');
    const { date, start, end, title } = rescheduleData;
    if (!date || !start || !end) { setRescheduleError('All fields required.'); return; }
    if (start >= end) { setRescheduleError('End must be after start.'); return; }
    try {
      await updateBooking(rescheduleTarget.booking_id, {
        title: title || rescheduleTarget.title,
        start_time: `${date}T${start}:00`,
        end_time: `${date}T${end}:00`,
      });
      setRescheduleTarget(null);
      reload();
    } catch (e) {
      setRescheduleError(e.detail || e.message);
    }
  };

  if (loading) return <div className="text-center py-20 text-slate-500">Loading...</div>;

  const filteredRooms = activeRooms.filter(room => {
    // Search by name or amenities
    const searchMatch =
      room.name.toLowerCase().includes(search.toLowerCase()) ||
      room.amenities?.some(a =>
        a.toLowerCase().includes(search.toLowerCase())
      );

    // Status
    const statusMatch =
      statusFilter === "all" || room.status === statusFilter;

    // Capacity
    const capacityMatch =
      capacityFilter === "any" ||
      (capacityFilter === "small" && room.capacity <= 4) ||
      (capacityFilter === "medium" && room.capacity >= 5 && room.capacity <= 10) ||
      (capacityFilter === "large" && room.capacity > 10);

    // Amenities
    const amenityMatch =
      amenityFilters.length === 0 ||
      amenityFilters.every(a => room.amenities?.includes(a));

    return searchMatch && statusMatch && capacityMatch && amenityMatch;
  });

  return (
    <div className="animate-fade-up">
      <PageHeader title="📅 Book a Room" subtitle="Select a room, pick a time slot, and confirm your booking" />


      {/* Room Cards Grid */}
      <div className="flex gap-6">

        {/* Filters Sidebar */}
        <div className="w-[260px] shrink-0 p-4 rounded-2xl bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-[#1e2a45]">

          <div className="flex items-center justify-between mb-4">
            <span className="font-bold text-indigo-400">⚙ Filters</span>
            <button
              onClick={() => {
                setSearch("");
                setStatusFilter("all");
                setCapacityFilter("any");
                setAmenityFilters([]);
              }}
              className="text-xs text-slate-400 hover:text-rose-400"
            >
              Reset
            </button>
          </div>

          {/* Search */}
          <div className="mb-4">
            <label className="block text-xs text-slate-500 mb-1">SEARCH</label>
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Name or feature..."
              className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm"
            />
          </div>

          {/* Status */}
          <div className="mb-4">
            <label className="block text-xs text-slate-500 mb-1">STATUS</label>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          {/* Capacity */}
          <div className="mb-4">
            <label className="block text-xs text-slate-500 mb-1">CAPACITY</label>
            <select
              value={capacityFilter}
              onChange={e => setCapacityFilter(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm"
            >
              <option value="any">Any</option>
              <option value="small">1–4</option>
              <option value="medium">5–10</option>
              <option value="large">10+</option>
            </select>
          </div>

          {/* Amenities */}
          <div>
            <label className="block text-xs text-slate-500 mb-2">AMENITIES</label>
            <div className="space-y-2">
              {AMENITIES.map(a => (
                <label key={a} className="flex items-center gap-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={amenityFilters.includes(a)}
                    onChange={() =>
                      setAmenityFilters(prev =>
                        prev.includes(a)
                          ? prev.filter(x => x !== a)
                          : [...prev, a]
                      )
                    }
                  />
                  {a}
                </label>
              ))}
            </div>
          </div>
        </div>



        {/* Room Cards Grid */}
        <div className="flex-1">
          <div className="grid grid-cols-3 gap-4 mb-2">
            {filteredRooms.map(room => (
              <RoomCard
                key={room.room_id}
                room={room}
                selected={selectedRoom?.room_id === room.room_id}
                onSelect={r =>
                  setSelectedRoom(
                    selectedRoom?.room_id === r.room_id ? null : r
                  )
                }
              />
            ))}
          </div>

          {filteredRooms.length === 0 && (
            <EmptyState icon="🔍" text="No rooms match the filters." />
          )}
        </div>

      </div>

      {activeRooms.length === 0 && <EmptyState icon="🏗️" text="No active rooms available." />}

      {/* Slot Picker */}
      {selectedRoom && (
        <SlotPicker
          room={selectedRoom}
          onBooked={() => { setSelectedRoom(null); reload(); }}
          onClose={() => setSelectedRoom(null)}
        />
      )}

      {/* Divider */}
      <div className="mt-8 mb-6">
        <div className="h-px bg-gradient-to-r from-transparent via-[#1e2a45] to-transparent" />
      </div>

      <SectionHeader title={isAdmin ? '📋 All Bookings' : '📋 My Bookings'} />

      {/* Cancel Confirm Dialog */}
      {cancelTarget && (
        <div className="mb-4 p-4 rounded-2xl bg-rose-500/5 border border-rose-500/20 animate-fade-in">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-lg">⚠️</span>
            <span className="text-sm text-rose-300">Cancel booking "{cancelTarget.title}"?</span>
          </div>
          <div className="flex gap-2">
            <button onClick={handleCancel}
              className="px-4 py-2 rounded-xl bg-rose-500/15 border border-rose-500/25 text-rose-400 text-sm font-semibold hover:bg-rose-500/25 transition-all">
              ✅ Yes, cancel
            </button>
            <button onClick={() => setCancelTarget(null)}
              className="px-4 py-2 rounded-xl border border-[#1e2a45] text-slate-400 text-sm font-semibold hover:border-slate-500 transition-all">
              ✖ No
            </button>
          </div>
        </div>
      )}

      {/* Reschedule Form */}
      {rescheduleTarget && (
        <div className="mb-4 p-5 rounded-2xl bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-indigo-500/20 animate-fade-in">
          <div className="text-sm font-bold text-slate-100 mb-3">🔄 Reschedule: {rescheduleTarget.title}</div>
          {rescheduleError && (
            <div className="mb-3 px-4 py-2 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-400 text-sm">❌ {rescheduleError}</div>
          )}
          <div className="grid grid-cols-4 gap-3 mb-3">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Title</label>
              <input type="text" value={rescheduleData.title} onChange={e => setRescheduleData(d => ({ ...d, title: e.target.value }))}
                placeholder={rescheduleTarget.title}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Date</label>
              <input type="date" value={rescheduleData.date} onChange={e => setRescheduleData(d => ({ ...d, date: e.target.value }))}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Start</label>
              <input type="time" value={rescheduleData.start} onChange={e => setRescheduleData(d => ({ ...d, start: e.target.value }))}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">End</label>
              <input type="time" value={rescheduleData.end} onChange={e => setRescheduleData(d => ({ ...d, end: e.target.value }))}
                className="w-full px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none" />
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={handleReschedule}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-sm font-bold hover:from-indigo-600 hover:to-purple-600 transition-all">
              💾 Save
            </button>
            <button onClick={() => setRescheduleTarget(null)}
              className="px-4 py-2 rounded-xl border border-[#1e2a45] text-slate-400 text-sm hover:border-rose-500 hover:text-rose-400 transition-all">
              ✖ Cancel
            </button>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <div>
          <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-xs focus:border-indigo-500 outline-none" />
        </div>
        <select value={filterRoom} onChange={e => setFilterRoom(e.target.value)}
          className="px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-xs focus:border-indigo-500 outline-none">
          <option value="">All Rooms</option>
          {cityRooms.map(r => <option key={r.room_id} value={r.room_id}>{r.name}</option>)}
        </select>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
          className="px-3 py-2 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-xs focus:border-indigo-500 outline-none">
          <option value="">All Status</option>
          <option value="confirmed">Confirmed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        {(filterDate || filterRoom || filterStatus) && (
          <button onClick={() => { setFilterDate(''); setFilterRoom(''); setFilterStatus(''); }}
            className="px-3 py-2 rounded-xl border border-[#1e2a45] text-slate-400 text-xs hover:text-rose-400 hover:border-rose-500 transition-all">
            ✖ Clear
          </button>
        )}
      </div>

      {/* Summary bar */}
      <div className="flex gap-6 mb-4 px-4 py-3 bg-[#0f1420] border border-[#1e2a45] rounded-xl">
        <span className="text-xs text-slate-500"><span className="text-slate-100 font-bold">{filtered.length}</span> results</span>
        <span className="text-xs text-slate-500"><span className="text-emerald-400 font-bold">{confirmedN}</span> confirmed</span>
        <span className="text-xs text-slate-500"><span className="text-rose-400 font-bold">{cancelledN}</span> cancelled</span>
      </div>

      {/* Booking list */}
      {filtered.length === 0 ? (
        <EmptyState icon="📭" text="No bookings found." />
      ) : (
        filtered.map(b => {
          const canModify = isAdmin || b.user_id === user?.user_id;
          return (
            <BookingCard
              key={b.booking_id}
              booking={b}
              roomName={roomMap[b.room_id] || ''}
              userName={userMap[b.user_id] || ''}
              onCancel={canModify ? (bk) => setCancelTarget(bk) : undefined}
              onReschedule={canModify ? (bk) => {
                setRescheduleTarget(bk);
                setRescheduleData({
                  title: bk.title,
                  date: bk.start_time?.slice(0, 10) || '',
                  start: bk.start_time?.slice(11, 16) || '',
                  end: bk.end_time?.slice(11, 16) || '',
                });
                setRescheduleError('');
              } : undefined}
              onCheckIn={canModify ? handleCheckIn : undefined}
              onCheckOut={canModify ? handleCheckOut : undefined}
            />
          );
        })
      )}
    </div>
  );
}
