import { useState, useEffect } from 'react'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { createSupabaseClient } from '@/lib/supabase'
import { triggerWorkflow } from '@/lib/github'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from 'lucide-react'
import {HoldingPricesDialog} from './HoldingPricesDialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DatePicker } from "@/components/ui/date-picker"
import { format } from "date-fns"
import type { Booking } from '@/lib/types'

export function AdminInterface() {
  const { isTestEnvironment } = useEnvironment()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [bookings, setBookings] = useState<Booking[]>([])

  // Dialog states
  const [addBookingOpen, setAddBookingOpen] = useState(false)
  const [updatePricesOpen, setUpdatePricesOpen] = useState(false)
  const [deleteBookingOpen, setDeleteBookingOpen] = useState(false)

  const [newBooking, setNewBooking] = useState({
    location: '',
    pickup_date: undefined as Date | undefined,
    dropoff_date: undefined as Date | undefined,
    category: '',
    holding_price: ''
  })

  const [bookingToDelete, setBookingToDelete] = useState('')

  // Initialize Supabase client
  const supabase = createSupabaseClient(isTestEnvironment)

  // Fetch bookings
  const fetchBookings = async () => {
    try {
      const { data, error } = await supabase
        .from('bookings')
        .select('*')
        .eq('active', true)
        .order('created_at', { ascending: true })

      if (error) throw error
      setBookings(data || [])
    } catch (error) {
      console.error('Error fetching bookings:', error)
      setMessage('Failed to load bookings')
    }
  }

  useEffect(() => {
    fetchBookings()
  }, [isTestEnvironment])

  const handleAddBooking = async () => {
    setLoading(true)
    setMessage('')

    try {
      // Validate dates are selected
      if (!newBooking.pickup_date || !newBooking.dropoff_date) {
        setMessage('Please select pickup and dropoff dates')
        setLoading(false)
        return
      }

      // Format dates as MM/DD/YYYY
      const pickupDateStr = format(newBooking.pickup_date, 'MM/dd/yyyy')
      const dropoffDateStr = format(newBooking.dropoff_date, 'MM/dd/yyyy')

      if (isTestEnvironment) {
        // Test mode: Update database directly
        const bookingId = `${newBooking.location}_${pickupDateStr.replace(/\//g, '')}_${dropoffDateStr.replace(/\//g, '')}`

        const { error } = await supabase
          .from('bookings')
          .insert({
            id: bookingId,
            location: newBooking.location,
            location_full_name: `${newBooking.location} International Airport`,
            pickup_date: pickupDateStr,
            dropoff_date: dropoffDateStr,
            pickup_time: '12:00 PM',
            dropoff_time: '12:00 PM',
            focus_category: newBooking.category,
            holding_price: newBooking.holding_price ? parseFloat(newBooking.holding_price) : null,
            active: true
          })
          .select()

        if (error) throw error

        // If a holding price was provided, create initial history entry
        if (newBooking.holding_price) {
          const { error: historyError } = await supabase
            .from('holding_price_histories')
            .insert({
              booking_id: bookingId,
              price: parseFloat(newBooking.holding_price),
              effective_from: new Date().toISOString(),
              effective_to: null
            })

          if (historyError) throw historyError
        }

        setMessage('Booking added successfully (test mode)')
      } else {
        // Production mode: Trigger GitHub Actions workflow
        await triggerWorkflow({
          action: 'add-booking',
          new_booking_location: newBooking.location,
          new_booking_pickup_date: pickupDateStr,
          new_booking_dropoff_date: dropoffDateStr,
          new_booking_category: newBooking.category,
          new_booking_holding_price: newBooking.holding_price || undefined
        })

        setMessage('Workflow triggered! Check GitHub Actions for status.')
      }

      setAddBookingOpen(false)
      setNewBooking({ location: '', pickup_date: undefined, dropoff_date: undefined, category: '', holding_price: '' })

      // Refresh bookings after a delay in production mode
      if (!isTestEnvironment) {
        setTimeout(() => fetchBookings(), 5000)
      } else {
        await fetchBookings()
      }
    } catch (error) {
      console.error('Error adding booking:', error)
      setMessage(error instanceof Error ? error.message : 'Failed to add booking')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateHoldingPrices = async (prices: Record<string, string>) => {
    setLoading(true)
    setMessage('')

    try {
      if (isTestEnvironment) {
        // Test mode: Update database directly
        for (const [key, value] of Object.entries(prices)) {
          if (value) {
            const bookingIndex = parseInt(key.replace('booking', '')) - 1
            const booking = bookings[bookingIndex]
            if (booking) {
              const newPrice = parseFloat(value)

              // Close current holding price history entry (set effective_to)
              const { data: currentHistory } = await supabase
                .from('holding_price_histories')
                .select('*')
                .eq('booking_id', booking.id)
                .is('effective_to', null)
                .single()

              if (currentHistory) {
                await supabase
                  .from('holding_price_histories')
                  .update({ effective_to: new Date().toISOString() })
                  .eq('id', currentHistory.id)
              }

              // Create new history entry
              const { error: historyError } = await supabase
                .from('holding_price_histories')
                .insert({
                  booking_id: booking.id,
                  price: newPrice,
                  effective_from: new Date().toISOString(),
                  effective_to: null
                })

              if (historyError) throw historyError

              // Update the booking's current holding_price
              const { error: bookingError } = await supabase
                .from('bookings')
                .update({ holding_price: newPrice })
                .eq('id', booking.id)

              if (bookingError) throw bookingError
            }
          }
        }

        setMessage('Holding prices updated successfully (test mode)')
        await fetchBookings()
      } else {
        // Production mode: Trigger workflow for each price update
        // The workflow expects JSON format: [booking_number, price]
        for (const [key, value] of Object.entries(prices)) {
          if (value) {
            const bookingNumber = parseInt(key.replace('booking', ''))
            const updatesJson = JSON.stringify([bookingNumber, parseFloat(value)])

            await triggerWorkflow({
              action: 'update-holding-prices',
              booking_updates_json: updatesJson
            })
          }
        }

        setMessage('Workflow(s) triggered! Check GitHub Actions for status.')
        // Refresh bookings after a delay
        setTimeout(() => fetchBookings(), 5000)
      }

      setUpdatePricesOpen(false)
    } catch (error) {
      console.error('Error updating prices:', error)
      setMessage(error instanceof Error ? error.message : 'Failed to update prices')
    } finally {
      setLoading(false)
    }
  }

  const handleCheckPrices = async () => {
    setLoading(true)
    setMessage('')

    try {
      await triggerWorkflow({
        action: 'check-prices'
      })

      setMessage('Price check workflow triggered! Check GitHub Actions for status.')
      // Refresh bookings after workflow completes (rough estimate)
      setTimeout(() => fetchBookings(), 30000) // 30 seconds
    } catch (error) {
      console.error('Error triggering price check:', error)
      setMessage(error instanceof Error ? error.message : 'Failed to trigger price check')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteBooking = async () => {
    setLoading(true)
    setMessage('')

    try {
      if (isTestEnvironment) {
        // Test mode: Update database directly
        const bookingIndex = parseInt(bookingToDelete) - 1
        const booking = bookings[bookingIndex]

        if (!booking) throw new Error('Booking not found')

        const { error } = await supabase
          .from('bookings')
          .update({ active: false })
          .eq('id', booking.id)

        if (error) throw error

        setMessage('Booking deleted successfully (test mode)')
        await fetchBookings()
      } else {
        // Production mode: Trigger GitHub Actions workflow
        await triggerWorkflow({
          action: 'delete-booking',
          booking_to_delete: bookingToDelete
        })

        setMessage('Workflow triggered! Check GitHub Actions for status.')
        // Refresh bookings after a delay
        setTimeout(() => fetchBookings(), 5000)
      }

      setDeleteBookingOpen(false)
      setBookingToDelete('')
    } catch (error) {
      console.error('Error deleting booking:', error)
      setMessage(error instanceof Error ? error.message : 'Failed to delete booking')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto mt-8">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Admin Controls {isTestEnvironment && '(Test Mode)'}</span>
        </CardTitle>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {/* Check Prices Button */}
        {!isTestEnvironment && (
          <Button
            variant="default"
            className="w-full"
            onClick={handleCheckPrices}
            disabled={loading || bookings.length === 0}
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Check Prices Now
          </Button>
        )}

        {/* Add Booking Button */}
        <Button
          variant="outline"
          className="w-full"
          onClick={() => setAddBookingOpen(true)}
        >
          Add New Booking
        </Button>

        {/* Update Prices Button */}
        <Button
          variant="outline"
          className="w-full"
          onClick={() => setUpdatePricesOpen(true)}
        >
          Update Holding Prices
        </Button>

        {/* Delete Booking Button */}
        <Button
          variant="destructive"
          className="w-full"
          onClick={() => setDeleteBookingOpen(true)}
        >
          Delete Booking
        </Button>

        {message && (
          <Alert>
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}

        {/* Add Booking Dialog */}
        <Dialog open={addBookingOpen} onOpenChange={setAddBookingOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Booking</DialogTitle>
              <DialogDescription>Enter the details for the new booking.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <Input
                placeholder="Airport code (e.g., KOA)"
                value={newBooking.location}
                onChange={(e) => setNewBooking({...newBooking, location: e.target.value})}
              />
              <DatePicker
                date={newBooking.pickup_date}
                onDateChange={(date) => setNewBooking({...newBooking, pickup_date: date})}
                placeholder="Select pickup date"
              />
              <DatePicker
                date={newBooking.dropoff_date}
                onDateChange={(date) => setNewBooking({...newBooking, dropoff_date: date})}
                placeholder="Select dropoff date"
              />
              <Input
                placeholder="Vehicle category"
                value={newBooking.category}
                onChange={(e) => setNewBooking({...newBooking, category: e.target.value})}
              />
              <Input
                type="number"
                placeholder="Holding price (optional)"
                value={newBooking.holding_price}
                onChange={(e) => setNewBooking({...newBooking, holding_price: e.target.value})}
              />
              <Button
                onClick={handleAddBooking}
                disabled={loading}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Add Booking
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Holding Prices Dialog */}
        <HoldingPricesDialog
          open={updatePricesOpen}
          onOpenChange={setUpdatePricesOpen}
          bookings={bookings}
          onSubmit={handleUpdateHoldingPrices}
          loading={loading}
        />

        {/* Delete Booking Dialog */}
        <Dialog open={deleteBookingOpen} onOpenChange={setDeleteBookingOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Delete Booking</DialogTitle>
              <DialogDescription>Select a booking to delete.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <Select onValueChange={setBookingToDelete}>
                <SelectTrigger>
                  <SelectValue placeholder="Select booking to delete" />
                </SelectTrigger>
                <SelectContent>
                  {bookings.map((booking, index) => (
                    <SelectItem key={booking.id} value={(index + 1).toString()}>
                      {booking.location}: {booking.pickup_date} to {booking.dropoff_date}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={handleDeleteBooking}
                disabled={loading || !bookingToDelete}
                variant="destructive"
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Delete Booking
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  )
}