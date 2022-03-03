import os
import sys
import threading
import time
from datetime import datetime as dt
import PySimpleGUI as sg
from GSheet import SheetManager
from configparser import ConfigParser
import validators
from Recorder import Recorder
from WebBrowserTortops import Browser
from appdirs import user_data_dir


def main():
    """
        FUNCTIONS =====================================================================================
    """

    def print_window(message='Error'):
        sg.Print(message, do_not_reroute_stdout=False)

    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

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

    def read_file(file: str, section: str):
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

    def popup_error(title: str = 'Mandar Error', data: list = None, **kargs):
        _data = ['', ''] if data is None else data
        _layout = [[sg.Titlebar(title)],
                   [sg.Text('Error:', size=5), sg.Multiline(_data[0], k='error')],
                   [sg.Text('ID:', size=5), sg.InputText(_data[1], k='id', size=4), sg.Button('Submit', k='submit', expand_x=True)]]
        return sg.Window('Mandar Error', _layout, keep_on_top=True, modal=True, **kargs).read(close=True)

    def popup_config(title: str = 'Configuracion', data: dict = None, **kargs):
        if data is None:
            return
        _teleop_name = data['teleop_name']
        _url = data['gsheet_url']
        _json = data['json_file']
        _page = data['gsheet_page']
        _video_folder = data['rec_folder_path']
        _fps = data['fps']
        _record_urls = data['recording_urls']
        _max_time = data['max_time_recording']

        _layout = [[sg.Titlebar(title)],
                   [sg.Text('TELEOPERADOR')],
                   [sg.Text('Nombre:', s=10), sg.InputText(_teleop_name, k='teleop_name', expand_x=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('GOOGLE SHEET')],
                   [sg.Text('URL:', s=10), sg.InputText(_url, k='gsheet_url', enable_events=True, expand_x=True)],
                   [sg.Text('JSON:', s=10), sg.InputText(_json, k='json_file', disabled=True, enable_events=True), sg.FileBrowse(k='fb', file_types=(("JSON Files", "*.json"),), disabled=True)],
                   [sg.Text('Pagina:', s=10), sg.InputCombo([_page], default_value=_page, k='gsheet_page', expand_x=True, disabled=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('VIDEO')],
                   [sg.Text('Carpeta:', s=10), sg.InputText(_video_folder, k='rec_folder_path', disabled=False, enable_events=True)],  #
                   [sg.Text('Tiempo max:', s=10), sg.InputText(_max_time, k='max_time_recording', expand_x=True)],
                   [sg.Text('FPS:', s=10), sg.InputCombo([1, 12, 15, 24, 30, 60], default_value=_fps, k='fps', expand_x=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('BUSCADOR')],
                   [sg.Text('pagina(s):', s=10), sg.InputText(_record_urls, k='recording_urls', expand_x=True)],
                   [sg.Button('Guardar', k='save', expand_x=True), sg.Button('Abrir Folder', k='open_folder'), sg.Button('Salir', k='exit', expand_x=True)]]

        _window = sg.Window('Configuraciones globales', _layout, keep_on_top=True, modal=True, **kargs)
        while True:
            _event, _values = _window.read()
            # print(_event, _values)
            if _event == 'gsheet_url':
                if validators.url(_values['gsheet_url']):
                    _window.Element('fb').Update(disabled=False)
                else:
                    _window.Element('fb').Update(disabled=True)
                    _window.Element('json_file').Update(value='')
                    _window.Element('gsheet_page').Update(value='')
            elif _event == 'json_file':
                _sheet = SheetManager(_values['json_file'], _values['gsheet_url'])
                if _sheet.check_connection():
                    _window.Element('gsheet_page').Update(disabled=False)
                    _sheets = _sheet.get_pages().keys()
                    if _sheets:
                        _window.Element('gsheet_page').Update(value=list(_sheets)[0], values=list(_sheets))
                else:
                    _window.Element('gsheet_page').Update(disabled=True, value='')
            elif _event == 'save':
                save_file(DATA['save_file'], DATA['config_section'], _values)
                update_data(DATA, _values)
            elif _event == 'open_folder':
                os.startfile(DIR)
            elif _event == sg.WINDOW_CLOSED or _event == 'Quit' or _event == 'exit':
                break
        _window.close()

    def update_data(old_data: dict, new_data: dict):
        if old_data and new_data:
            for key in new_data.keys():
                if key in old_data:
                    old_data[key] = new_data[key]
            return True
        return False

    def start_autorecording():
        threading.Thread(target=autorecording, daemon=True).start()

    def autorecording():
        _time_out_time = 30
        _time_out = _time_out_time
        _time_out = 5

        while True:
            time.sleep(1)

            def in_urls():
                _split_url_list = []
                for url in list(DATA['recording_urls'].split(',')):
                    _split_url_list.append(url.split("/")[-1])
                _split_current_url = BROWSER.get_current_page()
                if _split_current_url:
                    _split_current_url = BROWSER.get_current_page().split('/')[-1]
                    if _split_current_url in _split_url_list:
                        return True
                else:
                    RECORDER.stop_recording()
                    time.sleep(_time_out)

            if RECORDER.is_recording():
                if in_urls():
                    _time_out = _time_out_time
                else:
                    if _time_out > 0:
                        _time_out -= 1
                        print(f'Waiting for teleop, time left:{_time_out}')
                    else:
                        RECORDER.stop_recording()
            else:
                if in_urls():
                    _time_out = _time_out_time
                    file_name = f'{E.day}-{E.month}-{E.year}({E.hour}-{E.minute}-{E.second})'
                    RECORDER.start_recording(file_name)

    """
    Program =====================================================================================
    """
    DEBUG_CONSOLE = False
    DIR = user_data_dir('Utilities', 'Tortops', roaming=True)
    os.makedirs(DIR, exist_ok=True)

    DATA = {'teleop_name': 'Teleop',
            'gsheet_url': '',
            'json_file': '',
            'gsheet_page': '',
            'rec_folder_path': DIR,
            'fps': 15,
            'recording_urls': 'teleoperation',
            'max_time_recording': 120,
            'save_file': DIR + '\config.ini',
            'config_section': 'Config'}

    if not update_data(DATA, read_file(DATA['save_file'], DATA['config_section'])):
        popup_config(data=DATA)

    BROWSER = Browser()
    E = dt.now()
    RECORDER = Recorder(DATA['rec_folder_path'], DATA['fps'], int(DATA['max_time_recording']) * int(DATA['fps']) * 60)
    COMMANDS = {'send_error': 'Reportar error', 'stop_recording': 'Detener grabacion', 'config': 'Configuracion', 'debug': 'Consola', 'exit': 'Salir'}
    COMMANDS_MENU = list(COMMANDS.values())

    LAYOUT = [[sg.Button('', image_filename=resource_path('tortoise.png'), image_size=(100, 100), border_width=0, button_color='white', right_click_menu=['&Right', COMMANDS_MENU])]]
    MAIN_WINDOW = sg.Window('Auto Click', LAYOUT, size=(100, 100), grab_anywhere=True, keep_on_top=True, alpha_channel=0.6, no_titlebar=True, transparent_color='white', element_padding=0, margins=(0, 0), finalize=True)
    start_autorecording()
    while True:
        event, values = MAIN_WINDOW.read()
        # print(event, values)
        if event == COMMANDS['send_error']:
            def send_error(title, data: list = None):
                _g_sheet = SheetManager(DATA['json_file'], DATA['gsheet_url'])
                if not _g_sheet.check_connection():
                    return
                pop = popup_error(title, data)
                if pop[0]:
                    _data = pop[1]
                    if _data['error'] != '' and _data['id'] != '':
                        _date = f'{E.day}/{E.month}/{E.year} {E.hour}:{E.minute}:{E.second}'
                        _format_data = {'A': _data['id'], 'D': _data['error'], 'E': DATA['teleop_name'], 'F': _date}
                        _g_sheet.send_report(DATA['gsheet_page'], _format_data)
                    else:
                        send_error('FALTA RELLENAR CAMPOS', [_data['error'], _data['id']])

            send_error('Configuracion')
        elif event == COMMANDS['config']:
            popup_config(data=DATA)
        elif event == COMMANDS['stop_recording']:
            RECORDER.stop_recording()
        elif event == COMMANDS['debug']:
            print_window('[CONSOLA]')
        elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == COMMANDS['exit']:
            break
    MAIN_WINDOW.close()


if __name__ == '__main__':
    main()
