# web_crawler.py
# Description: This file contains the selenium web crawler for the Piazza File Downloader.
# Author: Wenjin Li
# Date: 2023/07/03

import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Crawler():
    email = ''
    password = ''
    driver = None
    session = None

    def __init__(self):
        # Configure Chrome options for running in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Run in headless mode

        # Create the webdriver with the specified options
        # self.driver = webdriver.Chrome(options=chrome_options)
        self.driver = webdriver.Chrome()
        # open the login page
        url = 'https://piazza.com/account/login'
        self.driver.get(url)

    def log_in(self):
        try:
            # Wait for email and password fields to be present
            email_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'email_field')))
            password_field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'password_field')))
            
            # Enter email and password
            email_field.send_keys(self.email)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(1)

            try:
                # Check if login was successful and print error message if not
                error_element = self.driver.find_element(By.ID, 'modal_error_text')
                if error_element.is_displayed():
                    error_message = error_element.get_attribute('innerHTML').strip()
                    print(f'Login failed. Error message: {error_message}')
                    # self.driver.quit()
                    # exit(0)
                    return False
            except (TimeoutException,NoSuchElementException):
                pass

            # Wait for login to complete, assume the login is complete when the title contains "Piazza"
            WebDriverWait(self.driver, 10).until(EC.title_contains('Piazza'))

            # return True for successful login    
            return True
        
        except TimeoutException:
            print("Login process took too long. Please check your internet connection or try again later.")
            self.driver.quit()
            exit(0)

    def class_dropDown_menu(self):
        self.driver.find_element("id", 'classDropdownMenuId').click()
        time.sleep(1)
        self.driver.find_element("id", 'toggleInactiveNetworksId').click()
        time.sleep(1)
        my_classes = self.driver.find_element("id", 'my_classes')
        
        # save all the classes in a dictionary
        class_dict = {}
        class_elements = my_classes.find_elements(By.CSS_SELECTOR, "a[data-pats='classes_dropdown_item']")

        for i, class_element in enumerate(class_elements):
            # print(class_element.text,end="| ")
            # print(class_element.get_attribute("id"))
            # print(class_element.find_element(By.CLASS_NAME, "course_number").text)
            class_name = class_element.find_element(By.CLASS_NAME, "course_number").text
            class_url = class_element.get_attribute("id").replace('network_', 'https://piazza.com/class/')
            class_dict[i] = {
                'rank_id': i,
                "class_name": class_name,
                "url": class_url
            }

        # print(class_dict)
        return class_dict
    
    def download_files(self, target_url):
        # load the target url
        self.driver.get(target_url)
        self.driver.find_element("id", 'resources_link').click()
        
        # wait for the page to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'resourceLink_idx0_0')))
        
        # get the cookies from the browser
        cookies = self.driver.get_cookies()
        
        # create a session and set the cookies
        self.session = requests.Session()
        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
        
        # download the all the files
        # TODO: download the selected area file
        i = 0
        while True:
            try:
                element = self.driver.find_element("id", f'resourceLink_idx0_{i}')
                # element = driver.find_element("id", f'resourceLink_idx1_{i}')
                # element = driver.find_element("id", f'resourceLink_idx2_{i}')
                file_url = element.get_attribute('href')
                print(f"loading URL: {file_url}")

                file_name = element.text.strip()
                
                # check if the file still exists, if not, skip to the next file
                response = self.session.get(file_url)
                response_code = response.raise_for_status()
                if response_code != None:
                    print(f"Error code: {response_code}")
                    i += 1
                    continue

                # download the file and save it to the local folder "test_files", this file could be a pdf, ppt, docx, zip, etc.
                with open(f'./test_files/{file_name}', 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                print(f'Downloaded: {file_name}')
                i += 1
                
            except Exception:
                print("no more file!")
                break

if __name__ == "__main__":
    testing_crawler = Crawler()
    testing_crawler.email = 'enter your email here'
    testing_crawler.password = 'enter your password here'
    testing_crawler.log_in()
    testing_crawler.class_dropDown_menu()
    # testing_crawler.download_files()
