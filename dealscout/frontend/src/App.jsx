import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CompanyProfile from "./pages/CompanyProfile";
import Search from "./pages/Search";
import Login from "./pages/Login";
import { isAuthenticated, setToken, removeToken, getToken } from "./api/companies";

function requireAuth({ children }) {
  const [ready, setReady] = useState(false);
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    const token = getToken();
    setAuthed(!!token);
    setReady(true);
  }, []);

  if (!ready) return null;
  if (!authed) return <Navigate to="/login" replace={true} />;
  return children;
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
        {/* Navigation Bar */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <Link to="/" className="flex items-center space-x-2">
                <span className="text-xl font-black tracking-tight text-blue-600">DealScout</span>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-bold">M&A Intel</span>
              </Link>
              <nav className="flex space-x-4 text-sm font-medium text-gray-600">
                <Link to="/" className="hover:text-blue-600 transition-colors">Dashboard</Link>
                <Link to="/search" className="hover:text-blue-600 transition-colors">Recherche Cibles</Link>
              </nav>
            </div>
            <div className="flex items-center space-x-3 text-xs text-gray-500">
              <span className="inline-block w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>API Connectée</span>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated() ? (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Connecté</span>
                  <button
                    onClick={() => {
                      removeToken();
                      window.location.reload();
                    }}
                    className="text-xs bg-red-50 text-red-600 px-2 py-1 rounded hover:bg-red-100 transition-colors"
                  >
                    Déconnexion
                  </button>
                </div>
              ) : (
                <Link to="/login" className="px-3 py-1.5 text-sm font-medium text-blue-600 border border-blue-200 rounded hover:bg-blue-50 transition-colors">
                  Se connecter
                </Link>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <requireAuth>
                  <Dashboard />
                </requireAuth>
              }
            />
            <Route
              path="/search"
              element={
                <requireAuth>
                  <Search />
                </requireAuth>
              }
            />
            <Route
              path="/companies/:id"
              element={
                <requireAuth>
                  <CompanyProfile />
                </requireAuth>
              }
            />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 py-4 text-center text-xs text-gray-400">
          DealScout &mdash; Investment & M&A Intelligence Platform &bull; Data Lakehouse Medallion
        </footer>
      </div>
    </BrowserRouter>
  );
}
