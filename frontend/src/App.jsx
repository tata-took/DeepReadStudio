import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'

import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import DocumentView from './components/DocumentView'
import Navigation from './components/Navigation'

// Configure axios defaults
axios.defaults.withCredentials = true
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/auth/status')
      if (response.data.authenticated) {
        setUser(response.data.user)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout')
      setUser(null)
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {user && <Navigation user={user} onLogout={handleLogout} />}

        <Routes>
          <Route
            path="/login"
            element={
              user ? <Navigate to="/" /> : <LoginPage onLogin={handleLogin} />
            }
          />

          <Route
            path="/"
            element={
              user ? <Dashboard user={user} /> : <Navigate to="/login" />
            }
          />

          <Route
            path="/document/:id"
            element={
              user ? <DocumentView user={user} /> : <Navigate to="/login" />
            }
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
