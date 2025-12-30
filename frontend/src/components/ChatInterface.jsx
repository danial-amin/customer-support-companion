import React, { useState, useRef, useEffect } from 'react'
import './ChatInterface.css'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

function ChatInterface({ messages, onSendMessage, isLoading }) {
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h3>Start a conversation</h3>
            <p>Ask a question and let the AI agents help you!</p>
            <div className="example-queries">
              <p>Try asking:</p>
              <ul>
                <li>"What is our return policy?"</li>
                <li>"How many customers signed up this month?"</li>
                <li>"Analyze our sales trends"</li>
              </ul>
            </div>
          </div>
        ) : (
          <MessageList messages={messages} />
        )}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  )
}

export default ChatInterface

