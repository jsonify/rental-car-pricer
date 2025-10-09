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
    // Validate that at least one price was entered
    const hasAnyPrices = Object.values(prices).some(value => value && !isNaN(parseFloat(value)))

    if (!hasAnyPrices) {
      setMessage('Please enter at least one valid price')
      return
    }

    // Call the parent's onSubmit handler
    await onSubmit(prices)
  }

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