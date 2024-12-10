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
        
        for booking_data in bookings_data:
            try:
                booking = booking_data['booking']
                dropoff_date = datetime.strptime(booking['dropoff_date'], "%m/%d/%Y").date()
                
                if dropoff_date >= current_date:
                    active_bookings.append(booking_data)
                else:
                    print(f"Skipping expired booking: {booking.get('location')} - {booking['dropoff_date']}")
            except (KeyError, ValueError) as e:
                print(f"Error processing booking: {str(e)}")
                continue
        
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
                trends = booking_data.get('trends', {})
                focus_trends = trends.get('focus_category', {})
                
                current_price = focus_trends.get('current')
                previous_price = focus_trends.get('previous_price')
                
                if current_price is not None and previous_price is not None:
                    price_drop = previous_price - current_price
                    if price_drop >= self.price_threshold:
                        significant_drops.append(booking_data)
                        print(
                            f"Significant price drop found for {booking.get('location')}: "
                            f"${price_drop:.2f}"
                        )
            except Exception as e:
                print(f"Error checking price drops: {str(e)}")
                continue
        
        return significant_drops
    
    def send_alerts(self, bookings_data: List[Dict]) -> bool:
        """
        Process bookings and send alerts if significant price drops are found
        
        Returns:
            bool: True if alerts were sent successfully or no alerts needed, False if error
        """
        try:
            if not bookings_data:
                print("No bookings data to process")
                return True
            
            # Filter out expired bookings
            active_bookings = self.filter_active_bookings(bookings_data)
            
            if not active_bookings:
                print("No active bookings to process")
                return True
            
            # Check for significant price drops
            bookings_with_drops = self.check_price_drops(active_bookings)
            
            if not bookings_with_drops:
                print("No significant price drops found")
                return True
            
            # Send email alert
            alert_sent = send_price_alert(bookings_with_drops)
            return alert_sent
                
        except Exception as e:
            print(f"Error sending price alerts: {str(e)}")
            return False