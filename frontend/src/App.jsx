import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import './App.css'
import ChatPage from './components/ChatPage'
import DocumentUpload from './components/DocumentUpload'
import StatusIndicator from './components/StatusIndicator'
import { checkHealth } from './services/api'

function Navigation() {
  const location = useLocation()
  const [isHealthy, setIsHealthy] = useState(null)

  useEffect(() => {
    checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false))
    
    const interval = setInterval(() => {
      checkHealth()
        .then(() => setIsHealthy(true))
        .catch(() => setIsHealthy(false))
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  return (
    <header className="app-header">
      <div className="header-content">
        <h1>⛽ Total Energies Fuel Management</h1>
        <StatusIndicator isHealthy={isHealthy} />
      </div>
      <nav className="main-nav">
        <Link 
          to="/" 
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          💬 Chat
        </Link>
        <Link 
          to="/documents" 
          className={`nav-link ${location.pathname === '/documents' ? 'active' : ''}`}
        >
          📄 Documents
        </Link>
      </nav>
      <p className="subtitle">Système de gestion de carburant Total Energies - Powered by LangGraph with RAG, SQL, and Data Analysis</p>
    </header>
  )
}

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/documents" element={<DocumentUpload />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

