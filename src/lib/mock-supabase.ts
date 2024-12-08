// src/lib/mock-supabase.ts
import { faker } from '@faker-js/faker'
import type { Booking, PriceHistory } from '@/lib/types'

// Helper to generate realistic car rental prices
const generatePrices = (basePrice: number) => {
  return {
    "Economy Car": basePrice * 0.8 + faker.number.float({ min: -20, max: 20 }),
    "Compact Car": basePrice * 0.9 + faker.number.float({ min: -20, max: 20 }),
    "Intermediate Car": basePrice * 0.95 + faker.number.float({ min: -20, max: 20 }),
    "Standard Car": basePrice + faker.number.float({ min: -20, max: 20 }),
    "Full-size Car": basePrice * 1.1 + faker.number.float({ min: -20, max: 20 }),
    "Premium Car": basePrice * 1.3 + faker.number.float({ min: -20, max: 20 }),
    "Compact SUV": basePrice * 1.4 + faker.number.float({ min: -20, max: 20 }),
    "Standard SUV": basePrice * 1.5 + faker.number.float({ min: -20, max: 20 }),
    "Full-size SUV": basePrice * 1.8 + faker.number.float({ min: -20, max: 20 }),
    "Premium SUV": basePrice * 2.2 + faker.number.float({ min: -20, max: 20 }),
    "Minivan": basePrice * 1.6 + faker.number.float({ min: -20, max: 20 })
  }
}

// Generate mock data
const generateMockBooking = (id: string): Booking => {
  const basePrice = faker.number.float({ min: 200, max: 600 })
  const location = faker.helpers.arrayElement(['KOA', 'HNL', 'OGG', 'LIH'])
  
  return {
    id,
    location,
    location_full_name: `${location} International Airport`,
    pickup_date: faker.date.future().toLocaleDateString(),
    dropoff_date: faker.date.future().toLocaleDateString(),
    pickup_time: "12:00 PM",
    dropoff_time: "12:00 PM",
    focus_category: faker.helpers.arrayElement([
      'Economy Car', 'Compact Car', 'Standard SUV', 'Full-size Car'
    ]),
    holding_price: basePrice,
    active: true,
    created_at: faker.date.past().toISOString()
  }
}

const generatePriceHistory = (bookingId: string, count = 10): PriceHistory[] => {
  const basePrice = faker.number.float({ min: 200, max: 600 })
  
  return Array.from({ length: count }, (_, i) => ({
    id: faker.string.uuid(),
    booking_id: bookingId,
    timestamp: faker.date.recent({ days: 30 - i }).toISOString(),
    prices: generatePrices(basePrice + (i * faker.number.float({ min: -20, max: 20 }))),
    created_at: faker.date.past().toISOString()
  }))
}

// Create mock store
export const mockStore = {
  bookings: Array.from({ length: 3 }, (_, i) => generateMockBooking(`booking_${i + 1}`)),
  priceHistories: [] as PriceHistory[]
}

// Initialize mock data
mockStore.bookings.forEach(booking => {
  mockStore.priceHistories.push(...generatePriceHistory(booking.id))
})

// Export mock client
export const mockSupabaseClient = {
  from: (table: string) => ({
    select: (columns: string = '*') => ({
      eq: (column: string, value: any) => ({
        order: (column: string, { ascending = true } = {}) => ({
          async then(resolve: Function) {
            await new Promise(r => setTimeout(r, 500))

            if (table === 'bookings') {
              const filteredBookings = mockStore.bookings.filter(b => b[column as keyof Booking] === value)
              resolve({
                data: filteredBookings,
                error: null
              })
            } else if (table === 'price_histories') {
              const filteredHistories = mockStore.priceHistories
                .filter(h => h[column as keyof PriceHistory] === value)
                .sort((a, b) => ascending ? 
                  new Date(a.created_at).getTime() - new Date(b.created_at).getTime() :
                  new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                )
              resolve({
                data: filteredHistories,
                error: null
              })
            }
          }
        })
      })
    })
  })
}

// Export test utilities
export const testUtils = {
  generateMockBooking,
  generatePriceHistory,
  mockStore,
  resetMockStore: () => {
    mockStore.bookings = Array.from({ length: 3 }, (_, i) => generateMockBooking(`booking_${i + 1}`))
    mockStore.priceHistories = []
    mockStore.bookings.forEach(booking => {
      mockStore.priceHistories.push(...generatePriceHistory(booking.id))
    })
  }
}