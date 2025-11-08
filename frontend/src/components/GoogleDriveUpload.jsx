import React, { useState, useEffect } from 'react'
import axios from 'axios'

export default function GoogleDriveUpload({ onSuccess }) {
  const [authorized, setAuthorized] = useState(false)
  const [files, setFiles] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    checkFiles()
  }, [])

  const checkFiles = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/google-drive/files')
      setFiles(response.data.files)
      setAuthorized(true)
      setError('')
    } catch (err) {
      if (err.response?.status === 401) {
        setAuthorized(false)
      } else {
        setError('Failed to load Google Drive files')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleAuthorize = async () => {
    try {
      const response = await axios.get('/api/google-drive/auth-url')
      const authUrl = response.data.auth_url

      // Open popup window
      const width = 600
      const height = 700
      const left = window.screen.width / 2 - width / 2
      const top = window.screen.height / 2 - height / 2

      const popup = window.open(
        authUrl,
        'Google Drive Authorization',
        `width=${width},height=${height},left=${left},top=${top}`
      )

      // Listen for callback
      window.addEventListener('message', async (event) => {
        if (event.data.type === 'google-drive-callback') {
          const code = event.data.code

          try {
            await axios.post('/api/google-drive/callback', { code })
            setAuthorized(true)
            checkFiles()
          } catch (err) {
            setError('Authorization failed')
          }

          if (popup) {
            popup.close()
          }
        }
      })

    } catch (err) {
      setError('Failed to get authorization URL')
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError('')

    try {
      const response = await axios.post('/api/upload/google-drive', {
        file_id: selectedFile.id
      })

      // Reset selection
      setSelectedFile(null)

      // Notify parent
      if (onSuccess) {
        onSuccess(response.data)
      }

      alert('File downloaded from Google Drive successfully! Processing has started.')

    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString()
  }

  if (!authorized) {
    return (
      <div className="text-center py-8">
        <div className="mb-4">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Connect Google Drive</h3>
        <p className="text-gray-600 mb-6">
          Authorize DeepRead Studio to access your Google Drive files
        </p>
        <button
          onClick={handleAuthorize}
          className="btn-primary"
        >
          Authorize Google Drive
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-900">Your PDF Files</h3>
        <button
          onClick={checkFiles}
          disabled={loading}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No PDF files found in your Google Drive</p>
        </div>
      ) : (
        <div className="border border-gray-200 rounded-lg max-h-96 overflow-y-auto">
          {files.map((file) => (
            <div
              key={file.id}
              onClick={() => setSelectedFile(file)}
              className={`p-4 border-b border-gray-200 last:border-b-0 cursor-pointer transition-colors ${
                selectedFile?.id === file.id
                  ? 'bg-primary-50 border-l-4 border-l-primary-600'
                  : 'hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {file.name}
                  </h4>
                  <div className="flex items-center space-x-3 mt-1 text-xs text-gray-500">
                    <span>{formatFileSize(file.size)}</span>
                    <span>Modified {formatDate(file.modified_time)}</span>
                  </div>
                </div>
                {selectedFile?.id === file.id && (
                  <svg
                    className="h-5 w-5 text-primary-600 flex-shrink-0 ml-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!selectedFile || uploading}
        className="w-full btn-primary"
      >
        {uploading ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            Uploading...
          </span>
        ) : (
          'Upload Selected File'
        )}
      </button>
    </div>
  )
}
