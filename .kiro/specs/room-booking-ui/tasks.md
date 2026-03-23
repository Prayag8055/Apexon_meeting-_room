# Implementation Tasks: Room Booking UI

## Phase 1: Project Scaffold

- [x] 1.1 Create `streamlit_app/` directory structure
  - `streamlit_app/app.py`
  - `streamlit_app/api_client.py`
  - `streamlit_app/theme.py`
  - `streamlit_app/pages/__init__.py`
  - `streamlit_app/pages/dashboard.py`
  - `streamlit_app/pages/rooms.py`
  - `streamlit_app/pages/bookings.py`
  - `streamlit_app/pages/users.py`
  - `streamlit_app/components/__init__.py`
  - `streamlit_app/components/cards.py`
  - `streamlit_app/components/forms.py`

- [x] 1.2 Create `streamlit_app/requirements.txt` with:
  - `streamlit>=1.32`
  - `requests`
  - `python-dateutil`

## Phase 2: Theme & CSS

- [x] 2.1 Implement `theme.py`
  - Define `COLORS`, `TYPOGRAPHY`, `SPACING`, `RADIUS`, `TRANSITION`, `SHADOW` constants
  - Implement `inject_css()` — injects full CSS block via `st.markdown`
  - Implement `badge_html(label, variant)` — returns HTML for status badges
  - Implement `card_html(content, extra_class)` — wraps content in `.rb-card` div

- [x] 2.2 Write CSS covering:
  - `.rb-card` base + hover (translateY, border-color, box-shadow)
  - `.rb-stat-card`, `.rb-stat-value`, `.rb-stat-label`
  - `.rb-badge` variants: confirmed, cancelled, active, inactive
  - `.rb-nav-item` active/hover states
  - `.rb-slot-free` and `.rb-slot-booked` for availability grid
  - `.rb-skeleton` shimmer animation
  - `.rb-page` fade-in animation
  - Streamlit overrides: sidebar background, button styles

## Phase 3: API Client

- [x] 3.1 Implement `api_client.py`
  - Define `BASE_URL` from env var `API_BASE_URL` (default `http://localhost:8000`)
  - Define `APIError(Exception)` with `status_code`, `message`, `detail`
  - Implement `_get(path, params)`, `_post(path, payload)`, `_put(path, payload)`, `_delete(path)` private helpers
    - All helpers: set 5s timeout, raise `APIError` on non-2xx, parse JSON error body
  - Implement all public functions per design: `health_check`, `get_rooms`, `get_room`, `create_room`, `update_room`, `deactivate_room`, `get_room_availability`, `get_bookings`, `get_booking`, `create_booking`, `update_booking`, `cancel_booking`, `get_users`, `get_user`, `create_user`, `get_user_bookings`
  - Apply `@st.cache_data(ttl=30)` to `get_rooms` and `get_users`

- [ ] 3.2 Write unit tests for `api_client.py` in `streamlit_app/tests/test_api_client.py`
  - Mock `requests` session; test URL construction, query param serialization
  - Test `APIError` raised on 404, 409, 422, 500 responses
  - Test successful response parsing for each endpoint

## Phase 4: Reusable Components

- [x] 4.1 Implement `components/cards.py`
  - `stat_card(label, value, icon, color)` — renders KPI tile using `st.markdown` with `.rb-stat-card` HTML
  - `room_card(room, on_edit, on_deactivate)` — renders room info + amenity badges + action buttons
  - `booking_card(booking, room_name, user_name, on_cancel, on_reschedule)` — renders booking info + status badge + action buttons
  - `user_card(user, booking_count, on_view)` — renders user info + booking count
  - `availability_grid(availability)` — renders time-slot grid with free/booked coloring

- [x] 4.2 Implement `components/forms.py`
  - `room_form(existing)` — name, floor, capacity, amenities multiselect, status select; returns dict or None
  - `booking_form(rooms, users, existing)` — room select, user select, title, date, start/end time, attendees, notes; returns dict or None
  - `user_form(existing)` — name, email, department; returns dict or None
  - `confirm_dialog(message, key)` — inline Yes/Cancel prompt; returns bool

## Phase 5: Pages

- [x] 5.1 Implement `pages/dashboard.py`
  - Fetch rooms, bookings, users with `st.spinner`
  - Render 4-column KPI row using `stat_card`
  - Render recent bookings list (last 5, sorted by `created_at`)
  - Render room status mini-list in right column

- [x] 5.2 Implement `pages/rooms.py`
  - Header row with "+ New Room" button
  - Collapsible create-room form using `room_form()`; handle `APIError` inline
  - Collapsible filter panel (capacity, floor, amenities)
  - 3-column grid of `room_card` components
  - Edit room: open form pre-populated with existing data; call `update_room` on submit
  - Deactivate room: `confirm_dialog` → `deactivate_room`
  - Availability section: room selectbox + date picker → `availability_grid`

- [x] 5.3 Implement `pages/bookings.py`
  - Header row with "+ New Booking" button
  - Collapsible create-booking form using `booking_form(rooms, users)`; handle 409 conflict inline
  - Filter panel (date, room, user, status)
  - List of `booking_card` components
  - Cancel: `confirm_dialog` → `cancel_booking` → `st.rerun()`
  - Reschedule: open `booking_form(existing=booking)` → `update_booking`

- [x] 5.4 Implement `pages/users.py`
  - Header row with "+ Register User" button
  - Collapsible register-user form using `user_form()`; handle 409 duplicate email inline
  - 3-column grid of `user_card` components
  - User bookings drawer: clicking "View Bookings" sets `st.session_state.selected_user`; renders `booking_card` list below grid

## Phase 6: Entry Point

- [x] 6.1 Implement `app.py`
  - `st.set_page_config(page_title="Room Booking", layout="wide")`
  - Call `inject_css()` on every render
  - Sidebar: logo/title, nav buttons (Dashboard, Rooms, Bookings, Users), API health indicator
  - Session state routing: `st.session_state.page` → call appropriate `render_*()` function
  - Wrap all page renders in try/except `requests.exceptions.ConnectionError` → `st.error("Cannot connect to API")`

## Phase 7: Polish & Testing

- [x] 7.1 Add `@st.cache_data.clear()` calls after all write operations (create/update/delete) to invalidate stale room/user caches

- [x] 7.2 Verify all `st.spinner("...")` wrappers are present on every API call

- [ ] 7.3 Add `streamlit_app/tests/test_theme.py`
  - Test `badge_html` returns correct CSS class for each variant
  - Test `card_html` wraps content in `.rb-card`

- [ ] 7.4 Manual smoke test checklist:
  - [ ] Dashboard loads with correct counts
  - [ ] Create room → appears in room grid
  - [ ] Edit room → changes reflected
  - [ ] Deactivate room → status badge updates
  - [ ] View availability → grid renders free/booked slots
  - [ ] Create booking → appears in bookings list
  - [ ] Create conflicting booking → 409 error shown inline
  - [ ] Cancel booking → status updates to cancelled
  - [ ] Reschedule booking → new time reflected
  - [ ] Register user → appears in user grid
  - [ ] View user bookings → correct bookings shown
  - [ ] API unreachable → error shown in sidebar and page
