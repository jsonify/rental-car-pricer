# email_module/charts.py

"""
Chart generator for price history visualization.
Handles Supabase JSON price data and creates simple, reliable price trend charts.
"""

import io
import base64
import logging
import json
from typing import List, Dict
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_focus_category_price(prices_json: str, focus_category: str) -> float:
    """Extract price for focus category from JSON string"""
    try:
        prices = json.loads(prices_json)
        return float(prices.get(focus_category, 0))
    except Exception as e:
        logger.error(f"Error extracting price: {str(e)}")
        return 0

def generate_price_trend_chart(price_records: List[Dict], 
                             holding_price_histories: List[Dict],
                             focus_category: str) -> str:
    """
    Generate a price trend chart as base64-encoded PNG
    
    Args:
        price_records: List of price history records from Supabase
        holding_price_histories: List of holding price records from Supabase
        focus_category: Category to track (e.g., "Full-size Car")
    """
    try:
        logger.debug(f"Generating chart for {focus_category}")
        logger.debug(f"Number of price records: {len(price_records)}")
        logger.debug(f"Number of holding records: {len(holding_price_histories)}")

        # Sort records by timestamp
        sorted_prices = sorted(price_records, key=lambda x: datetime.fromisoformat(x['timestamp']))
        sorted_holdings = sorted(holding_price_histories, 
                               key=lambda x: datetime.fromisoformat(x['effective_from']))

        # Extract data points
        dates = [datetime.fromisoformat(record['timestamp']) for record in sorted_prices]
        prices = [extract_focus_category_price(record['prices'], focus_category) 
                 for record in sorted_prices]

        # Create the figure with larger size for better visibility
        plt.figure(figsize=(8, 4))

        # Plot actual prices
        plt.plot(dates, prices, 'b-', linewidth=2, label='Current Price')
        logger.debug(f"Plotted {len(dates)} price points")

        # Plot holding prices
        if holding_price_histories:
            holding_dates = []
            holding_values = []
            
            for record in sorted_holdings:
                holding_dates.append(datetime.fromisoformat(record['effective_from']))
                holding_values.append(float(record['price']))

            plt.plot(holding_dates, holding_values, 'r--', linewidth=1.5, 
                    label='Holding Price', alpha=0.7)
            logger.debug(f"Plotted {len(holding_dates)} holding price points")

        # Customize appearance
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Format x-axis to show dates nicely
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        plt.xticks(rotation=45)
        
        # Format y-axis to show dollars
        plt.gca().yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: f'${int(x):,}'))

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        logger.debug("Chart generated and saved to buffer")

        # Encode as base64
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode()
        return f'data:image/png;base64,{image_base64}'

    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        return ""