// src/contexts/EnvironmentContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface EnvironmentContextType {
  isTestEnvironment: boolean
  setIsTestEnvironment: (value: boolean) => void
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined)

const STORAGE_KEY = 'use-test-environment'

const hasSupabaseConfig = !!(import.meta.env.VITE_SUPABASE_URL && import.meta.env.VITE_SUPABASE_ANON_KEY)

export function EnvironmentProvider({ children }: { children: ReactNode }) {
  const [isTestEnvironment, setIsTestEnvironment] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored !== null) return JSON.parse(stored)
    return !hasSupabaseConfig
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(isTestEnvironment))
  }, [isTestEnvironment])

  return (
    <EnvironmentContext.Provider value={{ isTestEnvironment, setIsTestEnvironment }}>
      {children}
    </EnvironmentContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useEnvironment() {
  const context = useContext(EnvironmentContext)
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider')
  }
  return context
}