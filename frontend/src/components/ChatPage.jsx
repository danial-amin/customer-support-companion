import React, { useState } from 'react'
import ChatInterface from './ChatInterface'
import AgentSelector from './AgentSelector'
import { queryAPI, checkHealth } from '../services/api'

function ChatPage() {
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
        content: error.message || 'Une erreur s\'est produite lors du traitement de votre demande',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-main">
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
    </div>
  )
}

export default ChatPage

