from selenium import webdriver
import time

def wait_for_page_load(driver, old_page_id):
    start_time = time.time()
    while time.time() < start_time + 5:
        new_page = driver.find_element_by_tag_name('html')
        if new_page.id != old_page_id:
            time.sleep(0.2)
            return True
        else:
            time.sleep(0.01)
    #raise Exception('Timeout waiting for Page Load')
    print 'Timeout waiting for Page Load'


def init_webdriver():
    driver = webdriver.Chrome()
    return driver

