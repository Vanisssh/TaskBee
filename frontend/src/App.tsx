import './App.css'
import { useEffect, useState } from 'react'
import AuthPage from './components/AuthPage'
import Dashboard from './components/Dashboard'
import Header from './components/Header'
import LoadingSpinner from './components/LoadingSpinner'
import { me, logout } from './services/auth'
import { getAuthToken } from './services/api'
import type { User } from './types'

function App() {
  const [user, setUser] = useState<User | null>(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      if (!getAuthToken()) {
        setAuthLoading(false)
        return
      }
      try {
        const current = await me()
        setUser(current)
      } catch {
        logout()
        setUser(null)
      } finally {
        setAuthLoading(false)
      }
    }
    init()
  }, [])

  const handleLogout = () => {
    logout()
    setUser(null)
  }

  if (authLoading) {
    return (
      <div className="app">
        <main className="app-main">
          <LoadingSpinner message="Проверка авторизации..." />
        </main>
      </div>
    )
  }

  return (
    <div className="app">
      {user ? (
        <>
          <Header user={user} onLogout={handleLogout} />
          <main className="app-main">
            <Dashboard />
          </main>
        </>
      ) : (
        <main className="app-main">
          <AuthPage onSuccess={setUser} />
        </main>
      )}
    </div>
  )
}

export default App
