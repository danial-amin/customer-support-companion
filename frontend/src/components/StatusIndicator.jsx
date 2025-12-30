import React from 'react'
import './StatusIndicator.css'

function StatusIndicator({ isHealthy }) {
  if (isHealthy === null) {
    return (
      <div className="status-indicator">
        <span className="status-dot checking"></span>
        <span>Checking...</span>
      </div>
    )
  }

  return (
    <div className="status-indicator">
      <span className={`status-dot ${isHealthy ? 'healthy' : 'unhealthy'}`}></span>
      <span>{isHealthy ? 'Connected' : 'Disconnected'}</span>
    </div>
  )
}

export default StatusIndicator

