import { useState, useEffect } from 'react';
import { getRoomAvailability, createBooking } from '../api';
import { useAuth } from '../AuthContext';
import { format } from 'date-fns';

export default function SlotPicker({ room, onBooked, onClose }) {
  const { user } = useAuth();
  const [date, setDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [title, setTitle] = useState('');
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [ibStart, setIbStart] = useState(null);
  const [ibEnd, setIbEnd] = useState(null)

  useEffect(() => {
    setLoading(true);
    setSelectedSlot(null);
    setError('');
    setSuccess('');
    getRoomAvailability(room.room_id, date)
      .then(data => {
        let free = (data.slots || []).filter(s => s.is_available);
        // Filter past slots for today
        const today = format(new Date(), 'yyyy-MM-dd');
        if (date === today) {
          const now = format(new Date(), 'HH:mm');
          free = free.filter(s => s.start_time.slice(11, 16) >= now);
        }
        setSlots(free);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [room.room_id, date]);

  const handleConfirm = async () => {
    if (!selectedSlot) return;
    setBooking(true);
    setError('');
    try {
      await createBooking({
        title: title.trim() || 'Meeting',
        room_id: room.room_id,
        user_id: user.user_id,
        start_time: selectedSlot.start_time,
        end_time: selectedSlot.end_time,
        notes: '',
      });
      setSuccess(`Booked! ${room.name} at ${selectedSlot.start_time.slice(11, 16)}`);
      setSelectedSlot(null);
      setTitle('');
      setTimeout(() => { onBooked?.(); }, 800);
    } catch (e) {
      setError(e.status === 409 ? 'Slot just got taken. Pick another.' : (e.detail || e.message));
    } finally { setBooking(false); }
  };

  const buildDateTime = (date, time) => `${date}T${time}:00`;

  return (
    <div className="animate-fade-up mt-4">
      <div className="h-px bg-gradient-to-r from-transparent via-indigo-500 to-transparent mb-5" />

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          ⚡ Pick a Time Slot — {room.name}
        </h3>
        <button onClick={onClose}
          className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-[#1e2a45] text-slate-400 hover:border-rose-500 hover:text-rose-400 transition-all">
          ✖ Close
        </button>
      </div>

      {/* Date picker */}
      <div className="mb-4">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Date</label>
        <input type="date" value={date} onChange={e => setDate(e.target.value)}
          className="px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none transition-all" />
      </div>

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
                setIbStart(buildDateTime(date, e.target.value))
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
                setIbEnd(buildDateTime(date, e.target.value))
              }
              className="bg-transparent w-full text-slate-100 text-sm outline-none"
            />
          </div>
        </div>

      </div>

      {error && (
        <div className="mb-3 px-4 py-2 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-400 text-sm">❌ {error}</div>
      )}
      {success && (
        <div className="mb-3 px-4 py-2 rounded-xl bg-emerald-500/8 border border-emerald-500/20 text-emerald-400 text-sm">✅ {success}</div>
      )}

      {loading ? (
        <div className="text-center py-8 text-slate-500 text-sm">Loading slots...</div>
      ) : slots.length === 0 ? (
        <div className="text-center py-8 text-slate-500 text-sm">No available slots for this date. Try another date.</div>
      ) : (
        <>
          <div className="text-xs text-slate-500 mb-3">
            🟢 {slots.length} available slots — click one to book
          </div>
          <div className="grid grid-cols-6 sm:grid-cols-8 gap-2 mb-4">
            {slots.map((slot, i) => {
              const t = slot.start_time.slice(11, 16);
              const picked = selectedSlot?.start_time === slot.start_time;
              return (
                <button key={i} onClick={() => setSelectedSlot(slot)}
                  className={`py-2 rounded-xl text-xs font-bold transition-all ${picked
                    ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/25 scale-105'
                    : 'bg-[#0f1420] border border-[#1e2a45] text-slate-400 hover:border-indigo-500 hover:text-indigo-300 hover:bg-indigo-500/5'
                    }`}>
                  {t}
                </button>
              );
            })}
          </div>
        </>
      )}

      {/* Confirm form */}
      {ibStart && ibEnd && (
        <div className="animate-fade-in">
          <div className="px-4 py-3 rounded-xl bg-emerald-500/8 border border-emerald-500/20 mb-4">
            <div className="text-sm font-semibold text-emerald-400">
              📅 {room.name} · {date} · {ibStart.slice(11, 16)} – {ibEnd.slice(11, 16)}
            </div>
          </div>
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Meeting Title</label>
              <input type="text" value={title} onChange={e => setTitle(e.target.value)}
                placeholder="e.g. Sprint Planning"
                className="w-full px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm placeholder-slate-600 focus:border-indigo-500 outline-none transition-all" />
            </div>
            <button onClick={handleConfirm} disabled={booking}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold text-sm hover:from-emerald-600 hover:to-teal-600 transition-all hover:-translate-y-0.5 hover:shadow-lg hover:shadow-emerald-500/25 disabled:opacity-50 whitespace-nowrap">
              {booking ? '⏳...' : '✅ Confirm Booking'}
            </button>
            <button onClick={() => setSelectedSlot(null)}
              className="px-4 py-2.5 rounded-xl border border-[#1e2a45] text-slate-400 text-sm hover:border-rose-500 hover:text-rose-400 transition-all">
              ✖
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
