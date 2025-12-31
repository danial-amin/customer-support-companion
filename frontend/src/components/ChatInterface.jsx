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

  const handleSuggestedQuestion = (question) => {
    if (!isLoading) {
      onSendMessage(question)
    }
  }

  // Suggested questions based on context
  const getSuggestedQuestions = () => {
    if (messages.length === 0) {
      // Initial suggested questions
      return [
        "What is your return policy?",
        "How many customers do we have?",
        "Show me sales trends",
        "What support tickets are open?"
      ]
    }
    
    // Get the last message to suggest follow-up questions
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.type === 'assistant') {
      const content = lastMessage.content.toLowerCase()
      
      // Context-aware suggestions based on the last response
      if (content.includes('return') || content.includes('policy')) {
        return [
          "What is the shipping policy?",
          "How do I process a return?",
          "What items can be returned?",
          "What is the refund process?"
        ]
      } else if (content.includes('customer') || content.includes('customers')) {
        return [
          "Show me customer details",
          "What are the top customers?",
          "How many new customers this month?",
          "Show customer statistics"
        ]
      } else if (content.includes('order') || content.includes('orders')) {
        return [
          "Show recent orders",
          "What is the average order value?",
          "Show order statistics",
          "What are the top products?"
        ]
      } else if (content.includes('ticket') || content.includes('support')) {
        return [
          "Show open tickets",
          "What are urgent tickets?",
          "Show ticket statistics",
          "How many tickets are resolved?"
        ]
      } else {
        // Generic follow-up questions
        return [
          "Tell me more",
          "Can you provide examples?",
          "What are the details?",
          "Show me related information"
        ]
      }
    }
    
    return []
  }

  const suggestedQuestions = getSuggestedQuestions()

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h3>Start a conversation</h3>
            <p>Ask a question and let the AI agents help you!</p>
            <div className="suggested-questions">
              <p>Suggested questions:</p>
              <div className="question-chips">
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    className="question-chip"
                    onClick={() => handleSuggestedQuestion(question)}
                    disabled={isLoading}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            <MessageList messages={messages} />
            {suggestedQuestions.length > 0 && !isLoading && (
              <div className="suggested-questions-inline">
                <p className="suggested-label">Suggested follow-ups:</p>
                <div className="question-chips">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      className="question-chip"
                      onClick={() => handleSuggestedQuestion(question)}
                      disabled={isLoading}
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  )
}

export default ChatInterface

