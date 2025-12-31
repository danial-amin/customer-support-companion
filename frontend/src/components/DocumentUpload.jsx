import React, { useState } from 'react'
import './DocumentUpload.css'
import { uploadDocument, connectSharePoint } from '../services/api'

function DocumentUpload() {
  const [activeTab, setActiveTab] = useState('upload') // 'upload' or 'sharepoint'
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)
  const [isUploading, setIsUploading] = useState(false)
  
  // SharePoint form state
  const [sharepointConfig, setSharepointConfig] = useState({
    siteUrl: '',
    tenantId: '',
    clientId: '',
    clientSecret: '',
    libraryName: '',
    folderPath: ''
  })
  const [sharepointStatus, setSharepointStatus] = useState(null)
  const [isConnecting, setIsConnecting] = useState(false)

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Validate file type
      const allowedTypes = [
        'text/plain',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/markdown',
        'text/csv'
      ]
      
      if (!allowedTypes.includes(file.type) && !file.name.match(/\.(txt|pdf|doc|docx|md|csv)$/i)) {
        setUploadStatus({
          type: 'error',
          message: 'Unsupported file type. Please upload .txt, .pdf, .doc, .docx, .md, or .csv files.'
        })
        setSelectedFile(null)
        return
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setUploadStatus({
          type: 'error',
          message: 'File size exceeds 10MB limit.'
        })
        setSelectedFile(null)
        return
      }
      
      setSelectedFile(file)
      setUploadStatus(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus({
        type: 'error',
        message: 'Please select a file to upload.'
      })
      return
    }

    setIsUploading(true)
    setUploadStatus(null)

    try {
      const result = await uploadDocument(selectedFile)
      setUploadStatus({
        type: 'success',
        message: `Successfully uploaded! Ingested ${result.chunks_ingested} chunks.`
      })
      setSelectedFile(null)
      // Reset file input
      const fileInput = document.getElementById('file-input')
      if (fileInput) fileInput.value = ''
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || error.message || 'Failed to upload document.'
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleSharePointConnect = async () => {
    // Validate required fields
    if (!sharepointConfig.siteUrl || !sharepointConfig.tenantId || 
        !sharepointConfig.clientId || !sharepointConfig.clientSecret) {
      setSharepointStatus({
        type: 'error',
        message: 'Please fill in all required SharePoint connection fields.'
      })
      return
    }

    setIsConnecting(true)
    setSharepointStatus(null)

    try {
      const result = await connectSharePoint(sharepointConfig)
      setSharepointStatus({
        type: 'success',
        message: `Successfully connected! Retrieved and ingested ${result.documents_retrieved} documents (${result.chunks_ingested} total chunks).`
      })
      // Clear sensitive fields after successful connection
      setSharepointConfig(prev => ({
        ...prev,
        clientSecret: ''
      }))
    } catch (error) {
      setSharepointStatus({
        type: 'error',
        message: error.response?.data?.detail || error.message || 'Failed to connect to SharePoint.'
      })
    } finally {
      setIsConnecting(false)
    }
  }

  const handleSharePointChange = (field, value) => {
    setSharepointConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="document-upload">
      <div className="upload-header">
        <h2>📄 Document Management</h2>
        <p>Upload documents or connect to SharePoint to add them to the RAG system</p>
      </div>

      <div className="upload-tabs">
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload Document
        </button>
        <button
          className={`tab-button ${activeTab === 'sharepoint' ? 'active' : ''}`}
          onClick={() => setActiveTab('sharepoint')}
        >
          🔗 Connect SharePoint
        </button>
      </div>

      <div className="upload-content">
        {activeTab === 'upload' && (
          <div className="upload-section">
            <div className="file-upload-area">
              <input
                type="file"
                id="file-input"
                onChange={handleFileSelect}
                accept=".txt,.pdf,.doc,.docx,.md,.csv"
                style={{ display: 'none' }}
              />
              <label htmlFor="file-input" className="file-input-label">
                {selectedFile ? (
                  <div className="file-selected">
                    <span className="file-icon">📄</span>
                    <div className="file-info">
                      <div className="file-name">{selectedFile.name}</div>
                      <div className="file-size">
                        {(selectedFile.size / 1024).toFixed(2)} KB
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="file-placeholder">
                    <span className="upload-icon">📤</span>
                    <p>Click to select a file</p>
                    <p className="file-hint">
                      Supported: .txt, .pdf, .doc, .docx, .md, .csv (max 10MB)
                    </p>
                  </div>
                )}
              </label>
            </div>

            {uploadStatus && (
              <div className={`status-message ${uploadStatus.type}`}>
                {uploadStatus.type === 'success' ? '✅' : '❌'} {uploadStatus.message}
              </div>
            )}

            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? 'Uploading...' : 'Upload & Ingest'}
            </button>
          </div>
        )}

        {activeTab === 'sharepoint' && (
          <div className="sharepoint-section">
            <div className="form-group">
              <label htmlFor="site-url">
                SharePoint Site URL <span className="required">*</span>
              </label>
              <input
                type="url"
                id="site-url"
                value={sharepointConfig.siteUrl}
                onChange={(e) => handleSharePointChange('siteUrl', e.target.value)}
                placeholder="https://yourtenant.sharepoint.com/sites/yoursite"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="tenant-id">
                Tenant ID <span className="required">*</span>
              </label>
              <input
                type="text"
                id="tenant-id"
                value={sharepointConfig.tenantId}
                onChange={(e) => handleSharePointChange('tenantId', e.target.value)}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="client-id">
                Client ID (Application ID) <span className="required">*</span>
              </label>
              <input
                type="text"
                id="client-id"
                value={sharepointConfig.clientId}
                onChange={(e) => handleSharePointChange('clientId', e.target.value)}
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="client-secret">
                Client Secret <span className="required">*</span>
              </label>
              <input
                type="password"
                id="client-secret"
                value={sharepointConfig.clientSecret}
                onChange={(e) => handleSharePointChange('clientSecret', e.target.value)}
                placeholder="Enter your client secret"
                required
              />
              <small className="form-hint">
                This will be securely transmitted and not stored in the browser
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="library-name">
                Document Library Name
              </label>
              <input
                type="text"
                id="library-name"
                value={sharepointConfig.libraryName}
                onChange={(e) => handleSharePointChange('libraryName', e.target.value)}
                placeholder="Documents (default if empty)"
              />
              <small className="form-hint">
                Leave empty to use default "Documents" library
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="folder-path">
                Folder Path (optional)
              </label>
              <input
                type="text"
                id="folder-path"
                value={sharepointConfig.folderPath}
                onChange={(e) => handleSharePointChange('folderPath', e.target.value)}
                placeholder="Folder1/Subfolder (leave empty for root)"
              />
              <small className="form-hint">
                Specific folder path within the library (e.g., "Support/FAQ")
              </small>
            </div>

            {sharepointStatus && (
              <div className={`status-message ${sharepointStatus.type}`}>
                {sharepointStatus.type === 'success' ? '✅' : '❌'} {sharepointStatus.message}
              </div>
            )}

            <button
              className="upload-button"
              onClick={handleSharePointConnect}
              disabled={isConnecting}
            >
              {isConnecting ? 'Connecting...' : 'Connect & Retrieve Documents'}
            </button>

            <div className="sharepoint-info">
              <h3>ℹ️ SharePoint Setup Instructions</h3>
              <ol>
                <li>Register an app in Azure AD (App Registrations)</li>
                <li>Grant API permissions: <code>Sites.Read.All</code> or <code>Sites.ReadWrite.All</code></li>
                <li>Create a client secret and copy the values</li>
                <li>Ensure the app has access to your SharePoint site</li>
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload

