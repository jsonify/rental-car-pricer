import { PriceTracker } from './components/PriceTracker'
import { AdminInterface } from './components/AdminInterface'
import { EnvironmentSwitcher } from './components/EnvironmentSwitcher'
import { EnvironmentProvider } from './contexts/EnvironmentContext'

function App() {
  return (
    <EnvironmentProvider>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <div className="max-w-2xl mx-auto px-4 pt-6 pb-2 space-y-4">
          <EnvironmentSwitcher />
          <AdminInterface />
        </div>
        <PriceTracker />
      </div>
    </EnvironmentProvider>
  )
}

export default App
