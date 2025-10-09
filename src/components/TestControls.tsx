import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, Trash2, Plus, RefreshCw } from 'lucide-react'
import { useEnvironment } from '@/contexts/EnvironmentContext'
import { testUtils } from '@/lib/supabase'

export const TestControls = () => {
  const { isTestEnvironment } = useEnvironment()
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [addBookingOpen, setAddBookingOpen] = useState(false)
  const [clearConfirmOpen, setClearConfirmOpen] = useState(false)

  const [newBooking, setNewBooking] = useState({
    location: '',
    pickup_date: '',
    dropoff_date: '',
    category: '',
    holding_price: ''
  })

  // Only render if test environment is enabled
  if (!isTestEnvironment) return null

  const handleAddBooking = async () => {
    try {
      setLoading(true);
      setMessage('');

      if (!newBooking.location || !newBooking.pickup_date || !newBooking.dropoff_date || !newBooking.category) {
        setMessage('Please fill in all required fields');
        return;
      }

      testUtils.addMockBooking({
        location: newBooking.location,
        location_full_name: `${newBooking.location} International Airport`,
        pickup_date: newBooking.pickup_date,
        dropoff_date: newBooking.dropoff_date,
        focus_category: newBooking.category,
        holding_price: newBooking.holding_price ? parseFloat(newBooking.holding_price) : undefined,
        pickup_time: '12:00 PM',
        dropoff_time: '12:00 PM',
        active: true
      });

      setAddBookingOpen(false);
      setMessage('Booking added successfully');
      setNewBooking({ location: '', pickup_date: '', dropoff_date: '', category: '', holding_price: '' })
      window.location.reload();
    } catch (error) {
      console.error('Add error:', error);
      setMessage(error instanceof Error ? error.message : 'Failed to add booking');
    } finally {
      setLoading(false);
    }
  };

  const handleResetData = async () => {
    try {
      setLoading(true)
      setMessage('')

      // Reset to initial mock data state (2 bookings with random but consistent data)
      testUtils.resetMockStore()
      setMessage('Test data reset to initial state')
      window.location.reload()
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Failed to reset data')
    } finally {
      setLoading(false)
    }
  }

  const handleClearAllBookings = async () => {
    try {
      setLoading(true);
      setMessage('');

      testUtils.clearMockStore();

      setClearConfirmOpen(false);
      setMessage('All test bookings cleared');
      window.location.reload();
    } catch (error) {
      console.error('Clear error:', error);
      setMessage(error instanceof Error ? error.message : 'Failed to clear bookings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto mb-8">
      <Card>
        <CardHeader>
          <CardTitle>Test Controls</CardTitle>
          <CardDescription>
            Tools for managing test data - changes only affect the test environment
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-row gap-4">
            <Button 
              onClick={() => setAddBookingOpen(true)}
              disabled={loading}
              className="flex-1"
            >
              <Plus className="mr-2 h-4 w-4" />
              Add Test Booking
            </Button>
            
            <Button 
              onClick={() => handleResetData()} 
              variant="outline"
              disabled={loading}
              className="flex-1"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Reset to Initial Data
            </Button>
            
            <Button 
              onClick={() => setClearConfirmOpen(true)}
              variant="destructive"
              disabled={loading}
              className="flex-1"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Clear All Bookings
            </Button>
          </div>

          {message && (
            <Alert>
              <AlertDescription>{message}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Add Booking Dialog */}
      <Dialog open={addBookingOpen} onOpenChange={setAddBookingOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Test Booking</DialogTitle>
            <DialogDescription>
              Create a new test booking with your specified data
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="location">Airport Code*</Label>
              <Input
                id="location"
                placeholder="e.g., KOA"
                value={newBooking.location}
                onChange={(e) => setNewBooking({...newBooking, location: e.target.value.toUpperCase()})}
                maxLength={3}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="pickup_date">Pickup Date* (MM/DD/YYYY)</Label>
              <Input
                id="pickup_date"
                placeholder="MM/DD/YYYY"
                value={newBooking.pickup_date}
                onChange={(e) => setNewBooking({...newBooking, pickup_date: e.target.value})}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="dropoff_date">Dropoff Date* (MM/DD/YYYY)</Label>
              <Input
                id="dropoff_date"
                placeholder="MM/DD/YYYY"
                value={newBooking.dropoff_date}
                onChange={(e) => setNewBooking({...newBooking, dropoff_date: e.target.value})}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="category">Vehicle Category*</Label>
              <Input
                id="category"
                placeholder="e.g., Economy Car"
                value={newBooking.category}
                onChange={(e) => setNewBooking({...newBooking, category: e.target.value})}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="holding_price">Holding Price</Label>
              <Input
                id="holding_price"
                type="number"
                placeholder="Optional"
                value={newBooking.holding_price}
                onChange={(e) => setNewBooking({...newBooking, holding_price: e.target.value})}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAddBookingOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddBooking} disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Add Booking
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Clear Confirmation Dialog */}
      <Dialog open={clearConfirmOpen} onOpenChange={setClearConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear All Test Bookings</DialogTitle>
            <DialogDescription>
              This will remove all test bookings. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setClearConfirmOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleClearAllBookings} disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Clear All Bookings
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}