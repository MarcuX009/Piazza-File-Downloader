# GUI.py
# Description: This file contains the GUI for the Piazza File Downloader.
# Author: Wenjin Li
# Date: 2023/07/03

import os
import sys
from subprocess import Popen
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QMetaObject, pyqtSlot
from threading import Thread

import web_crawler

class MainWindow(QWidget):
    crawler = web_crawler.Crawler()
    log_in_status = False
   
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piazza File Downloader")
        self.setFixedHeight(360)
        self.setFixedWidth(800)

        # Create input fields and button
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.log_in_button = QPushButton("Log in")
        self.log_in_button.clicked.connect(self.log_in)
        
        self.start_download_button = QPushButton("Start Download")
        self.start_download_button.clicked.connect(self.start_download)
        self.start_download_button.setEnabled(False)  # Disable the button initially
        
        # create drop down menu
        self.drop_down_menu_for_class = QComboBox()
        self.drop_down_menu_for_resource = QComboBox()
        # Disable the drop-down menu initially
        self.drop_down_menu_for_class.setEnabled(False)
        self.drop_down_menu_for_resource.setEnabled(False)

        # Create status console
        self.status_console = QTextEdit()
        self.status_console.setReadOnly(True)

        # Create open folder button
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        
        # Create layout and add widgets
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel("Email:"), alignment=Qt.AlignLeft)
        layout1.addWidget(self.email_input)
        layout1.addWidget(QLabel("Password:"))
        layout1.addWidget(self.password_input)
        layout1.addWidget(self.log_in_button)

        layout1.setSpacing(10)  
        layout1.setAlignment(Qt.AlignTop)  # Align widgets to the top of the window

        layout2 = QHBoxLayout()
        layout2.addWidget(self.drop_down_menu_for_class)
        layout2.addWidget(self.drop_down_menu_for_resource)
        layout2.addWidget(self.start_download_button)
        layout2.addWidget(self.open_folder_button)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.status_console)
        
        # Set the main layout for the widget
        main_layout = QVBoxLayout()  # Main vertical layout for the entire window
        
        # Add layouts to the main layout vertically
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignTop)

        self.setLayout(main_layout)
    
        # Connect the class selection change event
        self.drop_down_menu_for_class.currentIndexChanged.connect(self.update_resource_drop_down_menu)

    def open_folder(self):
        folder_path = os.getcwd()
        Popen(['explorer', folder_path])


    def log_in(self):
        # Disable the log-in button
        self.log_in_button.setEnabled(False)
        
        # Create a new thread for the login process
        self.login_thread = Thread(target=self.log_in_worker)
            
        # Start the login thread
        self.login_thread.start()

    def log_in_worker(self):
        # Save the email and password to the crawler
        self.crawler.email = self.email_input.text()
        self.crawler.password = self.password_input.text()
        
        # print "Logging in..."
        self.status_console.append("Logging in...")

        # Perform the login process
        self.log_in_status = self.crawler.log_in()
        
        # Update the GUI from the main thread
        QMetaObject.invokeMethod(self, "handle_login_result", Qt.QueuedConnection)

    @pyqtSlot()
    def handle_login_result(self):
        if self.log_in_status == False:
            # if log in failed, print "Log in failed" in status_console
            self.status_console.append("Log in failed, please manually log in to see if there is any error message")
            # turn on the log in button
            self.log_in_button.setEnabled(True)
            # clear the email and password input
            # self.email_input.clear()
            self.password_input.clear()
        else:
            # if log in successfully, print "Log in successfully" in status_console
            self.status_console.append("Log in successfully")

            # Clear the email and password input
            self.email_input.clear()
            self.password_input.clear()
            
            # after log in successfully, get the class_dict
            self.crawler.get_class_dropDown_menu()

            # print the class_dict in the drop down menu
            self.drop_down_menu_for_class.addItem("Select a class")
            self.drop_down_menu_for_resource.addItem("Select a resource")

            for i in range(len(self.crawler.class_dict)):
                self.drop_down_menu_for_class.addItem(self.crawler.class_dict[i]['class_name'])
            
            # Enable the drop-down menu and start download button
            self.drop_down_menu_for_class.setEnabled(True)
            self.start_download_button.setEnabled(True)

            # Update the resource drop-down menu
            self.update_resource_drop_down_menu()
    
    @pyqtSlot()
    def update_resource_drop_down_menu(self):
        # Clear the session dictionary and disable the resource drop-down menu
        self.crawler.session_dict = {}
        self.drop_down_menu_for_resource.clear()
        self.drop_down_menu_for_resource.setEnabled(False)

        # Get the index of the selected class
        class_index = self.drop_down_menu_for_class.currentIndex() - 1

        if class_index >= 0:
            # Update the session information based on the selected class
            self.crawler.get_resource_dropDown_menu(class_index=class_index)

            # Update the resource drop-down menu
            self.drop_down_menu_for_resource.addItem("Select a resource")
            for i in range(len(self.crawler.session_dict)):
                self.drop_down_menu_for_resource.addItem(self.crawler.session_dict[i]['session_name'])

            self.drop_down_menu_for_resource.setEnabled(True)
        
    def start_download(self):
        # Disable the start download button
        self.start_download_button.setEnabled(False)
        # TODO: Create a new thread for the download process, add a progress bar, and make it in a new thread later
        # print "Start Downloading..."
        if self.drop_down_menu_for_class.currentText() != "Select a class" \
            and self.drop_down_menu_for_resource.currentText() != "Select a resource":
            self.status_console.append("Start Downloading...")
            self.start_download_worker()
        else:
            self.status_console.append("Please select a class and a resource")
        # Enable the start download button
        self.start_download_button.setEnabled(True)

    @pyqtSlot()
    def start_download_worker(self):
        # from those selected class and resource, start the download process
        number_of_file = self.crawler.download_files(self.drop_down_menu_for_class.currentIndex()-1, self.drop_down_menu_for_resource.currentIndex()-1)
        if number_of_file == 0:
            self.status_console.append("No file to download")
        elif number_of_file == 1:
            self.status_console.append(f"Download finished {number_of_file} file")
        else:
            self.status_console.append(f"Download finished {number_of_file} files")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    # window.crawler.driver.quit()
