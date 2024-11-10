# email_module/styles/css_styles.py
EMAIL_CSS = '''
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1d1d1f;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background: #f5f5f7;
}

.header {
    text-align: center;
    padding: 40px 20px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    margin-bottom: 30px;
}

.header h1 {
    font-size: 32px;
    font-weight: 700;
    background: linear-gradient(120deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.metadata {
    color: #6b7280;
    font-size: 14px;
}

.booking-card {
    background: white;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 30px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.location-header {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #f3f4f6;
}

.location-name {
    font-size: 24px;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 8px;
}

.dates {
    display: inline-block;
    background: #f3f4f6;
    padding: 8px 16px;
    border-radius: 20px;
    color: #4b5563;
    font-size: 14px;
    margin-top: 10px;
}

.focus-category {
    background: #f8fafc;
    border-radius: 16px;
    padding: 24px;
    margin: 30px 0;
    border: 2px solid #e2e8f0;
}

.focus-label {
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}

.focus-name {
    font-size: 20px;
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 16px;
}

.price {
    font-size: 36px;
    font-weight: 700;
    color: #1d1d1f;
    font-feature-settings: "tnum";
}

.change {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
    margin-left: 12px;
}

.increase {
    background: #fee2e2;
    color: #dc2626;
}

.decrease {
    background: #dcfce7;
    color: #16a34a;
}

.holding-compare {
    display: block;
    margin-top: 12px;
    padding: 8px 16px;
    border-radius: 12px;
    font-size: 14px;
    font-weight: 500;
}

.above {
    background: #fff7ed;
    color: #c2410c;
}

.below {
    background: #ecfdf5;
    color: #059669;
}

.price-list {
    margin-top: 30px;
    background: #f8fafc;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid #e2e8f0;
}

.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 2px solid #e2e8f0;
    transition: background-color 0.2s ease;
}

.price-row:last-child {
    border-bottom: none;
}

.price-row:hover {
    background-color: #f1f5f9;
}

.category-name {
    font-weight: 500;
    color: #1e293b;
}

.focus-row {
    background: #e0f2fe;
}

.better-deals {
    background: #f0f9ff;
    border-radius: 16px;
    padding: 24px;
    margin: 30px 0;
    border: 2px solid #bae6fd;
}

.better-deals-header {
    color: #0369a1;
    font-weight: 600;
    font-size: 18px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.deal-option {
    background: white;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
    color: #0c4a6e;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.price-stats {
    display: flex;
    gap: 16px;
    margin-top: 16px;
}

.stat-box {
    flex: 1;
    background: white;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
}

.stat-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
    margin-bottom: 8px;
}

.stat-value {
    font-size: 20px;
    font-weight: 600;
    color: #0f172a;
}

.footer {
    text-align: center;
    color: #6b7280;
    font-size: 12px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 2px solid #e5e7eb;
}
# Add to EMAIL_CSS
.booking-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 30px;
    margin: 30px 0;
}

@media (min-width: 768px) {
    .booking-grid {
        grid-template-columns: 1fr 1fr;
    }
}
'''