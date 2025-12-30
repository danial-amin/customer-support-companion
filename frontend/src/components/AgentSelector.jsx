import React from 'react'
import './AgentSelector.css'

const agents = [
  { value: 'auto', label: '🔄 Auto', description: 'Automatically route to best agent' },
  { value: 'rag', label: '📚 RAG', description: 'Retrieval Augmented Generation' },
  { value: 'sql', label: '🗄️ SQL', description: 'Natural Language to SQL' },
  { value: 'analyzer', label: '📊 Analyzer', description: 'Data Analysis & Insights' }
]

function AgentSelector({ selectedAgent, onSelectAgent }) {
  return (
    <div className="agent-selector">
      <h3>Select Agent</h3>
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

