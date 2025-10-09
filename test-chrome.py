#!/usr/bin/env python3
"""
Quick test script to verify Chrome + ChromeDriver setup
Run: python3 test-chrome.py
"""

from driver_setup import setup_driver

def test_chrome_setup():
    """Test that Chrome and ChromeDriver are working correctly"""
    print('🔍 Testing Chrome + ChromeDriver setup...')

    try:
        # Launch Chrome
        driver = setup_driver(headless=True)
        print('✅ Chrome launched successfully')

        # Navigate to Google
        driver.get('https://www.google.com')
        print(f'✅ Navigated to Google')
        print(f'✅ Page title: {driver.title}')

        # Clean up
        driver.quit()
        print('🎉 All tests passed! Chrome and ChromeDriver are working correctly.')
        return True

    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_chrome_setup()
    exit(0 if success else 1)
