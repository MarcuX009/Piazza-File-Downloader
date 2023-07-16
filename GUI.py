# GUI.py
# Description: This file contains the GUI for the Piazza File Downloader.
# Author: Wenjin Li
# Date: 2023/07/03

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QMetaObject, pyqtSlot
import requests
import threading

import web_crawler

class MainWindow(QWidget):
    crawler = web_crawler.Crawler()
    log_in_status = False
    class_dict = {}

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
        
        
        # # use a thread to run the log_in function if the log_in button is clicked
        # self.log_in_thread = threading.Thread(target=self.log_in)
        # self.log_in_button.clicked.connect(self.log_in_thread.start)
        self.log_in_button.clicked.connect(self.log_in)
        
        self.start_download_button = QPushButton("Start Download")
        self.start_download_button.clicked.connect(self.start_download)
        # self.start_download_button.setEnabled(False)  # Disable the button initially
        
        # create a drop down menu
        self.drop_down_menu = QComboBox()

        # Create status console
        self.status_console = QTextEdit()
        self.status_console.setReadOnly(True)
        
        # Create layout and add widgets
        layout1 = QHBoxLayout()
        layout1.addWidget(QLabel("Email:"), alignment=Qt.AlignLeft)
        layout1.addWidget(self.email_input)
        layout1.addWidget(QLabel("Password:"))
        layout1.addWidget(self.password_input)
        layout1.addWidget(self.log_in_button)
        layout1.addWidget(self.start_download_button)
        layout1.addWidget(self.drop_down_menu)
        
        # Set layout spacing and alignment
        layout1.setSpacing(10)  # Set spacing between widgets
        layout1.setAlignment(Qt.AlignTop)  # Align widgets to the top of the window
        layout1.addWidget(self.status_console)
        self.setLayout(layout1)

        # Create the login thread
        self.login_thread = threading.Thread(target=self.log_in_worker)

    def log_in(self):
        if not self.login_thread.is_alive():
            # Save the email and password to the crawler
            self.crawler.email = self.email_input.text()
            self.crawler.password = self.password_input.text()
            
            # Disable the log-in button
            self.log_in_button.setEnabled(False)
            
            # Start the login thread
            self.login_thread.start()

    def log_in_worker(self):
        self.log_in_status = self.crawler.log_in()
        
        # Update the GUI from the main thread
        QMetaObject.invokeMethod(self, "handle_login_result", Qt.QueuedConnection)

    @pyqtSlot()
    def handle_login_result(self):
        # save the email and password to the crawler
        # self.crawler.email = self.email_input.text()
        # self.crawler.password = self.password_input.text()
        # self.log_in_status = self.crawler.log_in()
        if self.log_in_status == False:
            # if log in failed, print "Log in failed" in status_console
            self.status_console.append("Log in failed")
            # clear the email and password input
            # self.email_input.clear()
            # self.password_input.clear()
        else:
            # if log in successfully, print "Log in successfully" in status_console
            self.status_console.append("Log in successfully")
           
            self.email_input.clear()
            self.password_input.clear()
            
            # after log in successfully, get the class_dict
            self.class_dict = self.crawler.class_dropDown_menu()

            # print the class_dict in the drop down menu
            self.drop_down_menu.addItem("Select a class")
            for i in range(len(self.class_dict)):
                self.drop_down_menu.addItem(self.class_dict[i]['class_name'])
            
            # Enable the start download button
            self.start_download_button.setEnabled(True)

    def start_download(self):
        # from the drop down menu, if user selected the class that they want to download, then start download that class and load that class's url
        if self.drop_down_menu.currentText() != "Select a class":
            self.crawler.download_files(self.class_dict[self.drop_down_menu.currentIndex()-1]['url'])
        else:
            self.status_console.append("Please select a class")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    window.crawler.driver.quit()
