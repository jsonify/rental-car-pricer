// src/components/AdminInterface.tsx
import { useState } from 'react'
import { adminApi } from '@/lib/api-handler'
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
  DialogTrigger,
} from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from 'lucide-react'

export function AdminInterface() {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [dialogOpen, setDialogOpen] = useState(false)

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
    
    try {
      let result;
      
      switch (action) {
        case 'check-prices':
          result = await adminApi.checkPrices()
          break
        case 'add-booking':
          result = await adminApi.addBooking(newBooking)
          setNewBooking({
            location: '',
            pickup_date: '',
            dropoff_date: '',
            category: '',
            holding_price: ''
          })
          setDialogOpen(false)
          break
        case 'update-holding-prices':
          result = await adminApi.updateHoldingPrices(holdingPrices)
          setHoldingPrices({
            booking1: '',
            booking2: '',
            booking3: ''
          })
          setDialogOpen(false)
          break
        case 'delete-booking':
          result = await adminApi.deleteBooking(bookingToDelete)
          setBookingToDelete('')
          setDialogOpen(false)
          break
      }

      setMessage(result.message)
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>Admin Controls</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {/* Check Prices Button */}
        <div>
          <Button 
            onClick={() => handleAction('check-prices')}
            disabled={loading}
            className="w-full"
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Check Current Prices
          </Button>
        </div>

        {/* Add Booking Section */}
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" className="w-full">Add New Booking</Button>
          </DialogTrigger>
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

        {/* Update Prices Section */}
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" className="w-full">Update Holding Prices</Button>
          </DialogTrigger>
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

        {/* Delete Booking Section */}
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="destructive" className="w-full">Delete Booking</Button>
          </DialogTrigger>
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