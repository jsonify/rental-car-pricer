const { useState, useEffect } = React;
const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } = Recharts;

const formatPrice = (price) => `$${parseFloat(price).toFixed(2)}`;

const StatCard = ({ title, value, subtitle, className }) => (
    <div className={\`bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow \${className}\`}>
        <div className="text-sm text-gray-500">{title}</div>
        <div className="text-2xl font-semibold mt-1">{value}</div>
        {subtitle && <div className="text-sm mt-1">{subtitle}</div>}
    </div>
);

const PriceDashboard = () => {
    const [priceData, setPriceData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPriceHistory = async () => {
            try {
                const response = await fetch('/price_history.json');
                if (!response.ok) throw new Error('Failed to load price history');
                const data = await response.json();
                setPriceData(data);
                setError(null);
            } catch (err) {
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

    // Transform bookings object into array
    const bookings = Object.entries(priceData.bookings || {}).map(([id, booking]) => ({
        id,
        ...booking
    }));

    const renderBookingCard = (booking) => {
        const priceHistory = booking.price_history || [];
        const latestRecord = priceHistory[priceHistory.length - 1] || {};
        const previousRecord = priceHistory[priceHistory.length - 2] || {};
        
        // Prepare data for chart
        const chartData = priceHistory.map(record => ({
            timestamp: record.timestamp,
            price: record.prices?.[booking.focus_category] || 0,
            holdingPrice: booking.holding_price
        }));

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
                        value={formatPrice(latestRecord.prices?.[booking.focus_category] || 0)}
                    />
                    <StatCard
                        title="Holding Price"
                        value={formatPrice(booking.holding_price || 0)}
                    />
                    <StatCard
                        title="Savings"
                        value={formatPrice(Math.max(0, (booking.holding_price || 0) - (latestRecord.prices?.[booking.focus_category] || 0)))}
                        subtitle="vs Holding Price"
                    />
                </div>

                <div className="h-[300px] mb-6">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="timestamp" />
                            <YAxis
                                domain={['auto', 'auto']}
                                tickFormatter={tick => `$${tick}`}
                            />
                            <Tooltip
                                formatter={(value) => [`$${value}`, 'Price']}
                                labelFormatter={(label) => `Time: ${label}`}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="price"
                                stroke="#2563eb"
                                activeDot={{ r: 8 }}
                                name="Price"
                            />
                            <Line
                                type="monotone"
                                dataKey="holdingPrice"
                                stroke="#dc2626"
                                strokeDasharray="5 5"
                                name="Holding Price"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
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

export default PriceDashboard;