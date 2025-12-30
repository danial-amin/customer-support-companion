import React from 'react'
import './SQLResultsTable.css'

function SQLResultsTable({ result }) {
  if (!result || !result.result) {
    return null
  }

  const { columns, rows, row_count } = result.result

  if (!columns || !rows || rows.length === 0) {
    return (
      <div className="sql-results-empty">
        <p>No rows found.</p>
      </div>
    )
  }

  // Format cell values
  const formatCell = (value) => {
    if (value === null || value === undefined) {
      return <span className="null-value">NULL</span>
    }
    if (typeof value === 'number') {
      // Format numbers with commas and handle decimals
      if (Number.isInteger(value)) {
        return value.toLocaleString()
      } else {
        return value.toLocaleString(undefined, { 
          minimumFractionDigits: 2, 
          maximumFractionDigits: 2 
        })
      }
    }
    if (typeof value === 'boolean') {
      return (
        <span className="boolean-value">
          {value ? '✓' : '✗'}
        </span>
      )
    }
    
    // Check if it's a date string
    const str = String(value)
    const dateMatch = str.match(/^\d{4}-\d{2}-\d{2}/)
    if (dateMatch) {
      try {
        const date = new Date(str)
        if (!isNaN(date.getTime())) {
          return (
            <span className="date-value" title={str}>
              {date.toLocaleDateString()} {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )
        }
      } catch (e) {
        // Not a valid date, continue
      }
    }
    
    // Truncate long strings
    if (str.length > 100) {
      return (
        <span className="truncated-value" title={str}>
          {str.substring(0, 100)}...
        </span>
      )
    }
    return str
  }

  // Detect column types for better alignment
  const getColumnType = (colName) => {
    if (rows.length === 0) return 'text'
    const firstValue = rows[0][colName]
    if (typeof firstValue === 'number') return 'number'
    if (typeof firstValue === 'boolean') return 'boolean'
    return 'text'
  }

  return (
    <div className="sql-results-container">
      <div className="sql-results-header">
        <span className="sql-results-count">
          {row_count} {row_count === 1 ? 'row' : 'rows'}
        </span>
        {row_count > 20 && (
          <span className="sql-results-note">
            (Showing first 20 rows)
          </span>
        )}
      </div>
      <div className="sql-results-table-wrapper">
        <table className="sql-results-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th 
                  key={idx}
                  className={`sql-column-header sql-column-${getColumnType(col)}`}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 20).map((row, rowIdx) => (
              <tr key={rowIdx} className={rowIdx % 2 === 0 ? 'even' : 'odd'}>
                {columns.map((col, colIdx) => (
                  <td 
                    key={colIdx}
                    className={`sql-cell sql-cell-${getColumnType(col)}`}
                  >
                    {formatCell(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {row_count > 20 && (
        <div className="sql-results-footer">
          <span className="sql-results-more">
            ... and {row_count - 20} more {row_count - 20 === 1 ? 'row' : 'rows'}
          </span>
        </div>
      )}
    </div>
  )
}

export default SQLResultsTable

