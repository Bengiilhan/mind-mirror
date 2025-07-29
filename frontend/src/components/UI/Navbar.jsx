import { Link } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="flex items-center justify-between px-4 py-3 bg-white dark:bg-gray-800 shadow-md">
      <div className="font-bold text-xl text-blue-600 dark:text-blue-300">Mind Mirror</div>
      <div className="flex gap-4">
        {isAuthenticated && (
          <>
            <Link to="/new-entry" className="px-3 py-1 rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition">Yeni Yazı</Link>
            <Link to="/archive" className="px-3 py-1 rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition">Arşiv</Link>
            <Link to="/stats" className="px-3 py-1 rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition">İstatistik</Link>
            <button onClick={logout} className="px-3 py-1 rounded text-red-500 hover:bg-red-100 dark:hover:bg-gray-700 transition">Çıkış</button>
          </>
        )}
        {!isAuthenticated && (
          <>
            <Link to="/login" className="px-3 py-1 rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition">Giriş</Link>
            <Link to="/register" className="px-3 py-1 rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition">Kayıt Ol</Link>
          </>
        )}
      </div>
    </nav>
  );
}
