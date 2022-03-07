import cv2
import numpy as np
import pyautogui
import threading
import os


class Recorder:
    def __init__(self, folder, fps, max_length):
        self.recording = False
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.screen_size = pyautogui.size()
        self.fps = fps
        self.max_length = max_length
        self.daemon = True

    def set_daemon(self, daemon):
        self.daemon = daemon

    def stop_recording(self):
        if self.recording:
            self.recording = False
            print('Stop Recording')

    def is_recording(self):
        return self.recording

    def start_recording(self, file_name):
        if self.is_recording():
            return
        print('Start Recording')
        def record():
            fps = int(self.fps)
            screen_size = self.screen_size
            max_length = self.max_length
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            file_name_format = f'{self.folder}/{file_name}.avi'
            out = cv2.VideoWriter(file_name_format, fourcc, fps, screen_size)
            max_recording_time = max_length
            for i in range(int(max_recording_time * fps)):  # Recording
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                out.write(frame)
                if self.recording is False:
                    cv2.destroyAllWindows()
                    out.release()
                    print(f'File Saved at {file_name_format}')
                    return
            print(f'File Saved at {file_name_format}')
            self.stop_recording()

        self.recording = True
        threading.Thread(target=record, daemon=self.daemon).start()
