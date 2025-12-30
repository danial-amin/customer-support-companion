import React, { useState } from 'react'
import './App.css'
import ChatInterface from './components/ChatInterface'
import AgentSelector from './components/AgentSelector'
import StatusIndicator from './components/StatusIndicator'
import { queryAPI, checkHealth } from './services/api'

function App() {
  const [selectedAgent, setSelectedAgent] = useState('auto')
  const [isHealthy, setIsHealthy] = useState(null)
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)

  React.useEffect(() => {
    // Check health on mount
    checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false))
    
    // Periodic health check
    const interval = setInterval(() => {
      checkHealth()
        .then(() => setIsHealthy(true))
        .catch(() => setIsHealthy(false))
    }, 30000) // Every 30 seconds

    return () => clearInterval(interval)
  }, [])

  const handleSendMessage = async (message) => {
    if (!message.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await queryAPI(message, selectedAgent)
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.answer,
        agent: response.agent_used,
        metadata: response.metadata,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: error.message || 'An error occurred while processing your request',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 Customer Support AI</h1>
          <StatusIndicator isHealthy={isHealthy} />
        </div>
        <p className="subtitle">Powered by LangGraph with RAG, SQL, and Data Analysis</p>
      </header>

      <main className="app-main">
        <div className="sidebar">
          <AgentSelector
            selectedAgent={selectedAgent}
            onSelectAgent={setSelectedAgent}
          />
        </div>

        <div className="chat-container">
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
        </div>
      </main>
    </div>
  )
}

export default App

