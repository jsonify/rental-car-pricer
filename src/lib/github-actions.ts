// src/lib/github-actions.ts
import { Octokit } from '@octokit/rest'
import { faker } from '@faker-js/faker'

const octokit = new Octokit({
  auth: import.meta.env.VITE_GITHUB_TOKEN
})

// GitHub repository details
const owner = import.meta.env.VITE_GITHUB_OWNER
const repo = import.meta.env.VITE_GITHUB_REPO

// Mock data generators
const generateMockPrices = (basePrice: number) => {
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

const generateMockPriceHistory = (bookingId: string, days = 14) => {
  const basePrice = faker.number.float({ min: 200, max: 600 })
  return Array.from({ length: days }, (_, i) => ({
    id: faker.string.uuid(),
    booking_id: bookingId,
    timestamp: faker.date.recent({ days: days - i }).toISOString(),
    prices: generateMockPrices(basePrice + (i * faker.number.float({ min: -20, max: 20 }))),
    created_at: faker.date.past().toISOString()
  }))
}

// Mock data store
let mockStore = {
  bookings: [] as any[],
  priceHistories: [] as any[],
  workflowStatus: 'unknown' as 'unknown' | 'pending' | 'completed' | 'failed'
}

export const githubActions = {


  clearMockStore: () => {
    mockStore.bookings.length = 0;
    mockStore.priceHistories.length = 0;
    mockStore.workflowStatus = 'unknown';
    
    // Important: Save to localStorage to persist the empty state
    localStorage.setItem('mockStore', JSON.stringify(mockStore));
    
    return { success: true };
  },

  triggerWorkflow: async (action: string, inputs: Record<string, string> = {}) => {
    if (window.localStorage.getItem('use-test-environment') === 'true') {
      mockStore.workflowStatus = 'pending';
      await new Promise(resolve => setTimeout(resolve, 1000));

      switch (action) {
        case 'add-booking': {
          // Generate a unique ID
          const newId = `booking_${Date.now()}`;
          
          // Create new booking with provided inputs
          const newBooking = {
            id: newId,
            location: inputs.new_booking_location,
            location_full_name: `${inputs.new_booking_location} International Airport`,
            pickup_date: inputs.new_booking_pickup_date,
            dropoff_date: inputs.new_booking_dropoff_date,
            focus_category: inputs.new_booking_category,
            holding_price: inputs.new_booking_holding_price ? parseFloat(inputs.new_booking_holding_price) : null,
            active: true,
            created_at: new Date().toISOString()
          };

          // Add to existing bookings array
          mockStore.bookings.push(newBooking);

          // Generate price history for new booking
          const newPriceHistories = generateMockPriceHistory(newId);
          mockStore.priceHistories.push(...newPriceHistories);

          // Persist updated store to localStorage
          localStorage.setItem('mockStore', JSON.stringify(mockStore));
          break;
        }

        case 'update-holding-prices': {
          mockStore.bookings = mockStore.bookings.map((booking, index) => ({
            ...booking,
            holding_price: parseFloat(inputs[`booking_${index + 1}_price`] as string) || booking.holding_price
          }))
          break
        }

        case 'delete-booking': {
          const indexToDelete = parseInt(inputs.booking_to_delete || '1') - 1
          if (indexToDelete >= 0 && indexToDelete < mockStore.bookings.length) {
            const bookingId = mockStore.bookings[indexToDelete].id
            mockStore.bookings = mockStore.bookings.filter((_, i) => i !== indexToDelete)
            mockStore.priceHistories = mockStore.priceHistories.filter(h => h.booking_id !== bookingId)
          }
          break
        }
      }

      mockStore.workflowStatus = 'completed'
      return { success: true }
    }

    // Production GitHub Actions call
    try {
      const response = await octokit.actions.createWorkflowDispatch({
        owner,
        repo,
        workflow_id: 'price-checker.yaml',
        ref: 'main',
        inputs: {
          action,
          ...inputs
        }
      })

      return { success: true }
    } catch (error) {
      console.error('Error triggering workflow:', error)
      throw new Error('Failed to trigger GitHub workflow')
    }
  },
   // Initialize store with persistence
   initializeMockStore: () => {
    // Try to load existing store from localStorage
    const savedStore = localStorage.getItem('mockStore');
    if (savedStore) {
      const parsed = JSON.parse(savedStore);
      mockStore.bookings = parsed.bookings;
      mockStore.priceHistories = parsed.priceHistories;
      return;
    }

    // If no saved store, initialize with default data
    mockStore.bookings = [
      {
        id: 'booking_1',
        location: 'KOA',
        location_full_name: 'KOA International Airport',
        pickup_date: '04/01/2025',
        dropoff_date: '04/08/2025',
        focus_category: 'Economy Car',
        holding_price: 299.99,
        active: true,
        created_at: new Date().toISOString()
      },
      {
        id: 'booking_2',
        location: 'HNL',
        location_full_name: 'HNL International Airport',
        pickup_date: '05/15/2025',
        dropoff_date: '05/22/2025',
        focus_category: 'Standard SUV',
        holding_price: 499.99,
        active: true,
        created_at: new Date().toISOString()
      }
    ];

    // Generate initial price histories
    mockStore.priceHistories = [];
    mockStore.bookings.forEach(booking => {
      mockStore.priceHistories.push(...generateMockPriceHistory(booking.id));
    });

    // Save initial state to localStorage
    localStorage.setItem('mockStore', JSON.stringify(mockStore));
  },

  // Add a method to get current store state
  getMockStore: () => {
    return mockStore;
  },

  getWorkflowStatus: async () => {
    if (window.localStorage.getItem('use-test-environment') === 'true') {
      return mockStore.workflowStatus
    }

    try {
      const { data } = await octokit.actions.listWorkflowRuns({
        owner,
        repo,
        workflow_id: 'price-checker.yaml',
        per_page: 1
      })

      return data.workflow_runs[0]?.status || 'unknown'
    } catch (error) {
      console.error('Error getting workflow status:', error)
      return 'unknown'
    }
  },
}

// Initialize mock store
githubActions.initializeMockStore()