import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import { useTheme } from "./ThemeContext"; // ✅ ADD THIS
import { useEffect } from "react"; // ✅ ADD THIS

import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import BookingsPage from './pages/BookingsPage';
import RoomsPage from './pages/RoomsPage';
import UsersPage from './pages/UsersPage';

function ProtectedRoutes() {
  const { user, isAdmin } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/bookings" element={<BookingsPage />} />
        {isAdmin && <Route path="/rooms" element={<RoomsPage />} />}
        {isAdmin && <Route path="/users" element={<UsersPage />} />}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export default function App() {
  const { theme } = useTheme(); // ✅ get theme

  return (
    <div
      className={`min-h-screen ${theme === "dark"
        ? "bg-[#0a0f1e] text-white"
        : "bg-white text-black"
        }`}
    >
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/*" element={<ProtectedRoutes />} />
        </Routes>
      </AuthProvider>
    </div>
  );
}