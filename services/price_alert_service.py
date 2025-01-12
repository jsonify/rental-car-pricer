"""
Service responsible for managing price alerts based on booking data.
Handles alert thresholds, expired booking filtering, and email notifications.
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging
from email_module import send_price_alert

class PriceAlertService:
    """Manages price alerts and threshold checking for car rental bookings"""
    
    def __init__(self, price_threshold: float = 10.0):
        """
        Initialize the price alert service
        
        Args:
            price_threshold: Minimum price drop (in dollars) to trigger an alert
        """
        self.price_threshold = price_threshold
    
    def filter_active_bookings(self, bookings_data: List[Dict]) -> List[Dict]:
        """Filter out expired bookings based on dropoff date"""
        current_date = datetime.now().date()
        active_bookings = []
        expired_bookings = []
        
        for booking_data in bookings_data:
            try:
                booking = booking_data['booking']
                dropoff_date = datetime.strptime(booking['dropoff_date'], "%m/%d/%Y").date()
                
                if dropoff_date >= current_date:
                    active_bookings.append(booking_data)
                else:
                    expired_bookings.append(f"{booking['location']} ({booking['dropoff_date']})")
            except (KeyError, ValueError) as e:
                print(f"Error processing booking: {str(e)}")
                continue
        
        if expired_bookings:
            print(f"Skipping expired bookings: {', '.join(expired_bookings)}")
        
        print(f"Found {len(active_bookings)} active bookings")
        return active_bookings
    
    def check_price_drops(self, bookings_data: List[Dict]) -> List[Dict]:
        """
        Check for significant price drops in bookings
        
        Returns:
            List of bookings with price drops exceeding the threshold
        """
        significant_drops = []
        
        for booking_data in bookings_data:
            try:
                booking = booking_data['booking']
                prices = booking_data.get('prices', {})
                focus_category = booking['focus_category']
                
                if focus_category not in prices:
                    print(f"Warning: Focus category {focus_category} not found in prices for {booking['location']}")
                    continue

                current_price = prices[focus_category]
                
                # Get the previous price from history if available
                price_history = booking.get('price_history', [])
                if len(price_history) > 1:
                    prev_record = price_history[-2]
                    prev_prices = prev_record.get('prices', {})
                    if focus_category in prev_prices:
                        previous_price = prev_prices[focus_category]
                        price_drop = previous_price - current_price
                        
                        if price_drop >= self.price_threshold:
                            significant_drops.append(booking_data)
                            print(
                                f"Significant price drop found for {booking['location']}: "
                                f"${price_drop:.2f}"
                            )
            except Exception as e:
                print(f"Error checking price drops for {booking.get('location', 'Unknown')}: {str(e)}")
                continue
        
        return significant_drops
    
    def send_alerts(self, bookings_data: List[Dict]) -> bool:
        """
        Process bookings and send alerts for all active bookings
        
        Returns:
            bool: True if alerts were sent successfully, False otherwise
        """
        try:
            # Filter out expired bookings
            active_bookings = self.filter_active_bookings(bookings_data)
            
            if not active_bookings:
                print("No active bookings to process")
                return True
            
            # Check for significant price drops but don't filter the bookings
            bookings_with_drops = self.check_price_drops(active_bookings)
            
            # Mark bookings that have significant drops
            for booking_data in active_bookings:
                booking = booking_data['booking']
                has_significant_drop = any(
                    drop['booking']['location'] == booking['location'] 
                    and drop['booking']['dropoff_date'] == booking['dropoff_date']
                    for drop in bookings_with_drops
                )
                booking_data['has_significant_drop'] = has_significant_drop
            
            # Send email with all active bookings
            print(f"Sending email update for {len(active_bookings)} bookings")
            if bookings_with_drops:
                print(f"Including {len(bookings_with_drops)} bookings with significant price drops")
            
            # Add summary data for email
            summary_data = {
                'total_bookings': len(active_bookings),
                'price_drops': len(bookings_with_drops),
                'locations': [b['booking']['location'] for b in active_bookings],
                'check_time': datetime.now().isoformat()
            }
            
            return send_price_alert(active_bookings, summary_data)
                
        except Exception as e:
            print(f"Error sending price alerts: {str(e)}")
            import traceback
            traceback.print_exc()
            return False