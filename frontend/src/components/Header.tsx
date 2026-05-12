import './Header.css'
import type { User } from '../types'

interface HeaderProps {
  user: User
  onLogout: () => void
}

function Header({ user, onLogout }: HeaderProps) {
  const roleLabel = user.role === 'executor' ? 'Исполнитель' : 'Заказчик'

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-logo">
          <h1>🐝 TaskBee</h1>
        </div>
        <div className="header-nav">
          <a href="https://github.com" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          <a href="/api/docs/" target="_blank" rel="noopener noreferrer">
            API Docs (Swagger)
          </a>
          <div className="profile-menu">
            <div className="profile-name">{user.name}</div>
            <div className="profile-meta">
              <span>{roleLabel}</span>
              <span>{user.email}</span>
            </div>
            <button type="button" className="logout-btn" onClick={onLogout}>
              Выход
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
