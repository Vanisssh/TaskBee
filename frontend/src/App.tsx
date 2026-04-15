import './App.css'
import Dashboard from './components/Dashboard'
import Header from './components/Header'

function App() {
  return (
    <div className="app">
      <Header />
      <main className="app-main">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
