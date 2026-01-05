import React, { useState, useRef, useEffect } from 'react'
import './ChatInterface.css'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

function ChatInterface({ messages, onSendMessage, isLoading }) {
  const messagesEndRef = useRef(null)
  const [userLanguage, setUserLanguage] = useState('en')

  // Detect browser language
  useEffect(() => {
    const browserLang = navigator.language || navigator.userLanguage || 'en'
    const langCode = browserLang.split('-')[0].toLowerCase()
    setUserLanguage(langCode === 'fr' ? 'fr' : 'en')
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

  // Suggested questions based on context and language
  const getSuggestedQuestions = () => {
    const isFrench = userLanguage === 'fr'
    
    if (messages.length === 0) {
      // Initial suggested questions for fuel management
      if (isFrench) {
        return [
          "Combien de stations-service avons-nous?",
          "Quels types de carburant sont disponibles?",
          "Montrez-moi les transactions de carburant récentes",
          "Quel est l'inventaire de carburant actuel?"
        ]
      } else {
      return [
          "How many fuel stations do we have?",
          "What fuel types are available?",
          "Show me recent fuel transactions",
          "What is the current fuel inventory?"
      ]
      }
    }
    
    // Get the last message to suggest follow-up questions
    const lastMessage = messages[messages.length - 1]
    if (lastMessage && lastMessage.type === 'assistant') {
      const content = lastMessage.content.toLowerCase()
      
      // Context-aware suggestions based on the last response
      if (content.includes('station') || content.includes('station-service') || content.includes('station')) {
        if (isFrench) {
          return [
            "Montrez-moi les stations à Paris",
            "Quelle station a le plus de ventes?",
            "Quel est l'inventaire par station?",
            "Montrez les statistiques des stations"
          ]
        } else {
          return [
            "Show me stations in Paris",
            "Which station has the most sales?",
            "What is the inventory by station?",
            "Show station statistics"
          ]
        }
      } else if (content.includes('véhicule') || content.includes('vehicle') || content.includes('fleet')) {
        if (isFrench) {
          return [
            "Montrez-moi tous les véhicules",
            "Quel véhicule consomme le plus?",
            "Montrez l'efficacité énergétique",
            "Quels véhicules sont actifs?"
          ]
        } else {
          return [
            "Show me all vehicles",
            "Which vehicle consumes the most?",
            "Show fuel efficiency",
            "What vehicles are active?"
          ]
        }
      } else if (content.includes('transaction') || content.includes('transaction')) {
        if (isFrench) {
        return [
            "Montrez les transactions par mois",
            "Quel est le coût total des transactions?",
            "Analysez les tendances de consommation",
            "Montrez les transactions récentes"
        ]
        } else {
        return [
            "Show transactions by month",
            "What is the total transaction cost?",
            "Analyze consumption trends",
            "Show recent transactions"
        ]
        }
      } else if (content.includes('carte') || content.includes('card') || content.includes('fuel card')) {
        if (isFrench) {
        return [
            "Combien de cartes carburant sont actives?",
            "Montrez l'utilisation des cartes",
            "Quelle carte a le plus d'utilisation?",
            "Montrez les limites de crédit"
        ]
        } else {
        return [
            "How many fuel cards are active?",
            "Show card usage",
            "Which card has the most usage?",
            "Show credit limits"
        ]
        }
      } else {
        // Generic follow-up questions
        if (isFrench) {
          return [
            "Dites-moi en plus",
            "Pouvez-vous fournir des exemples?",
            "Quels sont les détails?",
            "Montrez-moi des informations connexes"
          ]
        } else {
        return [
          "Tell me more",
          "Can you provide examples?",
          "What are the details?",
          "Show me related information"
        ]
        }
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
            <h3>{userLanguage === 'fr' ? 'Démarrer une conversation' : 'Start a conversation'}</h3>
            <p>{userLanguage === 'fr' ? 'Posez une question et laissez les agents IA vous aider avec la gestion de carburant!' : 'Ask a question and let the AI agents help you with fuel management!'}</p>
            <div className="suggested-questions">
              <p>{userLanguage === 'fr' ? 'Questions suggérées:' : 'Suggested questions:'}</p>
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
                <p className="suggested-label">{userLanguage === 'fr' ? 'Questions de suivi suggérées:' : 'Suggested follow-ups:'}</p>
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

