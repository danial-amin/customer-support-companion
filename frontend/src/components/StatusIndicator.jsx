import React from 'react'
import './StatusIndicator.css'

function StatusIndicator({ isHealthy }) {
  if (isHealthy === null) {
    return (
      <div className="status-indicator">
        <span className="status-dot checking"></span>
        <span>Vérification...</span>
      </div>
    )
  }

  return (
    <div className="status-indicator">
      <span className={`status-dot ${isHealthy ? 'healthy' : 'unhealthy'}`}></span>
      <span>{isHealthy ? 'Connecté' : 'Déconnecté'}</span>
    </div>
  )
}

export default StatusIndicator

