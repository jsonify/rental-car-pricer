"""
Example: How your Costco Travel scraper would look with Playwright
This is a side-by-side comparison to help you decide

Installation:
pip install playwright
playwright install chromium
"""

from playwright.sync_api import sync_playwright
import random
import time

def scrape_with_playwright():
    with sync_playwright() as p:
        # Launch browser (automatically downloads/manages Chromium)
        browser = p.chromium.launch(
            headless=True,  # or False for debugging
            args=[
                '--disable-blink-features=AutomationControlled',
                '--window-size=1920,1080'
            ]
        )

        # Create context (like a private browsing session)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        # Remove webdriver property (better stealth)
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)

        page = context.new_page()

        # Navigate
        page.goto('https://www.costcotravel.com/Rental-Cars')

        # Fill location (with human-like typing)
        location_input = page.locator('#pickupLocationTextWidget')
        location_input.click()

        # Human-like typing (built-in!)
        location_input.type('KOA', delay=random.randint(100, 300))

        # Wait and click dropdown
        page.wait_for_selector('//li[contains(text(), "KOA")]', timeout=10000)
        page.click('//li[contains(text(), "KOA")]')

        # Fill dates (Playwright has better date handling)
        page.fill('#pickUpDateWidget', '04/03/2025')
        page.fill('#dropOffDateWidget', '04/10/2025')

        # Select times
        page.select_option('#pickupTimeWidget', '12:00 PM')
        page.select_option('#dropoffTimeWidget', '12:00 PM')

        # Check age checkbox (no more execute_script!)
        if not page.is_checked('#driversAgeWidget'):
            page.check('#driversAgeWidget')

        # Click search and wait for navigation
        page.click('#findMyCarButton')
        page.wait_for_url('**/results**', timeout=60000)

        # Extract prices (cleaner selectors)
        prices = {}
        category_rows = page.locator('div[role="row"]').all()

        for row in category_rows:
            try:
                category = row.locator('div.inner.text-center.h3-tag-style').inner_text()
                price_element = row.locator('a.card.car-result-card.lowest-price')
                price = float(price_element.get_attribute('data-price'))
                prices[category] = price
                print(f"{category}: ${price}")
            except:
                continue

        # Screenshot (built-in, better quality)
        page.screenshot(path='screenshots/results.png', full_page=True)

        browser.close()
        return prices

# Async version (faster for multiple bookings)
async def scrape_with_playwright_async():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto('https://www.costcotravel.com/Rental-Cars')
        # ... rest of the code with await

        await browser.close()

if __name__ == '__main__':
    prices = scrape_with_playwright()
    print(f"\nFound {len(prices)} categories")
