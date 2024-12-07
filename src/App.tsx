// src/App.tsx
import { useState, useEffect } from 'react'
import { createClient } from '@supabase/supabase-js'
import { Chart } from './components/Chart'
import { DataGrid } from './components/DataGrid'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_KEY
)

export default function App() {
  const [priceData, setPriceData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPriceData()
    const subscription = supabase
      .channel('price_changes')
      .on('postgres_changes', { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'price_checks' 
      }, handleNewPrice)
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  async function fetchPriceData() {
    const { data, error } = await supabase
      .from('price_checks')
      .select('*')
      .order('checked_at', { ascending: false })
    
    if (data) setPriceData(data)
    setLoading(false)
  }

  function handleNewPrice(payload) {
    setPriceData(current => [payload.new, ...current])
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="min-h-screen bg-background">
      <div className="container py-10">
        <h1 className="text-4xl font-bold mb-8">Car Rental Price Monitor</h1>
        <div className="grid gap-8 md:grid-cols-2">
          <Chart data={priceData} />
          <DataGrid data={priceData} />
        </div>
      </div>
    </div>
  )
}
