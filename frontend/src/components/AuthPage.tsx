import { FormEvent, useMemo, useState } from 'react'
import './AuthPage.css'
import type { User } from '../types'
import { login, register } from '../services/auth'

type Mode = 'login' | 'register'
type Role = 'customer' | 'executor'

interface AuthPageProps {
  onSuccess: (user: User) => void
}

function AuthPage({ onSuccess }: AuthPageProps) {
  const [mode, setMode] = useState<Mode>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<Role>('customer')
  const [isSubmitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const title = useMemo(() => (mode === 'login' ? 'Вход в TaskBee' : 'Регистрация в TaskBee'), [mode])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      if (mode === 'login') {
        const result = await login({ email, password })
        onSuccess(result.user)
      } else {
        const result = await register({ name, email, password, role })
        onSuccess(result.user)
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Ошибка авторизации'
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>{title}</h1>
        <p className="auth-subtitle">По почте и паролю, с выбором роли пользователя</p>

        <div className="auth-tabs">
          <button type="button" className={mode === 'login' ? 'tab active' : 'tab'} onClick={() => setMode('login')}>
            Вход
          </button>
          <button
            type="button"
            className={mode === 'register' ? 'tab active' : 'tab'}
            onClick={() => setMode('register')}
          >
            Регистрация
          </button>
        </div>

        <form className="auth-form" onSubmit={submit}>
          {mode === 'register' && (
            <>
              <label>
                Имя
                <input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Иван Иванов" />
              </label>

              <label>
                Роль
                <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
                  <option value="customer">Заказчик</option>
                  <option value="executor">Исполнитель</option>
                </select>
              </label>
            </>
          )}

          <label>
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="user@mail.com" />
          </label>

          <label>
            Пароль
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={6}
              required
              placeholder="Минимум 6 символов"
            />
          </label>

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Подождите...' : mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default AuthPage
