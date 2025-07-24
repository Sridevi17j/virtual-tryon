import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import TryOnPage from './pages/TryOnPage';
import ResultsPage from './pages/ResultsPage';
import AboutPage from './pages/AboutPage';
import { ToastProvider } from './components/Toast';

function App() {
  return (
    <ToastProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/try-on" element={<TryOnPage />} />
              <Route path="/results/:jobId" element={<ResultsPage />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </ToastProvider>
  );
}

export default App;