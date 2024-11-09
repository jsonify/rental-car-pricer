# human_simulation.py

import random
import time
from selenium.webdriver.common.keys import Keys

def human_like_typing(element, text):
    """Simulate human-like typing with random delays"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def random_mouse_movement(driver):
    """Simulate random mouse movements"""
    driver.execute_script("""
        var event = new MouseEvent('mousemove', {
            'view': window,
            'bubbles': true,
            'cancelable': true,
            'clientX': arguments[0],
            'clientY': arguments[1]
        });
        document.dispatchEvent(event);
    """, random.randint(100, 700), random.randint(100, 500))

def enter_date(driver, field_id, date_value):
    """Enhanced date entry function with human-like behavior"""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    date_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, field_id))
    )
    
    date_field.click()
    time.sleep(random.uniform(0.3, 0.7))
    
    driver.execute_script("arguments[0].value = '';", date_field)
    date_field.clear()
    time.sleep(random.uniform(0.3, 0.7))
    
    driver.execute_script(f"arguments[0].value = '{date_value}';", date_field)
    
    date_field.click()
    human_like_typing(date_field, date_value)
    date_field.send_keys(Keys.TAB)
    
    time.sleep(random.uniform(1, 1.5))
    
    entered_value = driver.execute_script("return arguments[0].value;", date_field)
    print(f"Entered date for {field_id}: {entered_value}")
    
    return entered_value == date_value