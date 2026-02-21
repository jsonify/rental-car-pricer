// src/lib/mock-supabase.ts
import { faker } from '@faker-js/faker'
import type { Booking, PriceHistory, HoldingPriceHistory } from '@/lib/types'

const STORAGE_KEY = 'mockSupabaseStore'

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
const generateMockBooking = (id: string, index: number): Booking => {
  const locations = [
    { code: 'KOA', name: 'Kailua-Kona International Airport' },
    { code: 'HNL', name: 'Daniel K. Inouye International Airport' },
    { code: 'OGG', name: 'Kahului Airport' },
    { code: 'LIH', name: 'Lihue Airport' }
  ]
  const location = locations[index % locations.length]
  const basePrice = faker.number.float({ min: 200, max: 600 })

  return {
    id,
    location: location.code,
    location_full_name: location.name,
    pickup_date: '04/01/2025',
    dropoff_date: '04/08/2025',
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

const generatePriceHistory = (bookingId: string, count = 14): PriceHistory[] => {
  const basePrice = faker.number.float({ min: 200, max: 600 })

  return Array.from({ length: count }, (_, i) => ({
    id: faker.string.uuid(),
    booking_id: bookingId,
    timestamp: new Date(Date.now() - (count - i) * 24 * 60 * 60 * 1000).toISOString(),
    prices: generatePrices(basePrice + (i * faker.number.float({ min: -20, max: 20 }))),
    created_at: new Date(Date.now() - (count - i) * 24 * 60 * 60 * 1000).toISOString()
  }))
}

const generateHoldingPriceHistory = (bookingId: string, currentHoldingPrice: number): HoldingPriceHistory[] => {
  return [
    {
      id: faker.string.uuid(),
      booking_id: bookingId,
      price: currentHoldingPrice,
      effective_from: faker.date.past({ years: 1 }).toISOString(),
      effective_to: null,
      created_at: faker.date.past().toISOString()
    }
  ]
}

// Mock store interface
interface MockStore {
  bookings: Booking[]
  priceHistories: PriceHistory[]
  holdingPriceHistories: HoldingPriceHistory[]
}

// Initialize or load store from localStorage
const initializeMockStore = (): MockStore => {
  const savedStore = localStorage.getItem(STORAGE_KEY)

  if (savedStore) {
    try {
      return JSON.parse(savedStore)
    } catch (e) {
      console.warn('Failed to parse saved mock store, reinitializing')
    }
  }

  // Create initial data
  const bookings = Array.from({ length: 2 }, (_, i) =>
    generateMockBooking(`booking_${i + 1}`, i)
  )

  const priceHistories: PriceHistory[] = []
  const holdingPriceHistories: HoldingPriceHistory[] = []

  bookings.forEach(booking => {
    priceHistories.push(...generatePriceHistory(booking.id))
    holdingPriceHistories.push(...generateHoldingPriceHistory(booking.id, booking.holding_price || 0))
  })

  const store = { bookings, priceHistories, holdingPriceHistories }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store))
  return store
}

// Get current store
let mockStore = initializeMockStore()

// Helper to save store
const saveMockStore = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(mockStore))
}

