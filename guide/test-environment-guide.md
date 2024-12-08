# Test Environment Implementation Guide

## Overview

The test environment system allows developers to toggle between real production data from Supabase and mock data for testing purposes. This is implemented through a combination of React Context, mock data generators, and environment-aware components.

## Core Components

### 1. Environment Context

```tsx
// src/contexts/EnvironmentContext.tsx
export const EnvironmentProvider = ({ children }: { children: ReactNode }) => {
  const [isTestEnvironment, setIsTestEnvironment] = useState(() => {
    const stored = localStorage.getItem('use-test-environment')
    return stored ? JSON.parse(stored) : false
  })

  useEffect(() => {
    localStorage.setItem('use-test-environment', JSON.stringify(isTestEnvironment))
  }, [isTestEnvironment])

  return (
    <EnvironmentContext.Provider value={{ isTestEnvironment, setIsTestEnvironment }}>
      {children}
    </EnvironmentContext.Provider>
  )
}
```

### 2. Mock Data Store

```typescript
// Mock data structure in github-actions.ts
let mockStore = {
  bookings: [] as Booking[],
  priceHistories: [] as PriceHistory[],
  workflowStatus: 'unknown' as 'unknown' | 'pending' | 'completed' | 'failed'
}
```

## Key Features

### 1. Environment Toggle

- Implemented through the EnvironmentSwitcher component
- Persists selection in localStorage
- Visually indicates current environment

### 2. Mock Data Generation

The system uses Faker.js to generate realistic test data:

```typescript
const generateMockBooking = (id: string) => ({
  id,
  location: faker.helpers.arrayElement(['KOA', 'HNL', 'OGG', 'LIH']),
  location_full_name: `${location} International Airport`,
  pickup_date: faker.date.future().toLocaleDateString(),
  dropoff_date: faker.date.future().toLocaleDateString(),
  focus_category: faker.helpers.arrayElement([
    'Economy Car', 'Compact Car', 'Standard SUV', 'Full-size Car'
  ]),
  holding_price: faker.number.float({ min: 200, max: 600 }),
  active: true,
  created_at: faker.date.past().toISOString()
})
```

### 3. Action Simulation

Test environment simulates API actions with delays for realism:

```typescript
const simulateAction = async () => {
  mockStore.workflowStatus = 'pending'
  await new Promise(resolve => setTimeout(resolve, 1000))
  // Perform mock action
  mockStore.workflowStatus = 'completed'
}
```

## Implementation Guide

### 1. Setup Test Environment

```tsx
// In your main App component
import { EnvironmentProvider } from '@/contexts/EnvironmentContext'

function App() {
  return (
    <EnvironmentProvider>
      <div className="min-h-screen bg-gray-50">
        <EnvironmentSwitcher />
        {/* Other components */}
      </div>
    </EnvironmentProvider>
  )
}
```

### 2. Use Environment Context

```tsx
import { useEnvironment } from '@/contexts/EnvironmentContext'

function YourComponent() {
  const { isTestEnvironment } = useEnvironment()
  
  const fetchData = async () => {
    if (isTestEnvironment) {
      // Use mock data
      return mockStore.bookings
    } else {
      // Use real Supabase client
      return supabase.from('bookings').select('*')
    }
  }
}
```

### 3. Handle Actions

```typescript
const handleAction = async (action: string, inputs: Record<string, any>) => {
  if (isTestEnvironment) {
    // Simulate action
    await simulateAction(action, inputs)
    // Update mock store
    updateMockStore(action, inputs)
  } else {
    // Trigger real GitHub workflow
    await githubActions.triggerWorkflow(action, inputs)
  }
}
```

## Test Environment Features

### 1. Data Persistence
- Mock data persists during the session
- Resets on page refresh
- Can be manually reset via UI

### 2. Realistic Behavior
- Simulated loading states
- Artificial delays
- Error simulation
- Workflow status updates

### 3. Action Handling
- Add booking
- Update prices
- Delete booking
- Price checks

## Best Practices

1. **Always Check Environment**
```typescript
if (isTestEnvironment) {
  // Test behavior
} else {
  // Production behavior
}
```

2. **Reset Test Data**
```typescript
const resetTestData = () => {
  githubActions.initializeMockStore()
  window.location.reload()
}
```

3. **Handle Loading States**
```typescript
const [loading, setLoading] = useState(false)

const handleAction = async () => {
  setLoading(true)
  try {
    await performAction()
  } finally {
    setLoading(false)
  }
}
```

## Common Issues and Solutions

1. **Mock Data Not Updating**
- Ensure you're updating mockStore correctly
- Check that components are re-rendering
- Verify environment toggle state

2. **Actions Not Working**
- Confirm action handlers are environment-aware
- Check mock action simulation
- Verify workflow status updates

3. **UI Inconsistencies**
- Ensure loading states are properly managed
- Verify error handling
- Check component re-rendering

## Development Workflow

1. Start in test environment
2. Develop and test features with mock data
3. Toggle to production environment
4. Test with real data
5. Switch back to test for edge cases

## Testing Tools

```typescript
// Test utilities
export const testUtils = {
  generateMockBooking,
  generatePriceHistory,
  mockStore,
  resetMockStore: () => {
    mockStore.bookings = []
    mockStore.priceHistories = []
    githubActions.initializeMockStore()
  }
}
```

Remember to:
- Initialize mock store on application start
- Handle environment changes gracefully
- Maintain realistic data patterns
- Test both environments thoroughly
