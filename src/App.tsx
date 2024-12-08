import { PriceTracker } from './components/PriceTracker'
import { AdminInterface } from './components/AdminInterface'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Admin Controls */}
      <div className="container mx-auto px-4 py-8">
        <AdminInterface />
      </div>
      
      {/* Price Tracker Dashboard */}
      <div className="container mx-auto px-4 pb-8">
        <PriceTracker />
      </div>
    </div>
  )
}

export default App