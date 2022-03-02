import os
from datetime import datetime as dt
import PySimpleGUI as sg
from GSheet import SheetManager
from configparser import ConfigParser
import validators
from Recorder import Recorder


def main():
    """
        FUNCTIONS =====================================================================================
    """

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

    def popup_error(title: str = 'Mandar Error', data: list = None, **kargs):
        _data = ['', ''] if data is None else data
        _layout = [[sg.Titlebar(title)],
                   [sg.Text('Error:', size=5), sg.Multiline(_data[0], k='ERROR')],
                   [sg.Text('ID:', size=5), sg.InputText(_data[1], k='ID', size=4), sg.Button('Submit', k='submit', expand_x=True)]]
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
                   [sg.Text('- TELEOPERADOR')],
                   [sg.Text('Nombre:', s=8), sg.InputText(_teleop_name, k='teleop_name', expand_x=True)],
                   [sg.Text('-  GOOGLE SHEET')],
                   [sg.Text('URL:', s=8), sg.InputText(_url, k='gsheet_url', enable_events=True, expand_x=True)],
                   [sg.Text('JSON:', s=8), sg.InputText(_json, k='json_file', disabled=True, enable_events=True), sg.FileBrowse(k='ignore', disabled=True)],
                   [sg.Text('Pagina:', s=8), sg.InputCombo([], default_value=_page, k='gsheet_page', expand_x=True, disabled=True)],
                   [sg.Text('VIDEO')],
                   [sg.Text('Carpeta:', s=8), sg.InputText(_video_folder, k='rec_folder_path', disabled=True, enable_events=True), sg.FolderBrowse(k='ignore', disabled=False)],
                   [sg.Text('Tiempo maximo:', s=8), sg.InputText(_max_time, k='max_time_recording', expand_x=True)],
                   [sg.Text('FPS:', s=8), sg.InputCombo(['1', '12', '15', '24', '30', '60'], default_value=_fps, k='fps', expand_x=True)],
                   [sg.Text('- BUSCADOR')],
                   [sg.Text('pagina(s):', s=8), sg.InputText(_record_urls, k='recording_urls', expand_x=True)],
                   [sg.Button('Guardar', k='save', expand_x=True), sg.Button('Salir', k='exit', expand_x=True)]]

        _window = sg.Window('Configuraciones globales', _layout, keep_on_top=True, modal=True, **kargs)
        while True:
            _event, _values = _window.read()
            print(_event, _values)
            if _event == 'url':
                if validators.url(_values['url']):
                    _window.Element('fb').Update(disabled=False)
                else:
                    _window.Element('fb').Update(disabled=True)
                    _window.Element('json').Update(value='')
            elif _event == 'json':
                _sheet = SheetManager(_values['json'], _values['url'])
                if _sheet:
                    _window.Element('page').Update(disabled=False)
                    _sheets = _sheet.get_pages().keys()
                    print(_sheets)
                    if _sheets:
                        _window.Element('page').Update(values=list(_sheets))
                else:
                    _window.Element('page').Update(disabled=True, value='')
            elif _event == 'save':
                save_file(DATA['save_file'], DATA['config_section'], _values)
            elif _event == sg.WINDOW_CLOSED or _event == 'Quit' or _event == 'exit':
                break
        _window.close()

    """
    Program =====================================================================================
    """
    DATA = {'teleop_name': 'Teleop',
            'gsheet_url': '',
            'json_file': '.json',
            'gsheet_page': 0,
            'rec_folder_path': '/',
            'fps': 15,
            'recording_urls': '',
            'max_time_recording': 120,
            'save_file': 'config.ini',
            'config_section': 'Config'}

    read_data = read_file(DATA['save_file'], DATA['config_section'])
    if read_data:
        DATA['teleop_name'] = read_data['teleop_name']
        DATA['gsheet_url'] = read_data['gsheet_url']
        DATA['json_file'] = read_data['json_file']
        DATA['gsheet_page'] = read_data['gsheet_page']
        DATA['rec_folder_path'] = read_data['rec_folder_path']
        DATA['fps'] = int(read_data['fps'])
        # DATA['recording_urls'] = config_data['record_urls']
        DATA['max_time_recording'] = int(read_data['max_time_recording'])
    else:
        popup_config(data=DATA)

    E = dt.now()
    RECORDER = Recorder(DATA['rec_folder_path'], DATA['fps'], DATA['max_time_recording'] * DATA['fps'] * 60)
    COMMANDS = {'send_error': 'Reportar error', 'record': 'Grabar', 'config': 'Configuracion', 'exit': 'Salir'}
    COMMANDS_MENU = list(COMMANDS.values())

    LAYOUT = [[sg.Button('', image_filename='tortoise.png', image_size=(100, 100), border_width=0, button_color='white', right_click_menu=['&Right', COMMANDS_MENU])]]
    MAIN_WINDOW = sg.Window('Auto Click', LAYOUT, size=(100, 100), grab_anywhere=True, keep_on_top=True, alpha_channel=0.8, no_titlebar=True, transparent_color='white', element_padding=0, margins=(0, 0))

    while True:
        event, values = MAIN_WINDOW.read()
        # print(event, values)
        if event == COMMANDS['send_error']:
            def send_error(title, data: list = None):
                pop = popup_error(title, data)
                if pop[0]:
                    _data = pop[1]
                    if _data['ERROR'] != '' and _data['ID'] != '':
                        _sheet = SheetManager(DATA['json_file'], DATA['gsheet_url'])
                        date = f'{E.day}/{E.month}/{E.year} {E.hour}:{E.minute}:{E.second}'
                        _format_data = {'A': _data['ID'], 'D': _data['ERROR'], 'E': DATA['teleop_name'], 'F': date}
                        _sheet.send_report(DATA['gsheet_page'], _format_data)
                    else:
                        send_error('FALTAN RELLENAR CAMPOS', [_data['ERROR'], _data['ID']])

            send_error('Configuracion')

        elif event == COMMANDS['record']:
            if not RECORDER.is_recording():
                print('Grabando')
                file_name = f'{E.day}-{E.month}-{E.year}({E.hour}-{E.minute}-{E.second})'
                RECORDER.start_recording(file_name)
            else:
                RECORDER.stop_recording()
                print('Ya no')
        elif event == COMMANDS['config']:
            popup_config(data=DATA)
        elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == COMMANDS['exit']:
            break
    MAIN_WINDOW.close()


if __name__ == '__main__':
    main()
