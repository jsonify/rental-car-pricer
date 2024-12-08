import { useState, useEffect } from 'react'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { githubActions } from '@/lib/github-actions'
import { createSupabaseClient } from '@/lib/supabase'
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
import { Loader2, RefreshCw } from 'lucide-react'
import {HoldingPricesDialog} from './HoldingPricesDialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function AdminInterface() {
  const { isTestEnvironment } = useEnvironment()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [workflowStatus, setWorkflowStatus] = useState('unknown')
  const [bookings, setBookings] = useState([])
  
  // Dialog states
  const [addBookingOpen, setAddBookingOpen] = useState(false)
  const [updatePricesOpen, setUpdatePricesOpen] = useState(false)
  const [deleteBookingOpen, setDeleteBookingOpen] = useState(false)

  const [newBooking, setNewBooking] = useState({
    location: '',
    pickup_date: '',
    dropoff_date: '',
    category: '',
    holding_price: ''
  })

  const [bookingToDelete, setBookingToDelete] = useState('')

  // Initialize Supabase client
  const supabase = createSupabaseClient(isTestEnvironment)

  // Fetch bookings
  useEffect(() => {
    const fetchBookings = async () => {
      try {
        if (isTestEnvironment) {
          // Get data from mock store
          const mockStore = githubActions.getMockStore()
          setBookings(mockStore.bookings)
        } else {
          // Get data from Supabase
          const { data, error } = await supabase
            .from('bookings')
            .select('*')
            .eq('active', true)
            .order('created_at', { ascending: true })

          if (error) throw error
          setBookings(data || [])
        }
      } catch (error) {
        console.error('Error fetching bookings:', error)
        setMessage('Failed to load bookings')
      }
    }

    fetchBookings()
  }, [isTestEnvironment])

  const handleAction = async (action, inputs = {}) => {
    setLoading(true)
    setMessage('')
    setWorkflowStatus('pending')
    
    try {
      if (isTestEnvironment) {
        const result = await githubActions.triggerWorkflow(action, inputs)
        if (result.success) {
          setMessage('Mock action completed successfully')
          window.location.reload()
        }
      } else {
        // Handle production actions
        switch (action) {
          case 'update-holding-prices':
            // Update each booking's holding price in Supabase
            for (const [key, value] of Object.entries(inputs)) {
              if (value) {
                const bookingIndex = parseInt(key.replace('booking_', '')) - 1
                const booking = bookings[bookingIndex]
                if (booking) {
                  const { error } = await supabase
                    .from('bookings')
                    .update({ holding_price: parseFloat(value) })
                    .eq('id', booking.id)

                  if (error) throw error
                }
              }
            }
            setMessage('Holding prices updated successfully')
            window.location.reload()
            break

          // ... handle other actions ...
        }
      }
    } catch (error) {
      console.error('Error:', error)
      setMessage(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto mt-8">
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Admin Controls {isTestEnvironment && '(Test Mode)'}</span>
          {workflowStatus !== 'unknown' && (
            <div className="text-sm font-normal">
              Status: {workflowStatus}
              {loading && <RefreshCw className="ml-2 h-4 w-4 animate-spin inline" />}
            </div>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="flex flex-col gap-4">
        {/* Check Prices Button */}
        <Button 
          onClick={() => handleAction('check-prices')}
          disabled={loading}
          className="w-full"
        >
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Check Current Prices {isTestEnvironment && '(Mock)'}
        </Button>

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
              <Input
                type="text"
                placeholder="Pickup date (MM/DD/YYYY)"
                value={newBooking.pickup_date}
                onChange={(e) => setNewBooking({...newBooking, pickup_date: e.target.value})}
              />
              <Input
                type="text"
                placeholder="Dropoff date (MM/DD/YYYY)"
                value={newBooking.dropoff_date}
                onChange={(e) => setNewBooking({...newBooking, dropoff_date: e.target.value})}
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
                onClick={() => handleAction('add-booking', {
                  new_booking_location: newBooking.location,
                  new_booking_pickup_date: newBooking.pickup_date,
                  new_booking_dropoff_date: newBooking.dropoff_date,
                  new_booking_category: newBooking.category,
                  new_booking_holding_price: newBooking.holding_price
                })}
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
          onSubmit={(prices) => handleAction('update-holding-prices', {
            booking_1_price: prices.booking1,
            booking_2_price: prices.booking2,
            booking_3_price: prices.booking3
          })}
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
                onClick={() => handleAction('delete-booking', {
                  booking_to_delete: bookingToDelete
                })}
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