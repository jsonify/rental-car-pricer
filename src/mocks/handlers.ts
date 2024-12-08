// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'
import { faker } from '@faker-js/faker'

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

// Generate mock booking data
const generateMockBooking = (id: string) => {
  const basePrice = faker.number.float({ min: 200, max: 600 })
  const location = faker.helpers.arrayElement(['KOA', 'HNL', 'OGG', 'LIH'])
  const focusCategory = faker.helpers.arrayElement([
    'Economy Car', 'Compact Car', 'Standard SUV', 'Full-size Car'
  ])
  
  const priceHistory = Array.from({ length: 10 }, (_, i) => ({
    timestamp: faker.date.recent({ days: 30 }).toISOString(),
    prices: generatePrices(basePrice + (i * faker.number.float({ min: -20, max: 20 }))),
    lowest_price: {
      category: focusCategory,
      price: basePrice
    }
  }))

  return {
    id,
    location,
    location_full_name: `${location} International Airport`,
    pickup_date: faker.date.future().toLocaleDateString(),
    dropoff_date: faker.date.future().toLocaleDateString(),
    pickup_time: "12:00 PM",
    dropoff_time: "12:00 PM",
    focus_category: focusCategory,
    holding_price: basePrice,
    price_history: priceHistory,
    created_at: faker.date.past().toISOString()
  }
}

// MSW handlers
export const handlers = [
  // Get all bookings
  http.get('/api/bookings', () => {
    const bookings = Array.from({ length: 3 }, (_, i) => 
      generateMockBooking(`booking_${i + 1}`)
    )
    
    return HttpResponse.json({
      data: bookings,
      count: bookings.length
    })
  }),

  // Get price histories
  http.get('/api/price-histories', () => {
    const basePrice = faker.number.float({ min: 200, max: 600 })
    const histories = Array.from({ length: 10 }, () => ({
      id: faker.string.uuid(),
      booking_id: faker.string.uuid(),
      timestamp: faker.date.recent().toISOString(),
      prices: generatePrices(basePrice),
      created_at: faker.date.past().toISOString()
    }))

    return HttpResponse.json({
      data: histories,
      count: histories.length
    })
  }),

  // Simulate price check
  http.post('/api/check-prices', async () => {
    // Simulate delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const basePrice = faker.number.float({ min: 200, max: 600 })
    return HttpResponse.json({
      success: true,
      prices: generatePrices(basePrice),
      timestamp: new Date().toISOString()
    })
  })
]

// src/mocks/browser.ts
import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

export const worker = setupWorker(...handlers)

// src/main.tsx
import { worker } from './mocks/browser'

if (process.env.NODE_ENV === 'development') {
  worker.start({
    onUnhandledRequest: 'bypass'
  })
}