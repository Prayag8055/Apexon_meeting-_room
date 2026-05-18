import { Badge } from './ui';

export default function BookingCard({ booking, roomName, userName, onCancel, onReschedule, onCheckIn, onCheckOut }) {
  const { title, status, start_time, end_time, notes, actual_check_in, actual_check_out } = booking;
  const date = start_time?.slice(0, 10) || '';
  const sTime = start_time?.slice(11, 16) || '';
  const eTime = end_time?.slice(11, 16) || '';

  let duration = '';
  try {
    const mins = (new Date(end_time) - new Date(start_time)) / 60000;
    duration = mins >= 60 ? `${Math.floor(mins / 60)}h${mins % 60 ? mins % 60 + 'm' : ''}` : `${mins}m`;
  } catch { }

  const accent = status === 'confirmed' ? '#10b981' : '#f43f5e';

  return (
    <div className="flex items-center gap-4 bg-gradient-to-br from-[#0f1420] to-[#161c2e] border border-[#1e2a45] rounded-2xl p-4 mb-2 transition-all hover:border-[#2d3f6b] hover:translate-x-1 group">
      {/* Accent bar */}
      <div className="w-1 self-stretch rounded-full flex-shrink-0" style={{ background: accent }} />

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="text-sm font-semibold text-slate-100 truncate">{title || 'Booking'}</div>
          <Badge status={status} />
        </div>
        <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-slate-500">
          <span className="flex items-center gap-1">🏢 {roomName}</span>
          <span className="flex items-center gap-1">👤 {userName}</span>
          <span className="flex items-center gap-1">📅 {date}</span>
          <span className="flex items-center gap-1">🕐 {sTime} – {eTime}</span>
          {duration && <span className="flex items-center gap-1">⏱️ {duration}</span>}
        </div>
        {notes && (
          <div className="text-xs text-slate-600 mt-1.5 italic truncate">"{notes}"</div>
        )}
      </div>

      {/* Actions */}
      {status === 'confirmed' && (onCancel || onReschedule) && (
        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
          {onCheckIn && !actual_check_in && (
            <button onClick={() => onCheckIn(booking)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/10 transition-all">
              ⏱️ Check In
            </button>
          )}
          {onCheckOut && actual_check_in && !actual_check_out && (
            <button onClick={() => onCheckOut(booking)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-yellow-500/20 text-yellow-400 hover:bg-yellow-500/10 transition-all">
              🚪 Check Out
            </button>
          )}
          {onReschedule && (
            <button onClick={() => onReschedule(booking)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-[#1e2a45] text-slate-400 hover:border-indigo-500 hover:text-indigo-300 transition-all">
              🔄 Reschedule
            </button>
          )}
          {onCancel && (
            <button onClick={() => onCancel(booking)}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-rose-500/20 text-rose-400 hover:bg-rose-500/10 transition-all">
              ✖ Cancel
            </button>
          )}
        </div>
      )}
    </div>
  );
}
