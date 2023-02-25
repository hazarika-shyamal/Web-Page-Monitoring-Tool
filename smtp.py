from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import smtplib
import matplotlib.pyplot as plt


class Monitor:
    def __init__(self, url, tag, attribute, value, interval, email_address, email_password):
        self.url = url
        self.tag = tag
        self.attribute = attribute
        self.value = value
        self.interval = interval
        self.email_address = email_address
        self.email_password = email_password
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.previous_state = None

    def __del__(self):
        self.driver.quit()

    def wait_for_page_load(self):
        # Wait for the page to load completely
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

    def get_element_attribute(self):
        # Use BeautifulSoup to extract the specified tag, attribute, and value
        self.driver.get(self.url)
        self.wait_for_page_load()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        element = soup.find(self.tag, {self.attribute: self.value})
        return str(element)

    def check_page_state(self):
        # Calculate the difference between the current and previous states of the page
        current_state = self.get_element_attribute()
        if self.previous_state is not None and self.previous_state != current_state:
            self.send_email(current_state)
        self.previous_state = current_state

    def send_email(self, current_state):
        # Send an email notification with the current state of the page
        subject = f"Page content has changed for {self.url}"
        message = f"Previous state:\n{self.previous_state}\n\nCurrent state:\n{current_state}"
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, self.email_address,
                            f'Subject: {subject}\n\n{message}')
            server.quit()
            print("Email notification sent")
        except Exception as e:
            print(f"Error sending email: {e}")

    def monitor_page(self):
        # Monitor the page and check its state at regular intervals
        while True:
            try:
                self.check_page_state()
            except Exception as e:
                print(f"Error monitoring page: {e}")
            time.sleep(self.interval)

    def plot_graph(self, changes):
        # Create a graph of the changes over time
        x, y = zip(*changes.items())
        plt.plot(x, y)
        plt.title(f"Changes in page content for {self.url}")
        plt.xlabel("Time")
        plt.ylabel("Number of changes")
        plt.show()

    def start(self):
        # Start monitoring the page and plot the changes over time
        changes = {}
        start_time = time.time()
        while time.time() - start_time < 3600:  # monitor for one hour
            try:
                current_state = self.get_element_attribute()
                if current_state in changes:
                    changes[current_state] += 1
                else:
                    changes[current_state] = 1
                self.check_page_state()
            except Exception as e:
                print(f"Error monitoring page: {e}")
            time.sleep(self.interval)
        self.plot_graph(changes)


monitor1 = Monitor("https://www.example.com", "h1", "class",
                   "example", 60, "example@gmail.com", "password")
monitor2 = Monitor("https://www.example2.com", "h2", "class",
                   "example2", 60, "example@gmail.com", "password")

monitor1.start()
monitor2.start()
