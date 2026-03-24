import { useState, useEffect, useCallback } from 'react';
import { getRooms, createRoom, updateRoom, deactivateRoom, getRoomAvailability } from '../api';
import { PageHeader, SectionHeader, EmptyState, Input, Select, Button } from '../components/ui';
import RoomCard from '../components/RoomCard';

const AMENITIES = ['Projector', 'Whiteboard', 'Video Conferencing', 'TV Screen', 'Phone', 'Standing Desk', 'Natural Light', 'Air Conditioning'];

function RoomForm({ existing, onSave, onCancel }) {
  const [name, setName] = useState(existing?.name || '');
  const [capacity, setCapacity] = useState(existing?.capacity || 10);
  const [floor, setFloor] = useState(existing?.floor || 1);
  const [status, setStatus] = useState(existing?.status || 'active');
  const [amenities, setAmenities] = useState(existing?.amenities || []);
  const [error, setError] = useState('');

  const toggle = (a) => setAmenities(prev => prev.includes(a) ? prev.filter(x => x !== a) : [...prev, a]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Room name is required.'); return; }
    onSave({ name: name.trim(), capacity: Number(capacity), floor: Number(floor), amenities, status });
  };

  return (
    <div className="p-5 rounded-2xl bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-[#1e2a45] mb-4 relative">
      <div className="absolute top-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-indigo-500 to-transparent" />
      <h3 className="text-base font-bold text-slate-100 mb-4">{existing ? '✏️ Edit Room' : '🏢 New Room'}</h3>
      {error && <div className="mb-3 px-4 py-2 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-400 text-sm">❌ {error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <Input label="Room Name" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Horizon Suite" />
          <Input label="Capacity" type="number" min="1" value={capacity} onChange={e => setCapacity(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <Input label="Floor" type="number" min="0" value={floor} onChange={e => setFloor(e.target.value)} />
          {existing && (
            <Select label="Status" value={status} onChange={e => setStatus(e.target.value)}
              options={[{ value: 'active', label: 'Active' }, { value: 'inactive', label: 'Inactive' }]} />
          )}
        </div>
        <div className="mb-4">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Amenities</label>
          <div className="flex flex-wrap gap-2">
            {AMENITIES.map(a => (
              <button key={a} type="button" onClick={() => toggle(a)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  amenities.includes(a)
                    ? 'bg-indigo-500/15 border border-indigo-500/30 text-indigo-300'
                    : 'bg-[#0a0f1e] border border-[#1e2a45] text-slate-500 hover:border-indigo-500/30 hover:text-indigo-400'
                }`}>
                {a}
              </button>
            ))}
          </div>
        </div>
        <div className="flex gap-2">
          <Button type="submit">{existing ? '💾 Save Room' : '✅ Create Room'}</Button>
          <Button variant="secondary" type="button" onClick={onCancel}>✖ Cancel</Button>
        </div>
      </form>
    </div>
  );
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editRoom, setEditRoom] = useState(null);
  const [error, setError] = useState('');

  // Availability viewer
  const [availRoom, setAvailRoom] = useState('');
  const [availDate, setAvailDate] = useState(new Date().toISOString().slice(0, 10));
  const [availData, setAvailData] = useState(null);

  const reload = useCallback(() => {
    setLoading(true);
    getRooms().then(setRooms).finally(() => setLoading(false));
  }, []);

  useEffect(reload, [reload]);

  const handleCreate = async (data) => {
    try { await createRoom(data); setShowForm(false); reload(); }
    catch (e) { setError(e.detail || e.message); }
  };

  const handleUpdate = async (data) => {
    try { await updateRoom(editRoom.room_id, data); setEditRoom(null); reload(); }
    catch (e) { setError(e.detail || e.message); }
  };

  const handleDeactivate = async (room) => {
    if (!confirm(`Deactivate "${room.name}"?`)) return;
    try { await deactivateRoom(room.room_id); reload(); }
    catch (e) { alert(e.detail || e.message); }
  };

  const loadAvailability = async () => {
    if (!availRoom || !availDate) return;
    try {
      const data = await getRoomAvailability(availRoom, availDate);
      setAvailData(data);
    } catch (e) { alert(e.detail || e.message); }
  };

  useEffect(() => { if (availRoom) loadAvailability(); }, [availRoom, availDate]);

  if (loading) return <div className="text-center py-20 text-slate-500">Loading...</div>;

  const activeRooms = rooms.filter(r => r.status === 'active');

  return (
    <div className="animate-fade-up">
      <div className="flex items-start justify-between mb-6">
        <PageHeader title="🏢 Meeting Rooms" subtitle="Manage your workspace rooms, amenities, and availability" />
        <Button onClick={() => { setShowForm(!showForm); setEditRoom(null); }}>＋ New Room</Button>
      </div>

      {error && <div className="mb-4 px-4 py-2 rounded-xl bg-rose-500/8 border border-rose-500/20 text-rose-400 text-sm">❌ {error}</div>}

      {showForm && <RoomForm onSave={handleCreate} onCancel={() => setShowForm(false)} />}
      {editRoom && <RoomForm existing={editRoom} onSave={handleUpdate} onCancel={() => setEditRoom(null)} />}

      {/* Summary */}
      <div className="flex gap-6 mb-5 px-4 py-3 bg-[#0f1420] border border-[#1e2a45] rounded-xl">
        <span className="text-xs text-slate-500"><span className="text-slate-100 font-bold">{rooms.length}</span> rooms</span>
        <span className="text-xs text-slate-500"><span className="text-emerald-400 font-bold">{activeRooms.length}</span> active</span>
        <span className="text-xs text-slate-500"><span className="text-rose-400 font-bold">{rooms.length - activeRooms.length}</span> inactive</span>
        <span className="text-xs text-slate-500"><span className="text-indigo-400 font-bold">{rooms.reduce((s, r) => s + r.capacity, 0)}</span> total seats</span>
      </div>

      {/* Room grid */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {rooms.map(room => (
          <RoomCard key={room.room_id} room={room}
            actions={
              <div className="flex gap-2 flex-1">
                <button onClick={() => { setEditRoom(room); setShowForm(false); }}
                  className="flex-1 py-2 rounded-xl text-xs font-semibold border border-[#1e2a45] text-slate-400 hover:border-indigo-500 hover:text-indigo-300 transition-all">
                  ✏️ Edit
                </button>
                {room.status === 'active' && (
                  <button onClick={() => handleDeactivate(room)}
                    className="flex-1 py-2 rounded-xl text-xs font-semibold border border-rose-500/20 text-rose-400 hover:bg-rose-500/10 transition-all">
                    🗑️ Deactivate
                  </button>
                )}
              </div>
            }
          />
        ))}
      </div>

      {rooms.length === 0 && <EmptyState icon="🏗️" text="No rooms yet. Create your first room!" />}

      {/* Availability Viewer */}
      <div className="h-px bg-gradient-to-r from-transparent via-[#1e2a45] to-transparent mb-6" />
      <SectionHeader title="📅 Room Availability" />
      <div className="grid grid-cols-2 gap-3 mb-4">
        <select value={availRoom} onChange={e => setAvailRoom(e.target.value)}
          className="px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none">
          <option value="">Select room...</option>
          {activeRooms.map(r => <option key={r.room_id} value={r.room_id}>{r.name}</option>)}
        </select>
        <input type="date" value={availDate} onChange={e => setAvailDate(e.target.value)}
          className="px-4 py-2.5 rounded-xl bg-[#0a0f1e] border border-[#1e2a45] text-slate-100 text-sm focus:border-indigo-500 outline-none" />
      </div>

      {availData && (
        <div>
          {(() => {
            const slots = availData.slots || [];
            const free = slots.filter(s => s.is_available).length;
            const pct = slots.length ? Math.round(free / slots.length * 100) : 0;
            return (
              <>
                <div className="flex items-center gap-4 mb-4 px-4 py-3 bg-[#0f1420] border border-[#1e2a45] rounded-xl">
                  <div className="flex-1">
                    <div className="text-xs text-slate-500 mb-1">Availability — {free} of {slots.length} slots free</div>
                    <div className="h-1.5 bg-[#1e2a45] rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-emerald-400">{pct}%</div>
                    <div className="text-[0.6rem] text-slate-600">available</div>
                  </div>
                </div>
                <div className="grid grid-cols-8 gap-2">
                  {slots.map((s, i) => {
                    const t = s.start_time?.slice(11, 16);
                    return (
                      <div key={i} className={`py-2 rounded-xl text-center text-xs font-bold transition-all ${
                        s.is_available
                          ? 'bg-emerald-500/8 border border-emerald-500/25 text-emerald-400'
                          : 'bg-rose-500/8 border border-rose-500/20 text-rose-400'
                      }`}>
                        <div>{t}</div>
                        <div className="text-[0.6rem] opacity-70 mt-0.5">{s.is_available ? 'Available' : (s.booking_title || 'Booked').slice(0, 10)}</div>
                      </div>
                    );
                  })}
                </div>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}
