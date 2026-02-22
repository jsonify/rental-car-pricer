import { useState } from 'react'
import { Settings } from 'lucide-react'
import { PriceTracker } from './components/PriceTracker'
import { AdminInterface } from './components/AdminInterface'
import { EnvironmentSwitcher } from './components/EnvironmentSwitcher'
import { EnvironmentProvider } from './contexts/EnvironmentContext'

function App() {
  const [adminOpen, setAdminOpen] = useState(false)

  return (
    <EnvironmentProvider>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        {/* Fixed settings toggle button */}
        <button
          onClick={() => setAdminOpen(v => !v)}
          className={`fixed top-4 right-4 z-50 rounded-lg p-2 border transition-colors ${
            adminOpen
              ? 'bg-slate-700 border-slate-600 text-slate-200'
              : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
          }`}
          title={adminOpen ? 'Close admin' : 'Admin settings'}
        >
          <Settings size={16} />
        </button>

        {/* Environment switcher - top left area */}
        <div className="max-w-2xl mx-auto px-4 pt-4 pb-2">
          <EnvironmentSwitcher />
        </div>

        {/* Admin panel - appears below env switcher when open */}
        {adminOpen && (
          <div className="max-w-2xl mx-auto px-4 pb-4">
            <AdminInterface />
          </div>
        )}

        <PriceTracker />
      </div>
    </EnvironmentProvider>
  )
}

export default App
