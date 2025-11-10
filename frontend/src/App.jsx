import React, { useState } from 'react'
import axios from 'axios'

axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0]

    setError('')
    setResult(null)

    if (!selectedFile) {
      setFile(null)
      return
    }

    if (selectedFile.type !== 'application/pdf') {
      setError('PDFファイルのみアップロードできます')
      setFile(null)
      return
    }

    setFile(selectedFile)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!file) {
      setError('送信するPDFファイルを選択してください')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      setIsLoading(true)
      setError('')

      const response = await axios.post('/api/mvp/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setResult(response.data)
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.message ||
        '要約リクエストの送信に失敗しました'
      setError(message)
      setResult(null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-3xl mx-auto px-4 py-10">
          <h1 className="text-3xl font-bold text-gray-900">DeepRead Studio</h1>
          <p className="mt-2 text-gray-600">
            PDFファイルをアップロードしてAI要約を取得しましょう。
            サーバーのURLは環境変数「VITE_API_URL」で変更できます。
          </p>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-10 space-y-8">
        <section className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">PDFを送信</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="pdf-upload" className="block text-sm font-medium text-gray-700 mb-2">
                PDFファイルを選択
              </label>
              <input
                id="pdf-upload"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="input-field"
                disabled={isLoading}
              />
              <p className="mt-2 text-xs text-gray-500">最大100MBまでのPDFに対応しています。</p>
            </div>

            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <button
              type="submit"
              className="btn-primary w-full sm:w-auto"
              disabled={!file || isLoading}
            >
              {isLoading ? '要約を生成中…' : '要約を取得'}
            </button>
          </form>
        </section>

        {isLoading && (
          <section className="card">
            <div className="flex items-center space-x-3 text-gray-600">
              <svg
                className="animate-spin h-5 w-5 text-primary-600"
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
              <span>サーバーでPDFを処理しています…</span>
            </div>
          </section>
        )}

        {result && (
          <section className="card space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">要約結果</h2>
                <p className="text-sm text-gray-500">{result.title}</p>
              </div>
              {typeof result.pages === 'number' && (
                <span className="inline-flex items-center px-3 py-1 rounded-full bg-primary-50 text-primary-700 text-sm font-medium">
                  {result.pages} ページ
                </span>
              )}
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">全体要約</h3>
              <p className="text-gray-700 whitespace-pre-line">
                {result.summary || '要約は生成されませんでした。'}
              </p>
            </div>

            {Array.isArray(result.sections) && result.sections.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">セクション要約</h3>
                {result.sections.map((section, index) => (
                  <div key={`${section.heading || 'section'}-${index}`} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="text-base font-semibold text-primary-700">
                      {section.heading || `セクション${index + 1}`}
                    </h4>
                    <p className="mt-2 text-gray-700 whitespace-pre-line">
                      {section.summary || 'このセクションの要約はありません。'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  )
}

export default App
