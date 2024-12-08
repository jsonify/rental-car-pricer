import { PriceTracker } from './components/PriceTracker'
import { AdminInterface } from './components/AdminInterface'
import { EnvironmentSwitcher } from './components/EnvironmentSwitcher'
import { EnvironmentProvider } from './contexts/EnvironmentContext'

function App() {
  return (
    <EnvironmentProvider>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <EnvironmentSwitcher />
          <AdminInterface />
        </div>
        
        <div className="container mx-auto px-4 pb-8">
          <PriceTracker />
        </div>
      </div>
    </EnvironmentProvider>
  )
}

export default App