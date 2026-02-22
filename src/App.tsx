import { Routes, Route } from 'react-router-dom'
import { PriceTracker } from './components/PriceTracker'
import { AdminInterface } from './components/AdminInterface'
import { EnvironmentSwitcher } from './components/EnvironmentSwitcher'
import { EnvironmentProvider } from './contexts/EnvironmentContext'
import { BookingDetail } from './pages/BookingDetail'

function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-5xl mx-auto px-4 pt-4 pb-2">
        <EnvironmentSwitcher />
      </div>

      <div className="max-w-5xl mx-auto px-4 pb-8 flex gap-8 items-start">
        {/* Main content: booking cards */}
        <div className="flex-1 min-w-0">
          <PriceTracker />
        </div>

        {/* Right sidebar: admin controls, always visible */}
        <div className="w-72 flex-shrink-0 sticky top-4 pt-8">
          <AdminInterface />
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <EnvironmentProvider>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/booking/:id" element={<BookingDetail />} />
      </Routes>
    </EnvironmentProvider>
  )
}

export default App
