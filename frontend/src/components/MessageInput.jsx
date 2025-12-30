import React, { useState } from 'react'
import './MessageInput.css'

function MessageInput({ onSendMessage, isLoading }) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (message.trim() && !isLoading) {
      onSendMessage(message)
      setMessage('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="message-input-container">
      <form onSubmit={handleSubmit} className="message-input-form">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
          disabled={isLoading}
          rows={1}
          className="message-input"
        />
        <button
          type="submit"
          disabled={!message.trim() || isLoading}
          className="send-button"
        >
          {isLoading ? '⏳' : '➤'}
        </button>
      </form>
    </div>
  )
}

export default MessageInput

