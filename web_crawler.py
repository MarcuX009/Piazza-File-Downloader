# web_crawler.py
# Description: This file contains the selenium web crawler for the Piazza File Downloader.
# Author: Wenjin Li
# Date: 2023/07/03

import requests
import os
from time import sleep
import mimetypes
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
    class_dict = {} # save all the classes in a dictionary
    session_dict = {} # save all the sessions in a dictionary

    def __init__(self):
        # Configure Chrome options for running in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Run in headless mode

        # Create the webdriver with the specified options
        self.driver = webdriver.Chrome(options=chrome_options)
        # self.driver = webdriver.Chrome()
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
            sleep(1)

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
            return False # sometime piazza will ask for verification your student status, so you need to manually log in

    def get_class_dropDown_menu(self):
        self.driver.find_element("id", 'classDropdownMenuId').click()
        sleep(1)
        self.driver.find_element("id", 'toggleInactiveNetworksId').click()
        sleep(1)
        my_classes = self.driver.find_element("id", 'my_classes')
        
        
        class_elements = my_classes.find_elements(By.CSS_SELECTOR, "a[data-pats='classes_dropdown_item']")

        for i, class_element in enumerate(class_elements):
            # print(class_element.text,end=" | ")
            # print(class_element.get_attribute("id"))
            # print(class_element.find_element(By.CLASS_NAME, "course_number").text)
            class_name = class_element.find_element(By.CLASS_NAME, "course_number").text
            class_url = class_element.get_attribute("id").replace('network_', 'https://piazza.com/class/')
            self.class_dict[i] = {
                'rank_id': i,
                "class_name": class_name,
                "url": class_url
            }

    
    def get_resource_dropDown_menu(self, class_index):
        # go to the target url and click the resource link
        self.driver.get(self.class_dict[class_index]['url'])
        self.driver.find_element("id", 'resources_link').click()

        # wait for the page to load
        sleep(1)
        # find the resources element and save all the sessions in a dictionary
        resources_element = self.driver.find_element(By.ID, "resources")
        i = 0
        while True:
            try:
                session_element = resources_element.find_element(By.ID, f"section_name_idx{i}").text
                # print(session_element) # print the session name # for testing
                self.session_dict[i] = {
                    'rank_id': i,
                    "session_name": session_element,
                }
                i += 1
            except NoSuchElementException:
                break

    def download_files(self, class_index, session_index):
        # find the class name
        class_name = self.class_dict[class_index]['class_name']

        # find the session name
        session_name = self.session_dict[session_index]['session_name']

        # create a folder for the class
        folder_path = f'./{class_name}/{session_name}'
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # get the cookies from the browser
        cookies = self.driver.get_cookies()
        
        # create a session and set the cookies
        self.session = requests.Session()
        for cookie in cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
        
        number_of_file = 0
        while True:
            try:
                element = self.driver.find_element("id", f'resourceLink_idx{session_index}_{number_of_file}')
                file_url = element.get_attribute('href')
                print(f"loading URL: {file_url}")

                file_name = element.text.strip()
                print(f"file name: {file_name}")
                # check if the file still exists, if not, skip to the next file
                response = self.session.get(file_url)
                response_code = response.raise_for_status()
                if response_code != None:
                    print(f"Error code: {response_code}")
                    number_of_file += 1
                    continue
                
                # Determine the file extension # TODO: if it's a google doc, show the warning and prompt the user to download it manually
                file_extension = mimetypes.guess_extension(response.headers.get('Content-Type'))
                print(f"file extension: {file_extension}")
                if not file_extension:
                    # If the file extension is missing, assume it is a PDF
                    file_extension = '.pdf'

                # Remove the file extension from the file name if it already exists
                if file_name.endswith(file_extension):
                    file_name = file_name[:-(len(file_extension))]

                # Construct the file path with the determined extension
                file_path = os.path.join(folder_path, f'{file_name}{file_extension}')

                # download the file and save it to the local folder "test_files", this file could be a pdf, ppt, docx, zip, etc.
                # with open(f'./test_files/{file_name}', 'wb') as file:
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)

                print(f'Downloaded: {file_name}')
                number_of_file += 1
                
            except Exception:
                print("no more file!")
                break
        
        return number_of_file

if __name__ == "__main__":
    pass
    # testing_crawler = Crawler()
    # testing_crawler.email = 'enter your email here'
    # testing_crawler.password = 'enter your password here'
    # testing_crawler.log_in()
    # testing_crawler.get_class_dropDown_menu()
    # testing_crawler.get_resource_dropDown_menu()
    # testing_crawler.download_files()
