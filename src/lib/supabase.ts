// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'
import { mockSupabaseClient, testUtils } from './mock-supabase'
export type { Booking, PriceHistory } from './types'

export const createSupabaseClient = (isTestEnvironment: boolean) => {
  return isTestEnvironment
    ? mockSupabaseClient
    : createClient(
        import.meta.env.VITE_SUPABASE_URL,
        import.meta.env.VITE_SUPABASE_ANON_KEY
      )
}

export { testUtils }