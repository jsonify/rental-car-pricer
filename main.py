#!/usr/bin/env python3

import argparse
import os
from booking_tracker import BookingTracker
from price_monitor import (
    setup_browser,
    enter_location,
    enter_date,
    set_times,
    check_age_checkbox,
    click_search,
    fill_search_form,
    wait_for_results,
    get_available_categories,
    validate_category,
    process_booking,
    run_price_checks,
)


def get_new_booking_info(page):
    """Get information for a new booking from user input."""
    from datetime import datetime, timedelta

    print("\n📝 Enter new booking information:")

    while True:
        location = input("\nEnter airport code (e.g., KOA): ").strip().upper()
        if len(location) == 3 and location.isalpha():
            break
        print("❌ Invalid airport code. Please enter a three-letter code.")

    while True:
        try:
            pickup_date = input("Enter pickup date (MM/DD/YYYY): ").strip()
            dropoff_date = input("Enter dropoff date (MM/DD/YYYY): ").strip()
            datetime.strptime(pickup_date, "%m/%d/%Y")
            datetime.strptime(dropoff_date, "%m/%d/%Y")
            break
        except ValueError:
            print("❌ Invalid date format. Please use MM/DD/YYYY format.")

    print(f"\nFetching available categories for {location}...")
    try:
        page.goto("https://www.costcotravel.com/Rental-Cars")
        page.wait_for_timeout(2000)

        if not fill_search_form(page, {
            "location": location,
            "pickup_date": pickup_date,
            "dropoff_date": dropoff_date,
            "pickup_time": "12:00 PM",
            "dropoff_time": "12:00 PM",
        }):
            raise Exception("Failed to fill search form")

        current_url = page.url
        click_search(page)
        if not wait_for_results(page, current_url):
            raise Exception("Failed to load results")

        available_categories = sorted(get_available_categories(page))
        if not available_categories:
            raise Exception("No categories found")

        print("\n📋 Available categories:")
        for i, cat in enumerate(available_categories, 1):
            print(f"{i}. {cat}")

        while True:
            try:
                cat_choice = int(input("\nSelect category number: ").strip())
                if 1 <= cat_choice <= len(available_categories):
                    focus_category = available_categories[cat_choice - 1]
                    break
                print(f"❌ Please enter a number between 1 and {len(available_categories)}")
            except ValueError:
                print("❌ Please enter a valid number")

    except Exception as e:
        print(f"❌ Error getting categories: {str(e)}")
        print("Using default category list...")
        default_categories = [
            "Economy Car", "Compact Car", "Intermediate Car", "Standard Car",
            "Full-size Car", "Premium Car", "Compact SUV", "Standard SUV",
            "Full-size SUV", "Premium SUV", "Minivan",
        ]
        print("\n📋 Default categories:")
        for i, cat in enumerate(default_categories, 1):
            print(f"{i}. {cat}")
        while True:
            try:
                cat_choice = int(input("\nSelect category number: ").strip())
                if 1 <= cat_choice <= len(default_categories):
                    focus_category = default_categories[cat_choice - 1]
                    break
                print(f"❌ Please enter a number between 1 and {len(default_categories)}")
            except ValueError:
                print("❌ Please enter a valid number")

    return {
        "location": location,
        "pickup_date": pickup_date,
        "dropoff_date": dropoff_date,
        "focus_category": focus_category,
        "pickup_time": "12:00 PM",
        "dropoff_time": "12:00 PM",
    }


def interactive_mode():
    """Run the price checker in interactive mode with user input."""
    print("\n🚗 Costco Travel Car Rental Price Tracker")
    print("=" * 50)

    tracker = BookingTracker()
    active_bookings = tracker.get_active_bookings()

    if not active_bookings:
        print("📢 No active bookings found.")
    else:
        print("\n📋 Current active bookings:")
        for i, booking in enumerate(active_bookings, 1):
            print(f"\n{i}. 📍 {booking['location']}")
            print(f"   📅 {booking['pickup_date']} - {booking['dropoff_date']}")
            print(f"   🎯 Focus: {booking['focus_category']}")

    print("\n🔄 Choose an action:")
    print("1. Track current bookings")
    print("2. Add a new booking")
    print("3. Delete a booking")
    print("4. Update holding prices")
    print("5. Exit")

    choice = input("\nChoice (default: 1): ").strip() or "1"

    if choice == "2":
        playwright, browser, context, page = setup_browser(headless=True)
        try:
            new_booking = get_new_booking_info(page)
            if validate_category(page, new_booking["focus_category"], new_booking["location"]):
                tracker.add_booking(**new_booking)
                print(f"\n✅ Added new booking: {new_booking['location']}")
                active_bookings = tracker.get_active_bookings()
            else:
                print("\n❌ Failed to add booking: Invalid category for location")
        finally:
            browser.close()
            playwright.stop()
    elif choice == "3":
        try:
            booking_id = tracker.get_booking_choice()
            if tracker.delete_booking(booking_id):
                print("\n✅ Booking deleted successfully")
        except ValueError as e:
            print(f"\n❌ Error: {str(e)}")
        return
    elif choice == "4":
        tracker.prompt_for_holding_prices()
        return
    elif choice == "5":
        print("\n👋 Goodbye!")
        return

    if active_bookings:
        run_price_checks(tracker, active_bookings)


def automated_mode():
    """Run the price checker in automated mode without user interaction."""
    import sys
    print("\n🤖 Running in automated mode")
    print("=" * 50)

    tracker = BookingTracker()
    active_bookings = tracker.get_active_bookings()

    if not active_bookings:
        print("📢 No active bookings found.")
        return

    print(f"📋 Found {len(active_bookings)} active bookings")
    success = run_price_checks(tracker, active_bookings)
    if not success:
        print("\n❌ Price check failed — no prices obtained for any booking")
        sys.exit(1)


def main():
    """Main function that handles command line arguments and execution mode."""
    try:
        parser = argparse.ArgumentParser(description="Costco Travel Car Rental Price Tracker")
        parser.add_argument("-i", "--interactive", action="store_true",
                            help="Run in interactive mode")
        args = parser.parse_args()

        is_ci = os.environ.get("CI") == "true"

        if args.interactive:
            print("\n🔄 Running in interactive mode...")
            interactive_mode()
        elif is_ci:
            print("\n🤖 Running in CI automated mode...")
            automated_mode()
        else:
            print("\n🤖 Running in automated mode...")
            print("Tip: Use -i or --interactive flag for interactive mode")
            automated_mode()

    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        import traceback
        print(f"\n❌ Unexpected error: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
