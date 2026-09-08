import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CompanyProfile from "./pages/CompanyProfile";
import Search from "./pages/Search";

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
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/search" element={<Search />} />
            <Route path="/companies/:id" element={<CompanyProfile />} />
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
