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
          message: 'Type de fichier non supporté. Veuillez télécharger des fichiers .txt, .pdf, .doc, .docx, .md ou .csv.'
        })
        setSelectedFile(null)
        return
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setUploadStatus({
          type: 'error',
          message: 'La taille du fichier dépasse la limite de 10MB.'
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
        message: 'Veuillez sélectionner un fichier à télécharger.'
      })
      return
    }

    setIsUploading(true)
    setUploadStatus(null)

    try {
      const result = await uploadDocument(selectedFile)
      setUploadStatus({
        type: 'success',
        message: `Téléchargement réussi! ${result.chunks_ingested} segments ingérés.`
      })
      setSelectedFile(null)
      // Reset file input
      const fileInput = document.getElementById('file-input')
      if (fileInput) fileInput.value = ''
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || error.message || 'Échec du téléchargement du document.'
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
        message: 'Veuillez remplir tous les champs requis pour la connexion SharePoint.'
      })
      return
    }

    setIsConnecting(true)
    setSharepointStatus(null)

    try {
      const result = await connectSharePoint(sharepointConfig)
      setSharepointStatus({
        type: 'success',
        message: `Connexion réussie! ${result.documents_retrieved} documents récupérés et ${result.chunks_ingested} segments ingérés au total.`
      })
      // Clear sensitive fields after successful connection
      setSharepointConfig(prev => ({
        ...prev,
        clientSecret: ''
      }))
    } catch (error) {
      setSharepointStatus({
        type: 'error',
        message: error.response?.data?.detail || error.message || 'Échec de la connexion à SharePoint.'
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
        <h2>📄 Gestion de documents</h2>
        <p>Téléchargez des documents ou connectez-vous à SharePoint pour les ajouter au système RAG</p>
      </div>

      <div className="upload-tabs">
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Télécharger un document
        </button>
        <button
          className={`tab-button ${activeTab === 'sharepoint' ? 'active' : ''}`}
          onClick={() => setActiveTab('sharepoint')}
        >
          🔗 Connecter SharePoint
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
                    <p>Cliquez pour sélectionner un fichier</p>
                    <p className="file-hint">
                      Formats supportés: .txt, .pdf, .doc, .docx, .md, .csv (max 10MB)
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
              {isUploading ? 'Téléchargement...' : 'Télécharger et ingérer'}
            </button>
          </div>
        )}

        {activeTab === 'sharepoint' && (
          <div className="sharepoint-section">
            <div className="form-group">
              <label htmlFor="site-url">
                URL du site SharePoint <span className="required">*</span>
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
                ID du locataire <span className="required">*</span>
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
                ID client (ID d'application) <span className="required">*</span>
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
                Secret client <span className="required">*</span>
              </label>
              <input
                type="password"
                id="client-secret"
                value={sharepointConfig.clientSecret}
                onChange={(e) => handleSharePointChange('clientSecret', e.target.value)}
                placeholder="Entrez votre secret client"
                required
              />
              <small className="form-hint">
                Ceci sera transmis de manière sécurisée et ne sera pas stocké dans le navigateur
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="library-name">
                Nom de la bibliothèque de documents
              </label>
              <input
                type="text"
                id="library-name"
                value={sharepointConfig.libraryName}
                onChange={(e) => handleSharePointChange('libraryName', e.target.value)}
                placeholder="Documents (par défaut si vide)"
              />
              <small className="form-hint">
                Laissez vide pour utiliser la bibliothèque "Documents" par défaut
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="folder-path">
                Chemin du dossier (optionnel)
              </label>
              <input
                type="text"
                id="folder-path"
                value={sharepointConfig.folderPath}
                onChange={(e) => handleSharePointChange('folderPath', e.target.value)}
                placeholder="Dossier1/Sous-dossier (laissez vide pour la racine)"
              />
              <small className="form-hint">
                Chemin de dossier spécifique dans la bibliothèque (par ex., "Support/FAQ")
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
              {isConnecting ? 'Connexion...' : 'Connecter et récupérer les documents'}
            </button>

            <div className="sharepoint-info">
              <h3>ℹ️ Instructions de configuration SharePoint</h3>
              <ol>
                <li>Enregistrez une application dans Azure AD (Inscriptions d'applications)</li>
                <li>Accordez les permissions API: <code>Sites.Read.All</code> ou <code>Sites.ReadWrite.All</code></li>
                <li>Créez un secret client et copiez les valeurs</li>
                <li>Assurez-vous que l'application a accès à votre site SharePoint</li>
              </ol>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload

