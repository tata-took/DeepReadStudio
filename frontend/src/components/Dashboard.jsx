import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'

import UploadForm from './UploadForm'
import GoogleDriveUpload from './GoogleDriveUpload'

export default function Dashboard({ user }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [uploadMode, setUploadMode] = useState('local') // 'local' or 'google-drive'

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/documents')
      setDocuments(response.data.documents)
      setError('')
    } catch (err) {
      setError('Failed to load documents')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = () => {
    fetchDocuments()
  }

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }

    try {
      await axios.delete(`/api/documents/${docId}`)
      fetchDocuments()
    } catch (err) {
      alert('Failed to delete document')
      console.error(err)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    }

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${badges[status] || badges.pending}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
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
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Upload and analyze your PDF documents</p>
      </div>

      {/* Upload Section */}
      <div className="mb-8">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Upload Document</h2>

            <div className="flex space-x-2">
              <button
                onClick={() => setUploadMode('local')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  uploadMode === 'local'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Local File
              </button>
              <button
                onClick={() => setUploadMode('google-drive')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  uploadMode === 'google-drive'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Google Drive
              </button>
            </div>
          </div>

          {uploadMode === 'local' ? (
            <UploadForm onSuccess={handleUploadSuccess} />
          ) : (
            <GoogleDriveUpload onSuccess={handleUploadSuccess} />
          )}
        </div>
      </div>

      {/* Documents List */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Your Documents</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No documents yet. Upload your first PDF to get started!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {doc.filename}
                      </h3>
                      {getStatusBadge(doc.status)}
                      {doc.source_type === 'google_drive' && (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-50 text-blue-700">
                          Google Drive
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{formatFileSize(doc.file_size)}</span>
                      {doc.total_pages && <span>{doc.total_pages} pages</span>}
                      <span>Uploaded {formatDate(doc.created_at)}</span>
                    </div>

                    {doc.status === 'processing' && (
                      <div className="mt-3">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${doc.progress}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{doc.progress}% complete</p>
                      </div>
                    )}

                    {doc.error_message && (
                      <p className="mt-2 text-sm text-red-600">{doc.error_message}</p>
                    )}
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    {doc.status === 'completed' && (
                      <Link
                        to={`/document/${doc.id}`}
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
                      >
                        View Summary
                      </Link>
                    )}

                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
