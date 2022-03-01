import os
import sys
import time
from datetime import datetime
import PySimpleGUI as sg
import pyautogui

from GPEmu import GamePad
from GSheet import SheetManager
from configparser import ConfigParser
import threading
import validators

from Recorder import Recorder

global SAVE_FILE, CONFIG_DATA, NAME, URL, JSON, PAGE, RECORDING_FOLDER, FPS,RECORDING_URL, MAX_TIME_RECORDING


def main():
    ''' xddd '''
    '''screen_size = tuple(pyautogui.size())
    e = datetime.now()
    folder = "%s-%s-%s" % (e.day, e.month, e.year)
    name = "%s/%s-%s-%s.avi" % (folder, e.hour, e.minute, e.second)
    os.makedirs(folder, exist_ok=True)

    recorder = Recorder(folder, name, screen_size, 15, 15 * 60)'''

    '''browser = Browser()
    print(browser.get_current_page())'''


    def save_file(file: str = '', section: str = '', data: dict = None):
        if data is None or section == '':
            return
        _config = ConfigParser()
        _config.read(file)
        if section not in _config.sections():
            _config.add_section(section)
        for _key, _value in data.items():
            _config.set(section, _key, str(_value))
        with open(file, 'w') as f:
            _config.write(f)
        return True

    def read_file(file: str = '', section: str = ''):
        if not os.path.exists(file):
            return False
        _config = ConfigParser()
        _config.read(file)
        _sections = _config.sections()
        if section in _sections:
            return dict(_config.items(section))
        elif _sections is not []:
            _values = []
            for s in _sections:
                _values.append(dict(_config.items(s)))
            return _values

    def popup_error(title='Mandar Error', data=None, **kargs):
        if data is None:
            data = ['', '']
        _layout = [[sg.Titlebar(title)],
                   [sg.Text('Error:', size=5), sg.Multiline(data[0], k='ERROR')],
                   [sg.Text('ID:', size=5), sg.InputText(data[1], k='ID', size=4), sg.Button('Submit', k='submit', expand_x=True)]]
        return sg.Window('Mandar Error', _layout, keep_on_top=True, modal=True, **kargs).read(close=True)

    def popup_config(title='Configuracion', data: dict = None, **kargs):
        teleop_name,url,json,page,video_folder,fps,record_urls,max_time = '','','','','','','','120'
        if data is not None:
            print(data)
            teleop_name = data['teleop_name']
            url = data['url']
            json = data['json']
            page = data['page']
            video_folder = data['video_folder']
            fps = data['fps']
            record_urls = data['record_urls']
            max_time = data['max_time']

        _layout = [[sg.Titlebar(title)],
                   [sg.Text('- TELEOPERADOR')],
                   [sg.Text('Nombre:', s=8), sg.InputText(teleop_name, k='teleop_name', expand_x=True)],
                   [sg.Text('-  GOOGLE SHEET')],
                   [sg.Text('URL:', s=8), sg.InputText(url, k='url', enable_events=True, expand_x=True)],
                   [sg.Text('JSON:', s=8),sg.InputText(json, k='json', disabled=True, enable_events=True), sg.FileBrowse(k='fb',disabled=True)],
                   [sg.Text('Pagina:', s=8), sg.InputCombo([],default_value=page, k='page',expand_x=True, disabled=True)],
                   [sg.Text('VIDEO')],
                   [sg.Text('Carpeta:',s=8),sg.InputText(video_folder, k='video_folder', disabled=True, enable_events=True), sg.FolderBrowse(k='save_folder', disabled=False)],
                   [sg.Text('Tiempo maximo:', s=8), sg.InputText(max_time, k='max_time', expand_x=True)],
                   [sg.Text('FPS:', s=8), sg.InputCombo(['1','12','15','24','30','60'],default_value=fps, k='fps', expand_x=True)],
                   [sg.Text('- BUSCADOR')],
                   [sg.Text('pagina(s):', s=8), sg.InputText(record_urls, k='record_urls', expand_x=True)],
                   [sg.Button('Guardar',k='save', expand_x=True), sg.Button('Salir', k='exit', expand_x=True)]]

        _window = sg.Window('Configuraciones globales', _layout, keep_on_top=True, modal=True, **kargs)
        while True:
            event, values = _window.read()
            print(event, values)
            if event == 'url':
                if validators.url(values['url']):
                    _window.Element('fb').Update(disabled=False)
                else:
                    _window.Element('fb').Update(disabled=True)
                    _window.Element('json').Update(value='')
            elif event == 'json':
                sheet = SheetManager(values['json'], values['url'])
                if sheet:
                    _window.Element('page').Update(disabled=False)
                    sheets = sheet.get_pages().keys()
                    print(sheets)
                    if sheets:
                        _window.Element('page').Update(values=list(sheets))
                else:
                    _window.Element('page').Update(disabled=True, value='')
            elif event == 'save':
                save_file(SAVE_FILE, CONFIG_SECTION, values)
            elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == 'exit':
                break
        _window.close()

    SAVE_FILE = 'config.ini'
    CONFIG_SECTION = 'Config'
    CONFIG_DATA = read_file(SAVE_FILE, CONFIG_SECTION)

    if CONFIG_DATA:
        NAME = CONFIG_DATA['teleop_name']
        URL = CONFIG_DATA['url']
        JSON = CONFIG_DATA['json']
        PAGE = CONFIG_DATA['page']
        RECORDING_FOLDER = CONFIG_DATA['video_folder']
        FPS = CONFIG_DATA['fps']
        RECORDING_URL = CONFIG_DATA['record_urls']
        MAX_TIME_RECORDING = CONFIG_DATA['max_time']
    else:
        popup_config()

    screen_size= (100,100)
    time_format = int(MAX_TIME_RECORDING) * int(FPS) * 60
    RECORDER = Recorder(RECORDING_FOLDER,FPS, time_format)

    commands = {'send_error': 'Reportar error','record': 'Grabar','config': 'Configuracion', 'exit': 'Salir'}
    commands_menu = list(commands.values())

    layout = [[sg.Button('', image_filename='tortoise.png', image_size=(100, 100), border_width=0, button_color='white', right_click_menu=['&Right', commands_menu])]]
    window = sg.Window('Auto Click', layout, size=(100, 100), grab_anywhere=True, keep_on_top=True, alpha_channel=0.8, no_titlebar=True, transparent_color='white', element_padding=0, margins=(0, 0))

    while True:
        event, values = window.read()
        #print(event, values)
        if event == commands['send_error']:
            def send_error(title, data: list = None):
                pop = popup_error(title, data)
                if pop[0]:
                    _data = pop[1]
                    if _data['ERROR'] != '' and _data['ID'] != '':
                        _sheet = SheetManager(JSON, URL)
                        _e = datetime.now()
                        date = f'{_e.day}/{_e.month}/{_e.year} {_e.hour}:{_e.minute}:{_e.second}'
                        _format_data = {'A':_data['ID'],'D':_data['ERROR'], 'E':NAME, 'F': date}
                        _sheet.send_report(PAGE, _format_data)
                    else:
                        send_error('FALTAN RELLENAR CAMPOS', [_data['ERROR'], _data['ID']])
            send_error('Configuracion')

        elif event == commands['record']:
            if not RECORDER.is_recording():
                print('Grabando')
                _e = datetime.now()
                file_name = f'{_e.day}-{_e.month}-{_e.year}({_e.hour}-{_e.minute}-{_e.second})'
                RECORDER.start_recording(file_name)
            else:
                RECORDER.stop_recording()
                print('Ya no')
        elif event == commands['config']:
            popup_config(data=CONFIG_DATA)
        elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == commands['exit']:
            break
    window.close()


if __name__ == '__main__':
    main()