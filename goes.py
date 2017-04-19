#!/usr/bin/env python

import re
import urllib
from bs4 import BeautifulSoup
import requests
import codecs
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import getpass
import os
import shutil
import webkit_driver
import time
from twilio.rest import Client


goes_username = 'username'
goes_password = 'password'


def get_title(driver):
    return driver.find_element_by_xpath('/html/head/title').get_attribute('text').encode('utf-8')

def click_button(driver, element):
    ActionChains(driver).move_to_element(element).click().perform()

def check_title(driver, title):
    if re.search(title, get_title(driver)):
        return True
    else:
        return False
    

def run_scrape(driver):
    driver.get(start_url)
    old_page_id = 0
    # Global Online Enrollment System (GOES)-Official U.S.\nGovernment Web Site to apply for Global Entry, FLUX, NEXUS, SENTRI, FAST

    if check_title(driver, 'Global\sOnline\sEnrollment'):
        print "Loaded Login Page"
        old_page_id = driver.find_element_by_tag_name('html').id
        driver.find_element_by_id('j_username').send_keys(goes_username)
        driver.find_element_by_id('j_password').send_keys(goes_password)

        click_button(driver, driver.find_element_by_id('SignIn'))

    # Wait For page Load
    webkit_driver.wait_for_page_load(driver, old_page_id)

    # 'Security Notification'
    if check_title(driver, 'Security'):
        print "Loaded Security Page"
        old_page_id = driver.find_element_by_tag_name('html').id
        click_button(driver, driver.find_element_by_id('checkMe'))

    # Wait for Page Load
    webkit_driver.wait_for_page_load(driver, old_page_id)

    # Home
    if check_title(driver, 'Home'):
        print "Loaded Home Page"
        old_page_id = driver.find_element_by_tag_name('html').id
        click_button(driver, driver.find_element_by_name("manageAptm"))

    # Wait for Page Load
    webkit_driver.wait_for_page_load(driver, old_page_id)

    # Interview Scheduled
    if check_title(driver, 'Interview'):
        print "Loaded Interview Scheduled Page"
        old_page_id = driver.find_element_by_tag_name('html').id
        click_button(driver, driver.find_element_by_name("reschedule"))

    # Wait for Page Load
    webkit_driver.wait_for_page_load(driver, old_page_id)

    # Select Enrollment Center
    if check_title(driver, 'Select'):
        print "Loaded Enrollement Centers, Picking SFO"
        old_page_id = driver.find_element_by_tag_name('html').id
        click_button(driver, driver.find_element_by_xpath("//input[@value=5446]"))

        # Wait For Next Button
        time.sleep(2)
        click_button(driver, driver.find_element_by_name("next"))

    # Wait for page Load
    webkit_driver.wait_for_page_load(driver, old_page_id)

    # Internet Schedule Calendar
    dates = []
    if check_title(driver, "Calendar"):
        print "Loaded Calendar"
        old_page_id = driver.find_element_by_tag_name('html').id
        entries = driver.find_elements_by_xpath("//*[@class='entry']")
        dates = [re.search('(201\d+)', entry.get_attribute('onClick')).group(1) for entry in entries]


    return dates


def run(driver):
    print "Running Scrape"
    dates = run_scrape(driver)

    # number to send SMS to
    toNumber = "+15105550006"

    #twilio tokens
    twilioAccount = "xxx"
    twilioToken = "yyy"
    fromNumber = "+15105550006"

    #201711012230
    mos = [re.search('(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', d) for d in dates]

    cnt = 0;
    for m in mos:
        year = m.group(1)
        month = m.group(2)
        day = m.group(3)
        hour = m.group(4)
        minute = m.group(5)

        msg = "%s/%s/%s at %s:%s" % (month, day, year, hour, minute)
        print "Found Dates %s" % (msg)

        if (month == '04' or month == '05') and cnt == 0:
            print "Sending Email"
            client = Client(twilioAccount,twilioToken)

            res = client.messages.create(to=toNumber, from_=fromNumber, 
                    body=msg)
        cnt+=1



if __name__ == '__main__':
        
    print("load driver")
    driver = webkit_driver.init_webdriver()
    print("loaded "+str(driver))

    start_url = 'https://goes-app.cbp.dhs.gov/goes/jsp/login.jsp'
    start_url = 'https://goes-app.cbp.dhs.gov/goes/index.jsp'


    while True:
        try:
            print("calling run")
            run(driver)
        except selenium.common.exceptions.WebDriverException:
            print "Driver Crashed"
            driver.quit()
            driver = webkit_driver.init_webdriver()
        print "Sleeping for 5 minutes"
        try:
            time.sleep(300)
        except KeyboardInterrupt:
            break

    


