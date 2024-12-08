import { useState } from 'react'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { githubActions } from '@/lib/github-actions'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select"
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, RefreshCw } from 'lucide-react'

export function AdminInterface() {
  const { isTestEnvironment } = useEnvironment()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [workflowStatus, setWorkflowStatus] = useState<string>('unknown')
  
  // Separate dialog states
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

  const [holdingPrices, setHoldingPrices] = useState({
    booking1: '',
    booking2: '',
    booking3: ''
  })

  const [bookingToDelete, setBookingToDelete] = useState('')

  const handleAction = async (action: string) => {
    setLoading(true)
    setMessage('')
    setWorkflowStatus('pending')
    
    try {
      let inputs = {}
      
      switch (action) {
        case 'add-booking':
          inputs = {
            new_booking_location: newBooking.location,
            new_booking_pickup_date: newBooking.pickup_date,
            new_booking_dropoff_date: newBooking.dropoff_date,
            new_booking_category: newBooking.category,
            new_booking_holding_price: newBooking.holding_price
          }
          setAddBookingOpen(false)
          break
          
        case 'update-holding-prices':
          inputs = {
            booking_1_price: holdingPrices.booking1,
            booking_2_price: holdingPrices.booking2,
            booking_3_price: holdingPrices.booking3
          }
          setUpdatePricesOpen(false)
          break
          
        case 'delete-booking':
          inputs = {
            booking_to_delete: bookingToDelete
          }
          setDeleteBookingOpen(false)
          break
      }
  
      const result = await githubActions.triggerWorkflow(action, inputs)
      
      if (result.success) {
        setMessage(isTestEnvironment ? 
          `Mock ${action} completed successfully` : 
          'Action started. Checking status...'
        )
  
        // Reset form data
        switch (action) {
          case 'add-booking':
            setNewBooking({
              location: '',
              pickup_date: '',
              dropoff_date: '',
              category: '',
              holding_price: ''
            })
            break
            
          case 'update-holding-prices':
            setHoldingPrices({
              booking1: '',
              booking2: '',
              booking3: ''
            })
            break
            
          case 'delete-booking':
            setBookingToDelete('')
            break
        }
  
        if (isTestEnvironment) {
          window.location.reload()
        }
      }
      
    } catch (error) {
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

        {/* Add Booking Dialog */}
        <Dialog open={addBookingOpen} onOpenChange={setAddBookingOpen}>
          <Button variant="outline" className="w-full" onClick={() => setAddBookingOpen(true)}>
            Add New Booking
          </Button>
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
                onClick={() => handleAction('add-booking')}
                disabled={loading}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Add Booking
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Update Prices Dialog */}
        <Dialog open={updatePricesOpen} onOpenChange={setUpdatePricesOpen}>
          <Button variant="outline" className="w-full" onClick={() => setUpdatePricesOpen(true)}>
            Update Holding Prices
          </Button>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Update Holding Prices</DialogTitle>
              <DialogDescription>Enter new holding prices for your bookings.</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <Input
                type="number"
                placeholder="Booking 1 new price"
                value={holdingPrices.booking1}
                onChange={(e) => setHoldingPrices({...holdingPrices, booking1: e.target.value})}
              />
              <Input
                type="number"
                placeholder="Booking 2 new price"
                value={holdingPrices.booking2}
                onChange={(e) => setHoldingPrices({...holdingPrices, booking2: e.target.value})}
              />
              <Input
                type="number"
                placeholder="Booking 3 new price"
                value={holdingPrices.booking3}
                onChange={(e) => setHoldingPrices({...holdingPrices, booking3: e.target.value})}
              />
              <Button 
                onClick={() => handleAction('update-holding-prices')}
                disabled={loading}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Update Holding Prices
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {/* Delete Booking Dialog */}
        <Dialog open={deleteBookingOpen} onOpenChange={setDeleteBookingOpen}>
          <Button 
            variant="destructive" 
            className="w-full"
            onClick={() => setDeleteBookingOpen(true)}
          >
            Delete Booking
          </Button>
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
                  <SelectItem value="1">Booking 1</SelectItem>
                  <SelectItem value="2">Booking 2</SelectItem>
                  <SelectItem value="3">Booking 3</SelectItem>
                </SelectContent>
              </Select>
              <Button 
                onClick={() => handleAction('delete-booking')}
                disabled={loading}
                variant="destructive"
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Delete Booking
              </Button>
            </div>
          </DialogContent>
        </Dialog>

        {message && (
          <Alert>
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}