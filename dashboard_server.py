from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os
import json
from datetime import datetime

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Add CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        
        if self.path == '/price_history.json':
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            try:
                with open('price_history.json', 'r') as f:
                    self.wfile.write(json.dumps(json.load(f)).encode())
            except Exception as e:
                self.wfile.write(json.dumps({
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }).encode())
        else:
            # Serve the requested file
            if self.path == '/':
                self.path = '/dashboard.html'
            return super().do_GET()

def write_dashboard_files():
    """Write the necessary dashboard files"""
    
    # Write the HTML file
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Car Rental Price Monitor</title>
    <!-- Load React -->
    <script src="https://unpkg.com/react@17/umd/react.development.js" crossorigin></script>
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js" crossorigin></script>
    <!-- Load Chart.js instead of Recharts -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Load Babel -->
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <!-- Load Tailwind -->
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        // Format price helper
        const formatPrice = (price) => `$${parseFloat(price).toFixed(2)}`;

        // Stat Card Component
        const StatCard = ({ title, value, subtitle, className }) => (
            <div className={`bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow ${className}`}>
                <div className="text-sm text-gray-500">{title}</div>
                <div className="text-2xl font-semibold mt-1">{value}</div>
                {subtitle && <div className="text-sm mt-1">{subtitle}</div>}
            </div>
        );

        // Price Chart Component
        const PriceChart = ({ data, focusCategory }) => {
            const canvasRef = React.useRef(null);
            const chartRef = React.useRef(null);

            React.useEffect(() => {
                if (!data || !canvasRef.current) return;

                // Destroy existing chart if it exists
                if (chartRef.current) {
                    chartRef.current.destroy();
                }

                const ctx = canvasRef.current.getContext('2d');
                const timestamps = data.map(record => record.timestamp);
                const prices = data.map(record => record.prices?.[focusCategory] || 0);

                chartRef.current = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: timestamps,
                        datasets: [{
                            label: 'Price',
                            data: prices,
                            borderColor: '#2563eb',
                            backgroundColor: '#2563eb20',
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return `$${context.raw.toFixed(2)}`;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                ticks: {
                                    callback: function(value) {
                                        return '$' + value.toFixed(0);
                                    }
                                }
                            }
                        }
                    }
                });

                return () => {
                    if (chartRef.current) {
                        chartRef.current.destroy();
                    }
                };
            }, [data, focusCategory]);

            return (
                <div className="h-[300px] relative">
                    <canvas ref={canvasRef}></canvas>
                </div>
            );
        };

        // Main Dashboard Component
        const PriceDashboard = () => {
            const [priceData, setPriceData] = React.useState(null);
            const [error, setError] = React.useState(null);
            const [loading, setLoading] = React.useState(true);

            React.useEffect(() => {
                const fetchPriceHistory = async () => {
                    try {
                        const response = await fetch('/price_history.json');
                        if (!response.ok) throw new Error('Failed to load price history');
                        const data = await response.json();
                        console.log('Fetched data:', data);
                        setPriceData(data);
                        setError(null);
                    } catch (err) {
                        console.error('Error fetching data:', err);
                        setError(err.message);
                    } finally {
                        setLoading(false);
                    }
                };

                fetchPriceHistory();
                const interval = setInterval(fetchPriceHistory, 30000);
                return () => clearInterval(interval);
            }, []);

            if (loading) {
                return (
                    <div className="min-h-screen bg-gray-50 p-8">
                        <div className="text-center text-gray-600">Loading price data...</div>
                    </div>
                );
            }

            if (error) {
                return (
                    <div className="min-h-screen bg-gray-50 p-8">
                        <div className="text-center text-red-600">Error: {error}</div>
                    </div>
                );
            }

            const bookings = Object.entries(priceData?.bookings || {}).map(([id, booking]) => ({
                id,
                ...booking
            }));

            const renderBookingCard = (booking) => {
                const priceHistory = booking.price_history || [];
                const latestRecord = priceHistory[priceHistory.length - 1] || {};
                const previousRecord = priceHistory[priceHistory.length - 2] || {};
                
                const currentPrice = latestRecord.prices?.[booking.focus_category] || 0;
                const previousPrice = previousRecord.prices?.[booking.focus_category] || 0;
                const priceChange = currentPrice - previousPrice;
                const percentChange = previousPrice ? (priceChange / previousPrice) * 100 : 0;

                return (
                    <div key={booking.id} className="bg-white rounded-xl shadow-md p-6 mb-6">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <h2 className="text-xl font-bold">{booking.location_full_name}</h2>
                                <p className="text-gray-500">
                                    {booking.pickup_date} - {booking.dropoff_date}
                                </p>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-gray-500">Focus Category</p>
                                <p className="font-semibold">{booking.focus_category}</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                            <StatCard
                                title="Current Price"
                                value={formatPrice(currentPrice)}
                                subtitle={priceChange !== 0 ? `${priceChange > 0 ? '↑' : '↓'} ${formatPrice(Math.abs(priceChange))} (${percentChange.toFixed(1)}%)` : 'No change'}
                                className={priceChange > 0 ? 'text-red-600' : priceChange < 0 ? 'text-green-600' : ''}
                            />
                            <StatCard
                                title="Holding Price"
                                value={formatPrice(booking.holding_price || 0)}
                            />
                            <StatCard
                                title="Potential Savings"
                                value={formatPrice(Math.max(0, (booking.holding_price || 0) - currentPrice))}
                                subtitle="vs Holding Price"
                                className="text-green-600"
                            />
                        </div>

                        <PriceChart data={priceHistory} focusCategory={booking.focus_category} />
                    </div>
                );
            };

            return (
                <div className="min-h-screen bg-gray-50 p-8">
                    <div className="max-w-7xl mx-auto">
                        <div className="flex justify-between items-center mb-8">
                            <h1 className="text-2xl font-bold">Car Rental Price Monitor</h1>
                            <p className="text-gray-500">
                                Last updated: {new Date(priceData.metadata?.last_updated).toLocaleString()}
                            </p>
                        </div>
                        <div className="space-y-6">
                            {bookings.map(renderBookingCard)}
                        </div>
                    </div>
                </div>
            );
        };

        // Render the app
        ReactDOM.render(
            <PriceDashboard />,
            document.getElementById('root')
        );
    </script>
</body>
</html>"""

    # Write the HTML file
    with open('dashboard.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Dashboard files created successfully")

def start_dashboard():
    """Start the dashboard server and open in browser"""
    # Ensure price history exists
    if not os.path.exists('price_history.json'):
        print("❌ price_history.json not found. Please run main.py first.")
        return

    # Write dashboard files
    write_dashboard_files()

    # Start the server
    port = 8000
    server = HTTPServer(('localhost', port), DashboardHandler)
    print(f"\n✨ Starting dashboard server on http://localhost:{port}")
    print("📊 Opening dashboard in your default browser...")
    
    # Open browser
    webbrowser.open(f'http://localhost:{port}/dashboard.html')
    
    try:
        print("\n🔄 Server is running. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        server.server_close()

if __name__ == '__main__':
    start_dashboard()