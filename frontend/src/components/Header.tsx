import './Header.css'

function Header() {
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
        </div>
      </div>
    </header>
  )
}

export default Header
