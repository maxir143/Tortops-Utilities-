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
    """ RUN PROGRAM """
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

    def new_window(name: str, window: object, multiwindow:bool = False):
        try:
            WINDOWS[name].append(window)
        except:
            WINDOWS[name] = [window]

    def destroy_window(name, window):
        WINDOWS[name].remove(window)
        window.close()

    def windows_bug(title: str = 'report_bug', **kargs):
        _layout = [[sg.Titlebar(COMMANDS[title])],
                   [sg.Text('Error:', size=5), sg.Multiline('', k='error')],
                   [sg.Text('ID:', size=5), sg.InputText('', k='id', size=4), sg.Button('Submit', k='submit', expand_x=True)]]
        _window = sg.Window(COMMANDS[title], _layout, keep_on_top=True, finalize=True, **kargs)
        new_window(title, _window)

    def windows_config(title: str = 'config', data: dict = None, **kargs):
        if data is None:
            return
        _layout = [[sg.Titlebar(COMMANDS[title])],
                   [sg.Text('TELEOPERADOR')],
                   [sg.Text('Nombre:', s=10), sg.InputText(data['teleop_name'], k='teleop_name', expand_x=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('GOOGLE SHEET')],
                   [sg.Text('URL:', s=10), sg.InputText(data['gsheet_url'], k='gsheet_url', enable_events=True, expand_x=True)],
                   [sg.Text('JSON:', s=10), sg.InputText(data['json_file'], k='json_file', disabled=True, enable_events=True), sg.FileBrowse(k='fb', file_types=(("JSON Files", "*.json"),), disabled=True)],
                   [sg.Text('Pagina:', s=10), sg.InputCombo([data['gsheet_page']], default_value=data['gsheet_page'], k='gsheet_page', expand_x=True, disabled=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('VIDEO')],
                   [sg.Text('Carpeta:', s=10), sg.InputText(data['rec_folder_path'], k='rec_folder_path', disabled=False, enable_events=True)],  #
                   [sg.Text('Tiempo max:', s=10), sg.InputText(data['max_time_recording'], k='max_time_recording', expand_x=True)],
                   [sg.Text('FPS:', s=10), sg.InputCombo([1, 12, 15, 24, 30, 60], default_value=data['fps'], k='fps', expand_x=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('BUSCADOR')],
                   [sg.Text('pagina(s):', s=10), sg.InputText(data['recording_urls'], k='recording_urls', expand_x=True)],
                   [sg.Button('Guardar', k='save', expand_x=True), sg.Button('Abrir Folder', k='open_folder')]]

        _window = sg.Window(COMMANDS[title], _layout, keep_on_top=True, finalize=True, **kargs)
        new_window(title, _window)

    def update_data(old_data: dict, new_data: dict):
        if old_data and new_data:
            for key in new_data.keys():
                if key in old_data:
                    old_data[key] = new_data[key]
            return True
        return False

    def autorecording():
        _time_out_time = 5
        _time_out = _time_out_time

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
    DIR = user_data_dir('Utilities', 'Tortops', roaming=True)
    os.makedirs(DIR, exist_ok=True)

    WINDOWS = {}

    DATA = {'teleop_name': 'Teleop',
            'gsheet_url': '',
            'json_file': DIR,
            'gsheet_page': '',
            'rec_folder_path': DIR,
            'fps': 15,
            'recording_urls': 'teleoperation',
            'max_time_recording': 120,
            'save_file': f'{DIR}\config.ini',
            'config_section': 'Config'}

    if not update_data(DATA, read_file(DATA['save_file'], DATA['config_section'])):
        windows_config(data=DATA)

    # threading.Thread(target=autorecording, daemon=True).start()

    BROWSER = Browser()
    E = dt.now()
    RECORDER = Recorder(DATA['rec_folder_path'], DATA['fps'], int(DATA['max_time_recording']) * int(DATA['fps']) * 60)
    COMMANDS = {'report_bug': 'Reportar error', 'stop_recording': 'Detener grabacion', 'auto_click': 'Auto click', 'config': 'Configuracion', 'debug': 'Consola', 'exit': 'Salir'}
    COMMANDS_MENU = list(COMMANDS.values())

    LAYOUT = [[sg.Button('', image_filename=resource_path('tortoise.png'), image_size=(100, 100), border_width=0, button_color='white', right_click_menu=['&Right', COMMANDS_MENU])]]
    MAIN_WINDOW = sg.Window('Auto Click', LAYOUT, size=(100, 100), grab_anywhere=True, keep_on_top=True, alpha_channel=0.6, no_titlebar=True, transparent_color='white', element_padding=0, margins=(0, 0), finalize=True)
    WINDOWS['main'] = MAIN_WINDOW

    while True:
        window, event, values = sg.read_all_windows()
        # print(f'Ventana: {window.Title}, Evento: {event}')
        if window == WINDOWS['main']:
            if event == COMMANDS['report_bug']:
                windows_bug()
            elif event == COMMANDS['config']:
                windows_config(data=DATA)
            elif event == COMMANDS['stop_recording']:
                RECORDER.stop_recording()
            elif event == COMMANDS['debug']:
                print_window('[CONSOLA]')
            elif event == COMMANDS['auto_click']:
                pass
            elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == COMMANDS['exit']:
                break

        elif window.Title == COMMANDS['config']:
            if event == 'gsheet_url':
                if validators.url(values['gsheet_url']):
                    window.Element('fb').Update(disabled=False)
                else:
                    window.Element('fb').Update(disabled=True)
                    window.Element('json_file').Update(value='')
                    window.Element('gsheet_page').Update(value='')
            elif event == 'json_file':
                sheet = SheetManager(values['json_file'], values['gsheet_url'])
                if sheet.check_connection():
                    window.Element('gsheet_page').Update(disabled=False)
                    sheets = sheet.get_pages().keys()
                    if sheets:
                        window.Element('gsheet_page').Update(value=list(sheets)[0], values=list(sheets))
                else:
                    window.Element('gsheet_page').Update(disabled=True, value='')
            elif event == 'save':
                save_file(DATA['save_file'], DATA['config_section'], values)
                update_data(DATA, values)
                destroy_window('config', window)
            elif event == 'open_folder':
                os.startfile(DIR)
            elif event == sg.WINDOW_CLOSED:
                destroy_window('config', window)

        elif window.Title == COMMANDS['report_bug']:
            if event == 'submit':
                g_sheet = SheetManager(DATA['json_file'], DATA['gsheet_url'])
                if not g_sheet.check_connection():
                    continue
                if values['error'] != '' and values['id'] != '':
                    date = f'{E.day}/{E.month}/{E.year} {E.hour}:{E.minute}:{E.second}'
                    format_data = {'A': values['id'], 'D': values['error'], 'E': DATA['teleop_name'], 'F': date}
                    g_sheet.send_report(DATA['gsheet_page'], format_data)
                    destroy_window('report_bug', window)
            elif event == sg.WINDOW_CLOSED:
                destroy_window('report_bug', window)
            '''def report_bug(title, data: list = None):
                                _g_sheet = SheetManager(DATA['json_file'], DATA['gsheet_url'])
                                if not _g_sheet.check_connection():
                                    return
                                pop = windows_bug(title, data)
                                if pop[0]:
                                    _data = pop[1]
                                    
                                    else:
                                        report_bug('FALTA RELLENAR CAMPOS', [_data['error'], _data['id']])
                            report_bug('Configuracion')'''

    MAIN_WINDOW.close()


if __name__ == '__main__':
    main()
