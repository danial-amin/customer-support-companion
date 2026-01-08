import React from 'react'
import './AgentSelector.css'

const agents = [
  { value: 'auto', label: '🔄 Auto', description: 'Routage automatique vers le meilleur agent' },
  { value: 'rag', label: '📚 RAG', description: 'Génération augmentée par récupération' },
  { value: 'sql', label: '🗄️ SQL', description: 'Langage naturel vers SQL' },
  { value: 'analyzer', label: '📊 Analyseur', description: 'Analyse de données et insights' }
]

function AgentSelector({ selectedAgent, onSelectAgent }) {
  return (
    <div className="agent-selector">
      <h3>Sélectionner un agent</h3>
      <div className="agent-list">
        {agents.map(agent => (
          <button
            key={agent.value}
            className={`agent-option ${selectedAgent === agent.value ? 'active' : ''}`}
            onClick={() => onSelectAgent(agent.value)}
          >
            <div className="agent-label">{agent.label}</div>
            <div className="agent-description">{agent.description}</div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default AgentSelector

