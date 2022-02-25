import time
from selenium.webdriver.common.by import By
import cv2
import numpy as np
import pyautogui
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os
import threading

class WebBrowser:
    def __init__(self):
        self.recording = False
        self.total_tabs = []
        self.driver = None

    def run(self, url: str = 'https://google.com/', maximize: bool = True):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        self.driver.get(url)
        if maximize:
            self.driver.maximize_window()

    def log_in(self, user: str = '', password: str = ''):
        self.is_browser_alive()
        try:
            self.driver.find_element(By.ID, 'mat-input-0').send_keys(user)
            self.driver.find_element(By.ID, 'mat-input-1').send_keys(password)
            return True  # Change state machine
        except Exception as e:
            print(e)

    def is_browser_alive(self):
        try:
            if len(self.driver.window_handles) == 1:
                self.driver.switch_to.window(self.driver.window_handles[0])
                u = self.driver.current_url.split('/')
                if u[0] == 'chrome:':
                    self.driver.get('')
            return True
        except Exception as e:
            print(e)
            self.driver.quit()
            sys.exit()

    def click_button(self, button: str = None):
        self.is_browser_alive()
        try:
            self.driver.find_element(By.XPATH, button).click()
            return True
        except Exception as e:
            print(e)

    def get_current_page(self):
        self.is_browser_alive()
        url = self.driver.current_url
        url = url.split('/')
        return url[-1]

    def wait_teleop(self):
        def run():
            while True:
                time.sleep(1)
                page = self.get_current_page()
                if self.recording is False:
                    if page == 'teleoperation':
                        self.start_recording()
                else:
                    if page != 'teleoperation':
                        self.stop_recording()

        x = threading.Thread(target=run, daemon=True)
        x.start()

    def stop_recording(self):
        self.recording = False

    def quit(self):
        print('adios')
        self.driver.quit()

    def start_recording(self):
        def record():
            screen_size = tuple(pyautogui.size())
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            fps = 15
            e = datetime.datetime.now()
            folder = "%s-%s-%s" % (e.day, e.month, e.year)
            os.makedirs(folder, exist_ok=True)
            date = "%s/%s-%s-%s.avi" % (folder, e.hour, e.minute, e.second)
            out = cv2.VideoWriter(date, fourcc, fps, screen_size)
            max_recording_time = 60 * 60 * 2
            for i in range(int(max_recording_time * fps)):  # Recording
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
                if self.recording is False:
                    cv2.destroyAllWindows()
                    out.release()
                    return

        self.recording = True
        x = threading.Thread(target=record, daemon=True)
        x.start()