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
        <div className="max-w-2xl mx-auto px-4 pt-4 pb-2 space-y-2">
          <EnvironmentSwitcher />

          <button
            onClick={() => setAdminOpen(v => !v)}
            className="flex items-center gap-1.5 text-xs text-gray-600 hover:text-gray-400 transition-colors py-1"
          >
            <Settings size={12} />
            {adminOpen ? 'Hide admin' : 'Admin'}
          </button>

          {adminOpen && <AdminInterface />}
        </div>

        <PriceTracker />
      </div>
    </EnvironmentProvider>
  )
}

export default App
