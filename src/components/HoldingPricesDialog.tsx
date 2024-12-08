import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from 'lucide-react'

const formatPrice = (price) => `$${Number(price || 0).toFixed(2)}`

export function HoldingPricesDialog({ 
  open, 
  onOpenChange, 
  bookings = [], 
  onSubmit, 
  loading 
}) {
  // Initialize prices state with empty strings
  const [prices, setPrices] = useState({})
  const [message, setMessage] = useState('')

  // Reset prices when dialog opens or bookings change
  useEffect(() => {
    if (open || bookings.length > 0) {
      const initialPrices = {}
      bookings.forEach((booking, index) => {
        initialPrices[`booking${index + 1}`] = booking.holding_price?.toString() || ''
      })
      setPrices(initialPrices)
      setMessage('')
    }
  }, [open, bookings])

  const handleSubmit = async () => {
    if (hasInvalidInputs) {
      setMessage('Please enter valid prices');
      return;
    }
  
    // For each price update, create a new history entry
    const updates = Object.entries(prices).map(async ([key, value]) => {
      if (!value) return;
  
      const index = parseInt(key.replace('booking', '')) - 1;
      const booking = bookings[index];
      
      if (booking) {
        // Close current holding price history entry
        const { data: currentHistory } = await supabase
          .from('holding_price_histories')
          .select('*')
          .eq('booking_id', booking.id)
          .is('effective_to', null)
          .single();
  
        if (currentHistory) {
          await supabase
            .from('holding_price_histories')
            .update({ effective_to: new Date().toISOString() })
            .eq('id', currentHistory.id);
        }
  
        // Create new history entry
        await supabase
          .from('holding_price_histories')
          .insert({
            booking_id: booking.id,
            price: parseFloat(value),
            effective_from: new Date().toISOString(),
            effective_to: null
          });
      }
    });
  
    await Promise.all(updates);
    onSubmit(prices);
  };

  const handlePriceChange = (index, value) => {
    setPrices(prev => ({
      ...prev,
      [`booking${index + 1}`]: value
    }))
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Update Holding Prices</DialogTitle>
          <DialogDescription>
            Enter new holding prices for your tracked bookings.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          {bookings.map((booking, index) => (
            <Card key={booking.id} className="bg-muted/50">
              <CardContent className="pt-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">
                      {booking.location} ({booking.location_full_name})
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {booking.pickup_date} - {booking.dropoff_date}
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Category: {booking.focus_category}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Current Holding Price</p>
                    <p className="text-lg font-semibold">
                      {formatPrice(booking.holding_price)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <Label htmlFor={`price-${index}`} className="min-w-24">
                    New Price:
                  </Label>
                  <Input
                    id={`price-${index}`}
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder={`Enter new price for ${booking.location}`}
                    value={prices[`booking${index + 1}`] ?? ''}
                    onChange={(e) => handlePriceChange(index, e.target.value)}
                    className="flex-1"
                  />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {message && (
          <Alert>
            <AlertDescription>{message}</AlertDescription>
          </Alert>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Update Prices
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}