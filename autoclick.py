import time
import sys
from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import PySimpleGUI as sg


class AutoClick:
    def __init__(self):
        self.mouse = Controller()
        self.points_in_screen = []
        self.state = 0
        self.sound = 0
        self.flag = 0
        self.flags_state = []
        self.layout = [[sg.Titlebar('Auto Click')],
                       [sg.Text('<Ctrl> to record coordinate', key='display_text', font=("Helvetica", "10"))],
                       [sg.Button('Start', key='btn_start', disabled=True, tooltip='Start/Stop <SHIFT>'), sg.Button('Erase', key='btn_erase', disabled=True), sg.Button('Reset', key='btn_reset', disabled=True), sg.Button('Quit')],
                       [sg.Listbox([], size=(25, 5), enable_events=True, key='cords_list')],
                       [[sg.Text('Record coordinate <CTRL> \rStart / Stop script <SHIFT>', key='info_text', font=("Helvetica", "8"), size=(25, 5))]]]
        self.window = sg.Window('Auto Click', self.layout, size=(220, 200), disable_minimize=True, return_keyboard_events=True, use_default_focus=True)

    def printInUi(self, txt=None):
            try:
                self.window['display_text'].update(txt)
            except:
                sys.exit()

    def falseClick(self, iter):
        for pos in self.points_in_screen:
            should_continue = self.flags_state[iter]
            if should_continue is False:
                return
            self.mouse.position = pos
            self.mouse.press(Button.left)
            self.mouse.release(Button.left)
            self.printInUi('Clicked on: {0}'.format(pos))
            time.sleep(1)
        self.falseClick(iter)

    def moveMousePosUi(self):
        index = self.window["cords_list"].Widget.curselection()
        if index:
            index = index[0]
            self.mouse.position = self.points_in_screen[index]

    def recordClick(self):
        if self.state == 0 or self.state == 2:
            self.points_in_screen.append(self.mouse.position)
            self.updateCordListUi(self.points_in_screen)
            self.printInUi('Coord added: {}'.format(self.mouse.position))
            self.focusUi()

    def updateCordListUi(self, cords):
        format_cord = []
        for i in cords:
            format_cord.append('x: {}, y: {}'.format(i[0], i[1]))
        self.window["cords_list"].update(format_cord)
        if cords:
            self.window['btn_erase'].update(disabled=False)
            self.window['btn_start'].update(disabled=False)
            self.window['btn_reset'].update(disabled=False)
            self.window['cords_list'].update(set_to_index=[len(self.points_in_screen) - 1], scroll_to_index=len(self.points_in_screen) - 1)
        else:
            self.window['btn_erase'].update(disabled=True)
            self.window['btn_start'].update(disabled=True)
            self.window['btn_reset'].update(disabled=True)
            if self.state == 2:
                self.state = 0

    def focusUi(self):
        self.window.BringToFront()

    def eraseCordSelected(self, list="cords_list"):
        if self.state == 0 or self.state == 2:
            index = self.window[list].get()
            if index:
                index = self.window["cords_list"].GetIndexes()
                self.printInUi('Coord deleted: {}'.format(self.points_in_screen[index[0]]))
                self.points_in_screen.pop(index[0])
                self.updateCordListUi(self.points_in_screen)

    def startClick(self, message='Starting task'):
        if self.state == 0:
            if self.points_in_screen:
                self.printInUi(message)
                self.state = 1
                self.flags_state.append(True)
                self.flag = len(self.flags_state) - 1
                threading.Thread(target=lambda:self.falseClick(self.flag),daemon=True).start()
        elif self.state == 2:
            self.state = 0
            self.startClick('Resume')
        elif self.state == 1:
            self.state = 2
            self.focusUi()
            self.flags_state[self.flag] = False
            self.printInUi('Pause')

    def resetClick(self):
        if self.state != 1:
            self.state = 0
            self.points_in_screen = []
            if self.flags_state:
                self.flags_state[self.flag] = False
            self.updateCordListUi(self.points_in_screen)
            self.printInUi('Coords reset successfully')

    def run(self):
        with keyboard.GlobalHotKeys({'<ctrl>': self.recordClick,'<shift>': self.startClick}) as s:
            while True:
                event, values = self.window.read()
                # See if user wants to quit or self.window was closed
                if event == 'btn_start':
                    self.startClick()
                elif event == 'btn_reset':
                    self.resetClick()
                elif event == 'btn_erase':
                    self.eraseCordSelected()
                elif event == 'cords_list':
                    self.moveMousePosUi()
                elif event == sg.WINDOW_CLOSED or event == 'Quit':
                    break
            self.window.close()

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()


'''
QUICK START
click = autoclick()
click.run()
'''
