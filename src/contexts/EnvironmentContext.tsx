// src/contexts/EnvironmentContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface EnvironmentContextType {
  isTestEnvironment: boolean
  setIsTestEnvironment: (value: boolean) => void
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined)

const STORAGE_KEY = 'use-test-environment'

export function EnvironmentProvider({ children }: { children: ReactNode }) {
  const [isTestEnvironment, setIsTestEnvironment] = useState(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : false
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

export function useEnvironment() {
  const context = useContext(EnvironmentContext)
  if (context === undefined) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider')
  }
  return context
}