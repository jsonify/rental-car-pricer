// src/components/TestControls.tsx
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { testUtils } from '@/lib/supabase'
import { isDevelopment } from '@/lib/environment'

export const TestControls = () => {
  if (!isDevelopment) return null

  const handleAddBooking = () => {
    const newBooking = testUtils.generateMockBooking(`booking_${testUtils.mockStore.bookings.length + 1}`)
    testUtils.mockStore.bookings.push(newBooking)
    testUtils.mockStore.priceHistories.push(...testUtils.generatePriceHistory(newBooking.id))
    window.location.reload()
  }

  const handleResetData = () => {
    testUtils.resetMockStore()
    window.location.reload()
  }

  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle>Test Controls</CardTitle>
      </CardHeader>
      <CardContent className="flex gap-4">
        <Button onClick={handleAddBooking}>Add Test Booking</Button>
        <Button onClick={handleResetData} variant="outline">Reset Test Data</Button>
      </CardContent>
    </Card>
  )
}