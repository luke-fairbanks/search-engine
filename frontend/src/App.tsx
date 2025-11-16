import React, { useState } from 'react';
import { NextUIProvider } from '@nextui-org/react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import SearchPage from './components/SearchPage';
import CrawlPage from './components/CrawlPage';
import Sidebar from './components/Sidebar';
import BackendStatus from './components/BackendStatus';

function AppContent() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const currentPage = location.pathname === '/crawler' ? 'crawl' : 'search';

  const handleNavigate = (page: 'search' | 'crawl') => {
    navigate(page === 'search' ? '/' : '/crawler');
  };

  return (
    <NextUIProvider>
      <div className="dark text-foreground bg-slate-900 min-h-screen">
        {/* Backend Status Banner */}
        <BackendStatus onStatusChange={setIsBackendOnline} />
        
        {/* Header Bar with Hamburger Menu */}
        <div className="fixed top-0 left-0 right-0 z-20 flex items-center px-6 py-4 bg-slate-900/50 backdrop-blur-xl border-b border-slate-700/30">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 bg-slate-800/80 backdrop-blur-xl border border-slate-700/50 rounded-xl hover:bg-slate-700/80 transition-all duration-200 shadow-lg hover:shadow-blue-500/20"
          >
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="ml-4 text-sm font-semibold text-slate-400">
            {currentPage === 'search' ? '🔍 Search' : '🕷️ Crawler'}
          </div>
        </div>

        {/* Sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          currentPage={currentPage}
          onNavigate={handleNavigate}
        />

        {/* Main Content with top padding to account for header */}
        <div className="pt-20">
          <Routes>
            <Route path="/" element={<SearchPage />} />
            <Route path="/crawler" element={<CrawlPage />} />
          </Routes>
        </div>
      </div>
    </NextUIProvider>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
