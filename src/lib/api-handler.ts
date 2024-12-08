// src/lib/api-handler.ts
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
)

export interface NewBooking {
  location: string
  pickup_date: string
  dropoff_date: string
  category: string
  holding_price?: string
}

export interface HoldingPrices {
  booking1: string
  booking2: string
  booking3: string
}

export const adminApi = {
  checkPrices: async () => {
    try {
      // Trigger price check job
      const { data, error } = await supabase
        .rpc('check_rental_prices')
      
      if (error) throw error
      return { success: true, message: 'Price check initiated successfully' }
    } catch (error) {
      console.error('Error checking prices:', error)
      throw new Error('Failed to initiate price check')
    }
  },

  addBooking: async (booking: NewBooking) => {
    try {
      // Validate inputs
      if (!booking.location || !booking.pickup_date || !booking.dropoff_date || !booking.category) {
        throw new Error('Missing required booking fields')
      }

      // Create booking ID
      const booking_id = `${booking.location}_${booking.pickup_date}_${booking.dropoff_date}`.replace(/\//g, '')

      // Insert new booking
      const { data, error } = await supabase
        .from('bookings')
        .insert([{
          id: booking_id,
          location: booking.location,
          location_full_name: `${booking.location} Airport`,
          pickup_date: booking.pickup_date,
          dropoff_date: booking.dropoff_date,
          focus_category: booking.category,
          holding_price: booking.holding_price ? parseFloat(booking.holding_price) : null,
          pickup_time: '12:00 PM',
          dropoff_time: '12:00 PM',
          created_at: new Date().toISOString(),
          active: true
        }])

      if (error) throw error
      return { success: true, message: 'Booking added successfully' }
    } catch (error) {
      console.error('Error adding booking:', error)
      throw new Error('Failed to add booking')
    }
  },

  updateHoldingPrices: async (prices: HoldingPrices) => {
    try {
      // Get active bookings
      const { data: bookings, error: fetchError } = await supabase
        .from('bookings')
        .select('id')
        .eq('active', true)
        .limit(3)

      if (fetchError) throw fetchError

      // Update each booking's holding price
      const updates = bookings.map(async (booking, index) => {
        const priceKey = `booking${index + 1}` as keyof HoldingPrices
        const newPrice = prices[priceKey]

        if (newPrice) {
          const { error } = await supabase
            .from('bookings')
            .update({ holding_price: parseFloat(newPrice) })
            .eq('id', booking.id)

          if (error) throw error
        }
      })

      await Promise.all(updates)
      return { success: true, message: 'Holding prices updated successfully' }
    } catch (error) {
      console.error('Error updating holding prices:', error)
      throw new Error('Failed to update holding prices')
    }
  },

  deleteBooking: async (bookingNumber: string) => {
    try {
      // Get the nth active booking
      const { data: bookings, error: fetchError } = await supabase
        .from('bookings')
        .select('id')
        .eq('active', true)
        .limit(parseInt(bookingNumber))
        .order('created_at', { ascending: true })

      if (fetchError) throw fetchError

      const bookingToDelete = bookings[bookings.length - 1]
      if (!bookingToDelete) throw new Error('Booking not found')

      // Soft delete by marking as inactive
      const { error } = await supabase
        .from('bookings')
        .update({ active: false })
        .eq('id', bookingToDelete.id)

      if (error) throw error
      return { success: true, message: 'Booking deleted successfully' }
    } catch (error) {
      console.error('Error deleting booking:', error)
      throw new Error('Failed to delete booking')
    }
  }
}