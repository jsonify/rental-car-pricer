// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
import { createMockSupabaseClient, testUtils } from './mock-supabase'
export type { Booking, PriceHistory, HoldingPriceHistory } from './types'

export const createSupabaseClient = (isTestEnvironment: boolean) => {
  if (isTestEnvironment) {
    return createMockSupabaseClient() as any
  }

  return createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY
  )
}

export { testUtils }
