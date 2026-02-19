# price_extractor.py

from datetime import datetime
from config import PRICES_FILE, PICKUP_LOCATION, PICKUP_DATE, DROPOFF_DATE


def extract_lowest_prices(page):
    """Extract lowest prices for each car category from the Costco Travel results page.

    Args:
        page: A Playwright Page object on the results page.

    Returns:
        dict: {category_name: float_price} for each category found.
    """
    print("\nExtracting lowest prices...")
    lowest_prices = {}

    category_rows = page.locator('div[role="row"]').all()

    for row in category_rows:
        try:
            category_name = row.locator(
                "div.inner.text-center.h3-tag-style"
            ).text_content()
            if not category_name:
                continue
            category_name = category_name.strip()

            price_str = row.locator(
                "a.card.car-result-card.lowest-price"
            ).get_attribute("data-price")

            lowest_prices[category_name] = float(price_str)
            print(f"Found {category_name}: ${price_str}")

        except Exception:
            continue

    save_prices_to_file(lowest_prices)
    return lowest_prices


def save_prices_to_file(prices):
    """Save prices to file with timestamp, location, and dates."""
    if not prices:
        return

    with open(PRICES_FILE, "a") as f:
        f.write(f"\n{'=' * 50}")
        f.write(f"\nPrices as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        f.write(f"\nLocation: {PICKUP_LOCATION}")
        f.write(f"\nDates: {PICKUP_DATE} - {DROPOFF_DATE}")
        f.write(f"\n{'-' * 50}\n")

        max_length = max(len(c) for c in prices)
        for category, price in prices.items():
            f.write(f"{category:<{max_length}}: ${price:>8.2f}\n")

        f.write(f"{'=' * 50}\n")

    print(f"Prices saved to {PRICES_FILE}")
