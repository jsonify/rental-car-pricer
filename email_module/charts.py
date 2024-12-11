# email_module/charts.py

"""
Chart generation module for email visualizations.
Uses Plotly for better compatibility in headless environments.
"""

import io
import base64
from typing import List, Dict
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def generate_price_trend_chart(price_history: List[Dict], 
                             holding_price_histories: List[Dict] = None,
                             width: int = 300,
                             height: int = 100) -> str:
    """
    Generate a price trend chart as a base64-encoded PNG image using Plotly
    
    Args:
        price_history: List of price records with timestamp and price
        holding_price_histories: Optional list of holding price records
        width: Chart width in pixels
        height: Chart height in pixels
    
    Returns:
        Base64-encoded PNG image string for email embedding
    """
    try:
        # Create figure
        fig = go.Figure()
        
        # Parse dates and prices
        dates = [datetime.fromisoformat(record['timestamp']) for record in price_history]
        prices = [float(record['price']) for record in price_history]
        
        # Add actual prices line
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines',
            name='Current Price',
            line=dict(color='#2563eb', width=2)
        ))
        
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
            
            # Add final point
            if current_price is not None:
                holding_dates.append(dates[-1])
                holding_prices.append(current_price)
            
            # Add holding prices line
            if holding_dates:
                fig.add_trace(go.Scatter(
                    x=holding_dates,
                    y=holding_prices,
                    mode='lines',
                    name='Holding Price',
                    line=dict(color='#dc2626', width=1.5, dash='dash')
                ))
        
        # Update layout
        fig.update_layout(
            width=width,
            height=height,
            margin=dict(l=40, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickformat='%m/%d'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.1)',
                tickprefix='$',
                tickformat=',.0f'
            )
        )
        
        # Convert to PNG
        img_bytes = fig.to_image(format="png", engine="kaleido")
        
        # Encode as base64
        image_base64 = base64.b64encode(img_bytes).decode()
        
        return f'data:image/png;base64,{image_base64}'
        
    except Exception as e:
        print(f"Error generating price trend chart: {str(e)}")
        return ""