// Mock Supabase client that implements the real Supabase API
export const createMockSupabaseClient = () => {
  return {
    from: (table: string) => ({
      select: (_columns: string = '*') => {
        const query = {
          data: [] as any[],
          error: null as any,

          eq: (column: string, value: any) => {
            if (table === 'bookings') {
              query.data = mockStore.bookings.filter(b => (b as any)[column] === value)
            } else if (table === 'price_histories') {
              query.data = mockStore.priceHistories.filter(h => (h as any)[column] === value)
            } else if (table === 'holding_price_histories') {
              query.data = mockStore.holdingPriceHistories.filter(h => (h as any)[column] === value)
            }
            return query
          },

          order: (column: string, options: { ascending?: boolean } = {}) => {
            const { ascending = true } = options
            query.data.sort((a, b) => {
              const aVal = (a as any)[column]
              const bVal = (b as any)[column]
              if (typeof aVal === 'string') {
                return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
              }
              return ascending ? aVal - bVal : bVal - aVal
            })
            return query
          },

          // Make it thenable for await/async
          then: (resolve: Function) => {
            // Simulate network delay
            setTimeout(() => {
              // Apply default filtering if no eq was called
              if (query.data.length === 0) {
                if (table === 'bookings') {
                  query.data = [...mockStore.bookings]
                } else if (table === 'price_histories') {
                  query.data = [...mockStore.priceHistories]
                } else if (table === 'holding_price_histories') {
                  query.data = [...mockStore.holdingPriceHistories]
                }
              }

              resolve({ data: query.data, error: query.error })
            }, 300)
          }
        }

        return query
      },

      insert: (data: any) => ({
        select: () => ({
          then: (resolve: Function) => {
            setTimeout(() => {
              const newItem = { ...data, id: faker.string.uuid(), created_at: new Date().toISOString() }

              if (table === 'bookings') {
                mockStore.bookings.push(newItem)
              } else if (table === 'price_histories') {
                mockStore.priceHistories.push(newItem)
              } else if (table === 'holding_price_histories') {
                mockStore.holdingPriceHistories.push(newItem)
              }

              saveMockStore()
              resolve({ data: [newItem], error: null })
            }, 300)
          }
        })
      }),

      update: (data: any) => ({
        eq: (column: string, value: any) => ({
          select: () => ({
            then: (resolve: Function) => {
              setTimeout(() => {
                let updatedItems: any[] = []

                if (table === 'bookings') {
                  mockStore.bookings = mockStore.bookings.map(item => {
                    if ((item as any)[column] === value) {
                      const updated = { ...item, ...data }
                      updatedItems.push(updated)
                      return updated
                    }
                    return item
                  })
                } else if (table === 'price_histories') {
                  mockStore.priceHistories = mockStore.priceHistories.map(item => {
                    if ((item as any)[column] === value) {
                      const updated = { ...item, ...data }
                      updatedItems.push(updated)
                      return updated
                    }
                    return item
                  })
                } else if (table === 'holding_price_histories') {
                  mockStore.holdingPriceHistories = mockStore.holdingPriceHistories.map(item => {
                    if ((item as any)[column] === value) {
                      const updated = { ...item, ...data }
                      updatedItems.push(updated)
                      return updated
                    }
                    return item
                  })
                }

                saveMockStore()
                resolve({ data: updatedItems, error: null })
              }, 300)
            }
          })
        })
      }),

      delete: () => ({
        eq: (column: string, value: any) => ({
          then: (resolve: Function) => {
            setTimeout(() => {
              if (table === 'bookings') {
                mockStore.bookings = mockStore.bookings.filter(item => (item as any)[column] !== value)
              } else if (table === 'price_histories') {
                mockStore.priceHistories = mockStore.priceHistories.filter(item => (item as any)[column] !== value)
              } else if (table === 'holding_price_histories') {
                mockStore.holdingPriceHistories = mockStore.holdingPriceHistories.filter(item => (item as any)[column] !== value)
              }

              saveMockStore()
              resolve({ data: null, error: null })
            }, 300)
          }
        })
      })
    })
  }
}

// Test utilities
export const testUtils = {
  getMockStore: () => mockStore,

  clearMockStore: () => {
    mockStore = { bookings: [], priceHistories: [], holdingPriceHistories: [] }
    saveMockStore()
  },

  resetMockStore: () => {
    localStorage.removeItem(STORAGE_KEY)
    mockStore = initializeMockStore()
  },

  addMockBooking: (bookingData?: Partial<Booking>) => {
    const id = `booking_${Date.now()}`
    const booking = generateMockBooking(id, mockStore.bookings.length)
    const newBooking = { ...booking, ...bookingData, id }

    mockStore.bookings.push(newBooking)
    mockStore.priceHistories.push(...generatePriceHistory(id))
    mockStore.holdingPriceHistories.push(...generateHoldingPriceHistory(id, newBooking.holding_price || 0))
    saveMockStore()

    return newBooking
  }
}
