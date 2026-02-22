import { useState, useEffect } from 'react'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { createSupabaseClient } from '@/lib/supabase'
import { triggerWorkflow } from '@/lib/github'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Loader2 } from 'lucide-react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DatePicker } from "@/components/ui/date-picker"
import { format } from "date-fns"
import type { Booking } from '@/lib/types'
import { useWorkflowStatus } from '@/hooks/useWorkflowStatus'
import { WorkflowStatusBanner } from './WorkflowStatusBanner'

export function AdminInterface() {
  const { isTestEnvironment } = useEnvironment()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [bookings, setBookings] = useState<Booking[]>([])
  const { workflowStatus, startTracking, reset: resetWorkflowStatus } = useWorkflowStatus()

  // Dialog states
  const [addBookingOpen, setAddBookingOpen] = useState(false)
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

      // Create category slug (remove spaces and special chars)
      const categorySlug = newBooking.category.replace(/[^a-zA-Z0-9]/g, '')

      if (isTestEnvironment) {
        // Test mode: Update database directly
        const bookingId = `${newBooking.location}_${pickupDateStr.replace(/\//g, '')}_${dropoffDateStr.replace(/\//g, '')}_${categorySlug}`

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

  const handleCheckPrices = async () => {
    setLoading(true)
    setMessage('')

    try {
      const runId = await triggerWorkflow({
        action: 'check-prices'
      })

      // Start tracking the workflow status
      startTracking(runId)
      setMessage('Price check workflow started! Tracking progress...')
    } catch (error) {
      console.error('Error triggering price check:', error)
      setMessage(error instanceof Error ? error.message : 'Failed to trigger price check')
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh bookings when workflow completes successfully
  useEffect(() => {
    if (workflowStatus.status === 'completed' && workflowStatus.conclusion === 'success') {
      fetchBookings()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workflowStatus.status, workflowStatus.conclusion])

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
    <div className="w-full max-w-2xl mx-auto mt-4 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
      <p className="text-slate-400 text-xs uppercase tracking-widest mb-1">
        Admin Controls {isTestEnvironment && <span className="text-amber-400 normal-case">(Test Mode)</span>}
      </p>

      {/* Workflow Status Banner */}
      {!isTestEnvironment && workflowStatus.runId && (
        <WorkflowStatusBanner
          status={workflowStatus}
          onDismiss={resetWorkflowStatus}
        />
      )}

      {/* Check Prices Button */}
      {!isTestEnvironment && (
        <button
          className="w-full bg-emerald-700 hover:bg-emerald-600 text-white border-0 rounded-lg py-2 px-4 text-sm font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          onClick={handleCheckPrices}
          disabled={loading || bookings.length === 0 || workflowStatus.status === 'in_progress' || workflowStatus.status === 'queued'}
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          Check Prices Now
        </button>
      )}

      {/* Add Booking Button */}
      <button
        className="w-full bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded-lg py-2 px-4 text-sm font-medium flex items-center justify-center gap-2 transition-colors"
        onClick={() => setAddBookingOpen(true)}
      >
        Add New Booking
      </button>

      {/* Delete Booking Button */}
      <button
        className="w-full bg-red-950 hover:bg-red-900 border border-red-800 text-red-400 rounded-lg py-2 px-4 text-sm font-medium flex items-center justify-center gap-2 transition-colors"
        onClick={() => setDeleteBookingOpen(true)}
      >
        Delete Booking
      </button>

      {message && (
        <p className="text-sm text-slate-400 text-center py-1">{message}</p>
      )}

      {/* Add Booking Dialog */}
      <Dialog open={addBookingOpen} onOpenChange={setAddBookingOpen}>
        <DialogContent className="bg-slate-900 border-slate-700 text-slate-100">
          <DialogHeader>
            <DialogTitle className="text-slate-100">Add New Booking</DialogTitle>
            <DialogDescription className="text-slate-400">Enter the details for the new booking.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <Input
              className="bg-slate-800 border-slate-700 text-slate-100 placeholder-slate-500"
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
              className="bg-slate-800 border-slate-700 text-slate-100 placeholder-slate-500"
              placeholder="Vehicle category"
              value={newBooking.category}
              onChange={(e) => setNewBooking({...newBooking, category: e.target.value})}
            />
            <Input
              className="bg-slate-800 border-slate-700 text-slate-100 placeholder-slate-500"
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

      {/* Delete Booking Dialog */}
      <Dialog open={deleteBookingOpen} onOpenChange={setDeleteBookingOpen}>
        <DialogContent className="bg-slate-900 border-slate-700 text-slate-100">
          <DialogHeader>
            <DialogTitle className="text-slate-100">Delete Booking</DialogTitle>
            <DialogDescription className="text-slate-400">Select a booking to delete.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <Select onValueChange={setBookingToDelete}>
              <SelectTrigger className="bg-slate-800 border-slate-700 text-slate-100">
                <SelectValue placeholder="Select booking to delete" />
              </SelectTrigger>
              <SelectContent className="bg-slate-800 border-slate-700">
                {bookings.map((booking, index) => (
                  <SelectItem key={booking.id} value={(index + 1).toString()} className="text-slate-200 focus:bg-slate-700 focus:text-slate-100">
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
    </div>
  )
}
