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
            <span className="message-type">⚠️ Error</span>
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
            {message.type === 'user' ? '👤 You' : `🤖 ${message.agent || 'AI'}`}
          </span>
          <span className="message-time">{formatTimestamp(message.timestamp)}</span>
        </div>
        <div className="message-text">{message.content}</div>
        {message.metadata && message.type === 'assistant' && (
          <div className="message-metadata">
            {message.metadata.sql_query && (
              <details className="metadata-detail">
                <summary>SQL Query</summary>
                <pre>{message.metadata.sql_query}</pre>
              </details>
            )}
            {(message.metadata.result || message.metadata.sql_result) && (
              <div className="sql-results-section">
                <strong>Query Results:</strong>
                <SQLResultsTable 
                  result={message.metadata.sql_result || { result: message.metadata.result }} 
                />
              </div>
            )}
            {message.metadata.python_code && (
              <details className="metadata-detail">
                <summary>📝 Python Code Executed</summary>
                <pre className="code-block">{message.metadata.python_code}</pre>
              </details>
            )}
            {(message.metadata.execution_result !== undefined && message.metadata.execution_result !== null) && (
              <details className="metadata-detail" open>
                <summary>📊 Execution Output</summary>
                <div className="execution-result-container">
                  <pre className="execution-result">
                    {message.metadata.execution_result || 'Code executed successfully (no output generated)'}
                  </pre>
                </div>
              </details>
            )}
            {(message.metadata.visualization || message.metadata.plot_base64) && (
              <div className="visualization">
                <strong>📈 Visualization:</strong>
                <div className="visualization-container">
                  <img 
                    src={`data:image/png;base64,${message.metadata.visualization || message.metadata.plot_base64}`} 
                    alt="Analysis visualization"
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
                    Failed to load visualization. The image data may be corrupted.
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
                <strong>Key Insights:</strong>
                <ul>
                  {message.metadata.insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
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

