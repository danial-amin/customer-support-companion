import React from 'react'
import './Message.css'
import SQLResultsTable from './SQLResultsTable'

function Message({ message }) {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  if (message.type === 'error') {
    return (
      <div className="message error">
        <div className="message-content">
          <div className="message-header">
            <span className="message-type">⚠️ Erreur</span>
            <span className="message-time">{formatTimestamp(message.timestamp)}</span>
          </div>
          <div className="message-text">{message.content}</div>
        </div>
      </div>
    )
  }

  return (
    <div className={`message ${message.type}`}>
      <div className="message-content">
        <div className="message-header">
          <span className="message-type">
            {message.type === 'user' ? '👤 Vous' : `🤖 ${message.agent || 'IA'}`}
          </span>
          <span className="message-time">{formatTimestamp(message.timestamp)}</span>
        </div>
        <div className="message-text">{message.content}</div>
        {message.metadata && message.type === 'assistant' && (
          <div className="message-metadata">
            {message.metadata.sql_query && (
              <details className="metadata-detail">
                <summary>Requête SQL</summary>
                <pre>{message.metadata.sql_query}</pre>
              </details>
            )}
            {(message.metadata.result || message.metadata.sql_result) && (
              <div className="sql-results-section">
                <strong>Résultats de la requête:</strong>
                <SQLResultsTable 
                  result={message.metadata.sql_result || { result: message.metadata.result }} 
                />
              </div>
            )}
            {message.metadata.python_code && (
              <details className="metadata-detail">
                <summary>📝 Code Python exécuté</summary>
                <pre className="code-block">{message.metadata.python_code}</pre>
              </details>
            )}
            {(message.metadata.execution_result !== undefined && message.metadata.execution_result !== null) && (
              <details className="metadata-detail" open>
                <summary>📊 Sortie d'exécution</summary>
                <div className="execution-result-container">
                  <pre className="execution-result">
                    {message.metadata.execution_result || 'Code exécuté avec succès (aucune sortie générée)'}
                  </pre>
                </div>
              </details>
            )}
            {(message.metadata.visualization || message.metadata.plot_base64) && (
              <div className="visualization">
                <strong>📈 Visualisation:</strong>
                <div className="visualization-container">
                  <img 
                    src={`data:image/png;base64,${message.metadata.visualization || message.metadata.plot_base64}`} 
                    alt="Visualisation de l'analyse"
                    className="visualization-image"
                    onError={(e) => {
                      console.error("Failed to load visualization image", {
                        hasData: !!(message.metadata.visualization || message.metadata.plot_base64),
                        dataLength: (message.metadata.visualization || message.metadata.plot_base64 || '').length
                      });
                      e.target.style.display = 'none';
                      const errorDiv = e.target.nextElementSibling;
                      if (errorDiv) errorDiv.style.display = 'block';
                    }}
                    onLoad={() => {
                      console.log("Visualization image loaded successfully");
                    }}
                  />
                  <div className="visualization-error" style={{display: 'none'}}>
                    Échec du chargement de la visualisation. Les données d'image peuvent être corrompues.
                    {message.metadata.visualization && (
                      <div style={{fontSize: '0.8em', marginTop: '0.5rem'}}>
                        Data length: {(message.metadata.visualization || '').length} chars
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
            {message.metadata.insights && message.metadata.insights.length > 0 && (
              <div className="insights">
                <strong>Insights clés:</strong>
                <ul>
                  {message.metadata.insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
            {message.metadata.rag_sources && message.metadata.rag_sources.length > 0 && (
              <div className="rag-sources">
                <strong>📚 Sources:</strong>
                <ul className="sources-list">
                  {message.metadata.rag_sources.map((source, idx) => (
                    <li key={idx} className="source-item">
                      <div className="source-header">
                        {source.url ? (
                          <a 
                            href={source.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="source-link"
                          >
                            📄 {source.file_name || source.source}
                          </a>
                        ) : (
                          <span className="source-name">📄 {source.file_name || source.source}</span>
                        )}
                        {source.file_type && (
                          <span className="source-type">{source.file_type}</span>
                        )}
                      </div>
                      {source.text_preview && (
                        <div className="source-preview">
                          {source.text_preview}
                        </div>
                      )}
                      {source.score && (
                        <div className="source-score">
                          Pertinence: {(source.score * 100).toFixed(1)}%
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default Message

