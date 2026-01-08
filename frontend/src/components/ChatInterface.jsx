import React, { useState, useRef, useEffect } from 'react'
import './ChatInterface.css'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

function ChatInterface({ messages, onSendMessage, isLoading }) {
  const messagesEndRef = useRef(null)
  const [userLanguage, setUserLanguage] = useState('fr')

  // Set language to French by default
  useEffect(() => {
    setUserLanguage('fr')
  }, [])

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
      // Initial suggested questions for fuel management
      return [
        "Combien de stations-service avons-nous?",
        "Quels types de carburant sont disponibles?",
        "Montrez-moi les transactions de carburant récentes",
        "Quel est l'inventaire de carburant actuel?"
      ]
    }
    
    // Get the last message to suggest follow-up questions
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.type === 'assistant') {
      const content = lastMessage.content.toLowerCase()
      
      // Context-aware suggestions based on the last response
      if (content.includes('station') || content.includes('station-service') || content.includes('station')) {
        return [
          "Montrez-moi les stations à Paris",
          "Quelle station a le plus de ventes?",
          "Quel est l'inventaire par station?",
          "Montrez les statistiques des stations"
        ]
      } else if (content.includes('véhicule') || content.includes('vehicle') || content.includes('fleet')) {
        return [
          "Montrez-moi tous les véhicules",
          "Quel véhicule consomme le plus?",
          "Montrez l'efficacité énergétique",
          "Quels véhicules sont actifs?"
        ]
      } else if (content.includes('transaction') || content.includes('transaction')) {
        return [
          "Montrez les transactions par mois",
          "Quel est le coût total des transactions?",
          "Analysez les tendances de consommation",
          "Montrez les transactions récentes"
        ]
      } else if (content.includes('carte') || content.includes('card') || content.includes('fuel card')) {
        return [
          "Combien de cartes carburant sont actives?",
          "Montrez l'utilisation des cartes",
          "Quelle carte a le plus d'utilisation?",
          "Montrez les limites de crédit"
        ]
      } else {
        // Generic follow-up questions
        return [
          "Dites-moi en plus",
          "Pouvez-vous fournir des exemples?",
          "Quels sont les détails?",
          "Montrez-moi des informations connexes"
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
            <div className="empty-icon">⛽</div>
            <h3>Démarrer une conversation</h3>
            <p>Posez une question et laissez les agents IA vous aider avec la gestion de carburant!</p>
            <div className="suggested-questions">
              <p>Questions suggérées:</p>
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
                <p className="suggested-label">Questions de suivi suggérées:</p>
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

