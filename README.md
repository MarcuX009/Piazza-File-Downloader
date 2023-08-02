# Piazza File Downloader

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)

The Piazza File Downloader is a Python tool with a simple user interface application that allows you to download files from your Piazza class sessions effortlessly. It utilizes web scraping to interact with the Piazza platform and retrieve files, making it a convenient solution for organizing and accessing your course materials.

## Features

- **User-friendly GUI:** The Piazza File Downloader provides an intuitive GUI for a seamless user experience. Simply log in to your Piazza account, select the desired class and session, and start downloading files with ease.

- **Secure Login:** Your Piazza login credentials are used only to access your account and retrieve files. The tool does not store or share any user information.

- **Class and Session Selection:** Choose from your enrolled classes and sessions through convenient drop-down menus, making it easy to navigate and find the files you need.

- **Download Status Console:** Stay informed of the download progress and status with the integrated status console. Receive feedback on successful logins and download completions.

## How to Use

1. Clone this repository to your local machine.
2. Install the required dependencies using the following command:
   ```
   pip install -r requirements.txt
   ```
3. Run the application by executing the `GUI.py` script:
   ```
   python GUI.py
   ```
   or you can just simply run the `GUI.exe`.

4. Upon launching the application, enter your Piazza email and password in the input fields and click the "Log in" button. The tool will securely log in to your Piazza account.
5. After successful login, select the class and session from the respective drop-down menus.
6. Click the "Start Download" button to initiate the file download process. The status console will display the progress and completion messages.
7. All downloaded files will be saved in the corresponding class and session folders within the current working directory.

## Requirements

- Python 3.x
- PyQt5
- Selenium

## Disclaimer

The Piazza File Downloader is intended for personal use to facilitate file retrieval from your Piazza classes. Ensure that you have appropriate authorization to access and download files from Piazza. Use the tool responsibly and adhere to the terms of service of the Piazza platform.

## Contributing

Contributions to the project are welcome! If you find any issues or have suggestions for improvement, feel free to open an issue or submit a pull request.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.