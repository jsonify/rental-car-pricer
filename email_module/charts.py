# email_module/charts.py

"""
Chart generation module for email visualizations.
Handles creating, saving, and encoding price trend charts for email embedding.
"""

import io
import base64
from typing import List, Dict
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_price_trend_chart(price_history: List[Dict], 
                             holding_price_histories: List[Dict] = None,
                             width: int = 300,
                             height: int = 100) -> str:
    """
    Generate a price trend chart as a base64-encoded PNG image
    
    Args:
        price_history: List of price records with timestamp and price
        holding_price_histories: Optional list of holding price records
        width: Chart width in pixels
        height: Chart height in pixels
    
    Returns:
        Base64-encoded PNG image string for email embedding
    """
    try:
        # Convert figure size from pixels to inches (assuming 100dpi)
        fig_width = width / 100
        fig_height = height / 100
        
        # Create figure with appropriate size
        plt.figure(figsize=(fig_width, fig_height), dpi=100)
        
        # Parse dates and prices
        dates = [datetime.fromisoformat(record['timestamp']) for record in price_history]
        prices = [float(record['price']) for record in price_history]
        
        # Plot actual prices
        plt.plot(dates, prices, color='#2563eb', linewidth=2, label='Current Price')
        
        # Add holding prices if available
        if holding_price_histories:
            holding_dates = []
            holding_prices = []
            
            # Sort holding price history by date
            sorted_holdings = sorted(holding_price_histories, 
                                  key=lambda x: datetime.fromisoformat(x['effective_from']))
            
            # Create points for the holding price line
            current_price = None
            for holding in sorted_holdings:
                holding_date = datetime.fromisoformat(holding['effective_from'])
                if holding_date <= dates[0]:  # Before our price history
                    current_price = holding['price']
                    continue
                    
                if current_price is not None:
                    holding_dates.append(holding_date)
                    holding_prices.append(current_price)
                    
                current_price = holding['price']
                holding_dates.append(holding_date)
                holding_prices.append(current_price)
            
            # Add final point at the end of our date range
            if current_price is not None:
                holding_dates.append(dates[-1])
                holding_prices.append(current_price)
            
            # Plot holding prices
            if holding_dates:
                plt.plot(holding_dates, holding_prices, color='#dc2626', 
                        linestyle='--', linewidth=1.5, alpha=0.6,
                        label='Holding Price')
        
        # Customize appearance
        plt.grid(True, alpha=0.2)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        
        # Format y-axis to show dollars
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', 
                   pad_inches=0.1, transparent=True)
        plt.close()
        
        # Encode as base64
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode()
        
        return f'data:image/png;base64,{image_base64}'
        
    except Exception as e:
        print(f"Error generating price trend chart: {str(e)}")
        return ""