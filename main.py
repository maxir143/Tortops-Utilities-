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
        try:
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

    def new_window(name: str, layout: list, multiple: bool = False, **kargs):
        if not multiple:
            if name in WINDOWS:
                if WINDOWS[name]:
                    return
        _window = sg.Window(WINDOWS_NAMES[name], layout, **kargs)
        try:
            WINDOWS[name].append(_window)
        except:
            WINDOWS[name] = [_window]

    def destroy_window(name, window):
        WINDOWS[name].remove(window)
        window.close()

    def windows_bug(**kargs):
        _title = 'report_bug'
        _layout = [[sg.Titlebar(WINDOWS_NAMES[_title])],
                   [sg.Text('Error:', size=5), sg.Multiline('', k='error')],
                   [sg.Text('ID:', size=5), sg.InputText('', k='id', size=4), sg.Button('Submit', k='submit', expand_x=True)]]
        new_window(_title, _layout, keep_on_top=True, finalize=True, **kargs)

    def windows_config(data: dict, **kargs):
        if data is None:
            return
        _title = 'config'
        _layout = [[sg.Titlebar(WINDOWS_NAMES[_title])],
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
        new_window(_title, _layout, keep_on_top=True, finalize=True, **kargs)

    def update_data(old_data: dict, new_data: dict):
        if old_data and new_data:
            for key in new_data.keys():
                if key in old_data:
                    old_data[key] = new_data[key]
            return True
        return False

    def auto_record():
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
                    file_name = f'{DATE.day}-{DATE.month}-{DATE.year}({DATE.hour}-{DATE.minute}-{DATE.second})'
                    RECORDER.start_recording(file_name)

    """
    Program =====================================================================================
    """
    # VARIABLES
    DATE = dt.now()
    DIR = user_data_dir('Utilities', 'Tortops', roaming=True)
    os.makedirs(DIR, exist_ok=True)
    WINDOWS = {}
    DATA = {
        'teleop_name': 'Teleop',
        'gsheet_url': '',
        'json_file': DIR,
        'gsheet_page': '',
        'rec_folder_path': DIR,
        'fps': 15,
        'recording_urls': 'teleoperation',
        'max_time_recording': 120,
        'save_file': f'{DIR}\config.ini',
        'config_section': 'Config'
    }
    WINDOWS_NAMES = {
        'main': 'main_window',
        'report_bug': 'Reportar error',
        'config': 'Configuracion',
    }
    EVENTS = {
        'report_bug': 'Reportar error',
        'stop_recording': 'Detener grabacion',
        'auto_click': 'Auto click',
        'config': 'Configuracion',
        'debug': 'Consola',
        'exit': 'Salir'
    }
    EVENTS_MENU = list(EVENTS.values())

    # Init Browser
    BROWSER = Browser()
    # Init Recorder
    RECORDER = Recorder(DATA['rec_folder_path'], DATA['fps'], int(DATA['max_time_recording']) * int(DATA['fps']) * 60)
    threading.Thread(target=auto_record, daemon=True).start()

    # MAIN WINDOW
    LAYOUT = [[sg.Button('', image_filename=resource_path('tortoise.png'), image_size=(100, 100), border_width=0, button_color='white', right_click_menu=['&Right', EVENTS_MENU])]]
    new_window('main', LAYOUT, size=(100, 100), grab_anywhere=True, keep_on_top=True, alpha_channel=0.6, no_titlebar=True, transparent_color='white', element_padding=0, margins=(0, 0), finalize=True)

    # GUI LOOP
    while True:
        window, event, values = sg.read_all_windows()
        # print(f'Ventana: {window.Title}, Evento: {event}')
        if window.Title == WINDOWS_NAMES['main']:
            if event == EVENTS['report_bug']:
                windows_bug()
            elif event == EVENTS['config']:
                windows_config(data=DATA)
            elif event == EVENTS['stop_recording']:
                RECORDER.stop_recording()
            elif event == EVENTS['debug']:
                print_window('[CONSOLA]')
            elif event == EVENTS['auto_click']:
                pass
            elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == EVENTS['exit']:
                break
        elif window.Title == WINDOWS_NAMES['config']:
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

        elif window.Title == WINDOWS_NAMES['report_bug']:
            if event == 'submit':
                g_sheet = SheetManager(DATA['json_file'], DATA['gsheet_url'])
                if not g_sheet.check_connection():
                    continue
                if values['error'] != '' and values['id'] != '':
                    date = f'{DATE.day}/{DATE.month}/{DATE.year} {DATE.hour}:{DATE.minute}:{DATE.second}'
                    format_data = {'A': values['id'], 'D': values['error'], 'DATE': DATA['teleop_name'], 'F': date}
                    g_sheet.send_report(DATA['gsheet_page'], format_data)
                    destroy_window('report_bug', window)
            elif event == sg.WINDOW_CLOSED:
                destroy_window('report_bug', window)

    # Ensure all windows to close
    for name in WINDOWS:
        for win in WINDOWS[name]:
            win.close()


if __name__ == '__main__':
    main()
