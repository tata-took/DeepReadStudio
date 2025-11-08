import React, { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'

export default function DocumentView({ user }) {
  const { id } = useParams()
  const [document, setDocument] = useState(null)
  const [summaries, setSummaries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedView, setSelectedView] = useState('overall') // 'overall' or 'chapters'

  useEffect(() => {
    fetchDocument()
  }, [id])

  const fetchDocument = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`/api/documents/${id}`)
      setDocument(response.data.document)
      setSummaries(response.data.summaries)
      setError('')
    } catch (err) {
      setError('Failed to load document')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const getOverallSummary = () => {
    return summaries.find(s => s.summary_type === 'overall')
  }

  const getChapterSummaries = () => {
    return summaries
      .filter(s => s.summary_type === 'chapter')
      .sort((a, b) => a.chapter_number - b.chapter_number)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="card">
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error || 'Document not found'}</p>
            <Link to="/" className="btn-primary inline-block">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const overallSummary = getOverallSummary()
  const chapterSummaries = getChapterSummaries()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          to="/"
          className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-4 inline-flex items-center"
        >
          <svg
            className="h-4 w-4 mr-1"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to Dashboard
        </Link>

        <h1 className="text-3xl font-bold text-gray-900 mb-2">{document.filename}</h1>

        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>{formatFileSize(document.file_size)}</span>
          {document.total_pages && <span>{document.total_pages} pages</span>}
          <span>Processed {formatDate(document.completed_at)}</span>
          {document.source_type === 'google_drive' && (
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-50 text-blue-700">
              Google Drive
            </span>
          )}
        </div>
      </div>

      {/* View Toggle */}
      <div className="mb-6">
        <div className="inline-flex rounded-lg border border-gray-200 p-1 bg-white">
          <button
            onClick={() => setSelectedView('overall')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === 'overall'
                ? 'bg-primary-600 text-white'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            Overall Summary
          </button>
          <button
            onClick={() => setSelectedView('chapters')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectedView === 'chapters'
                ? 'bg-primary-600 text-white'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            Chapter Summaries ({chapterSummaries.length})
          </button>
        </div>
      </div>

      {/* Overall Summary */}
      {selectedView === 'overall' && overallSummary && (
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Overall Summary</h2>

          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
              {overallSummary.content}
            </div>
          </div>

          {overallSummary.keywords && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Insights</h3>
              <div className="flex flex-wrap gap-2">
                {overallSummary.keywords.split(',').map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
                  >
                    {keyword.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chapter Summaries */}
      {selectedView === 'chapters' && (
        <div className="space-y-6">
          {chapterSummaries.length === 0 ? (
            <div className="card text-center py-8 text-gray-500">
              <p>No chapter summaries available</p>
            </div>
          ) : (
            chapterSummaries.map((summary) => (
              <div key={summary.id} className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">
                      Chapter {summary.chapter_number}
                      {summary.chapter_title && `: ${summary.chapter_title}`}
                    </h2>
                    {summary.start_page !== null && summary.end_page !== null && (
                      <p className="text-sm text-gray-500 mt-1">
                        Pages {summary.start_page + 1} - {summary.end_page + 1}
                      </p>
                    )}
                  </div>
                </div>

                <div className="prose max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                    {summary.content}
                  </div>
                </div>

                {summary.keywords && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-semibold text-gray-900 mb-2">Keywords</h4>
                    <div className="flex flex-wrap gap-2">
                      {summary.keywords.split(',').map((keyword, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                        >
                          {keyword.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
