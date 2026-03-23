"""Login & Registration page."""
from __future__ import annotations
import streamlit as st
from api_client import login_user_auth, register_user_auth, APIError

DEPARTMENT_OPTIONS = [
    "", "Engineering", "Design", "Product", "Marketing", "Sales",
    "HR", "Finance", "Operations", "Legal", "Support", "Other",
]


def render_login() -> bool:
    """Render login/register UI. Returns True if user is now logged in."""
    st.markdown(
        """
        <div style="text-align:center;padding:2rem 0 1rem">
            <div style="display:inline-flex;align-items:center;gap:0.6rem;margin-bottom:0.5rem">
                <div style="width:48px;height:48px;border-radius:0.75rem;
                            background:linear-gradient(135deg,#6366f1,#8b5cf6);
                            display:flex;align-items:center;justify-content:center;
                            font-size:1.5rem">🏢</div>
            </div>
            <div style="font-size:1.5rem;font-weight:800;
                        background:linear-gradient(135deg,#818cf8,#c084fc);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        background-clip:text">Apexon RoomBook</div>
            <div style="font-size:0.8rem;color:#8892b0;margin-top:0.25rem">
                Meeting Room Booking System</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        _render_login_form()

    with tab_register:
        _render_register_form()

    return "user" in st.session_state and st.session_state["user"] is not None


def _render_login_form():
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@apexon.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        submitted = st.form_submit_button("🔑 Sign In", use_container_width=True)
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
                return
            try:
                user = login_user_auth(email.strip(), password)
                st.session_state["user"] = user
                st.rerun()
            except APIError as e:
                if e.status_code == 401:
                    st.error("❌ Invalid email or password. Please try again.")
                else:
                    st.error(f"❌ {e}")


def _render_register_form():
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=True):
        rc1, rc2 = st.columns(2)
        name = rc1.text_input("Full Name", placeholder="e.g. Alex Johnson", key="reg_name")
        email = rc2.text_input("Email", placeholder="you@apexon.com", key="reg_email")
        rc3, rc4 = st.columns(2)
        password = rc3.text_input("Password", type="password", placeholder="Min 4 characters", key="reg_password")
        department = rc4.selectbox("Department", options=DEPARTMENT_OPTIONS,
                                   format_func=lambda x: x if x else "Select department...", key="reg_dept")
        submitted = st.form_submit_button("📝 Create Account", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Full name is required.")
                return
            if not email.strip() or "@" not in email:
                st.error("A valid email is required.")
                return
            if not password or len(password) < 4:
                st.error("Password must be at least 4 characters.")
                return
            try:
                user = register_user_auth(
                    name=name.strip(), email=email.strip(),
                    password=password, department=department or "",
                )
                st.session_state["user"] = user
                st.success("✅ Account created! You're now logged in.")
                st.rerun()
            except APIError as e:
                if e.status_code == 409:
                    st.error("⚠️ This email is already registered. Please login instead.")
                else:
                    st.error(f"❌ {e}")
