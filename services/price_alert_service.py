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
                    expired_bookings.append(booking['location'])
            except (KeyError, ValueError) as e:
                print(f"Error processing booking: {str(e)}")
                continue
        
        if expired_bookings:
            print(f"Skipping expired bookings: {', '.join(expired_bookings)}")
        
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
                current_price = prices.get(booking['focus_category'])
                holding_price = booking.get('holding_price')
                
                if current_price is not None and holding_price is not None:
                    price_drop = holding_price - current_price
                    if price_drop >= self.price_threshold:
                        significant_drops.append(booking_data)
                        logging.info(
                            f"Significant price drop found for {booking.get('location')}: "
                            f"${price_drop:.2f} below holding price"
                        )
            except Exception as e:
                logging.error(f"Error checking price drops: {str(e)}")
                continue
        
        return significant_drops
    
    def send_alerts(self, bookings_data: List[Dict]) -> bool:
        """
        Process bookings and send alerts if significant price drops are found
        
        Returns:
            bool: True if alerts were sent successfully, False otherwise
        """
        try:
            # Filter out expired bookings
            active_bookings = self.filter_active_bookings(bookings_data)
            
            if not active_bookings:
                logging.info("No active bookings to process")
                return True
            
            # Check for significant price drops
            bookings_with_drops = self.check_price_drops(active_bookings)
            
            if bookings_with_drops:
                logging.info(f"Sending alerts for {len(bookings_with_drops)} price drops")
                return send_price_alert(bookings_with_drops)
            else:
                logging.info("No significant price drops found")
                return True
                
        except Exception as e:
            logging.error(f"Error sending price alerts: {str(e)}")
            return False