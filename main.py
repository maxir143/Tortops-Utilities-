import os
import threading
import time
from datetime import datetime as dt
import PySimpleGUI as sg
from GSheet import SheetManager
import validators
from Recorder import Recorder
from WebBrowserTortops import Browser
from appdirs import user_data_dir
from autoclick import AutoClick
from Sequencer import Sequencer, SequencerCreator
from utilities import read_file, save_file, resource_path


def main():
    """
        FUNCTIONS =====================================================================================
    """

    def print_window(message='Error'):
        sg.Print(message, do_not_reroute_stdout=False)

    def new_window(window_name: str, layout: list, multiple: bool = False, **kwargs):
        if not multiple:
            if str(window_name) in WINDOWS:
                if WINDOWS[window_name]:
                    _window = WINDOWS[window_name][0]
                    _window.bring_to_front()
                    return _window
        _window = sg.Window(WINDOWS_NAMES[window_name], layout, **kwargs)
        if window_name in WINDOWS:
            WINDOWS[window_name].append(_window)
        else:
            WINDOWS[window_name] = [_window]
        return _window

    def destroy_window(window_type, window_name):
        WINDOWS[window_type].remove(window_name)
        window_name.close()

    def windows_bug(**kwargs):
        _title = 'report_bug'
        _layout = [[sg.Titlebar(WINDOWS_NAMES[_title], icon=resource_path(r'images\bug_ico.png'))],
                   [sg.Text('Error:', size=5), sg.Multiline('', k='error')],
                   [sg.Text('ID:', size=5), sg.InputText('', k='id', size=4), sg.Button('Submit', k='submit', expand_x=True)]]
        new_window(_title, _layout, finalize=True, **kwargs)

    def windows_config(data: dict, **kwargs):
        if data is None:
            return

        _title = 'config'
        _layout = [[sg.Titlebar(WINDOWS_NAMES[_title], icon=resource_path(r'images\tortoise_ico.png'))],
                   [sg.Text('TELEOPERADOR')],
                   [sg.Text('Nombre:', s=10), sg.InputText(data['teleop_name'], k='teleop_name', expand_x=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('GOOGLE SHEET')],
                   [sg.Text('URL:', s=10), sg.InputText(data['gsheet_url'], k='gsheet_url', enable_events=True, expand_x=True)],
                   [sg.Text('JSON:', s=10), sg.InputText(data['json_file'], k='json_file', disabled=True, enable_events=True), sg.FileBrowse(k='fb', file_types=(("JSON Files", "*.json"),), disabled=True)],
                   [sg.Text('Pagina:', s=10), sg.InputCombo([data['gsheet_page']], default_value=data['gsheet_page'], k='gsheet_page', expand_x=True, disabled=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('VIDEO')],
                   [sg.Text('Carpeta:', s=10), sg.InputText(data['rec_folder_path'], k='rec_folder_path', expand_x=True, enable_events=True)],  #
                   [sg.Text('Tiempo max:', s=10), sg.InputText(data['max_time_recording'], k='max_time_recording', expand_x=True), sg.Checkbox('Grabar automaticamente', k='auto_record', default=data['auto_record'])],
                   [sg.Text('FPS:', s=10), sg.InputCombo([1, 12, 15, 24, 30, 60], default_value=data['fps'], k='fps', expand_x=True)],
                   [sg.Text('_' * 64)],
                   [sg.Text('BUSCADOR')],
                   [sg.Text('pagina(s):', s=10), sg.InputText(data['recording_urls'], k='recording_urls', expand_x=True)],
                   [sg.Button('Guardar', k='save', expand_x=True), sg.Button('Abrir Folder', k='open_folder')]]
        new_window(_title, _layout, finalize=True, **kwargs)

    def window_sequencer(**kwargs):
        _title = 'sequencer'
        SEQUENCER.window = new_window(_title, SEQUENCER.init_layout(), size=(400, 400), resizable=True, finalize=True, **kwargs)

    def window_sequencer_creator(**kwargs):
        _title = 'sequencer_creator'
        SEQUENCER_CREATOR.window = new_window(_title, SEQUENCER_CREATOR.init_layout(), size=(400, 400), finalize=True, **kwargs)

    def window_autoclick(**kwargs):
        _title = 'autoclick'
        AUTOCLICK.window = new_window(_title, AUTOCLICK.init_layout(), size=(220, 200), return_keyboard_events=True, finalize=True, **kwargs)

    def update_data(old_data: dict, new_data: dict):
        if old_data and new_data:
            for key in new_data.keys():
                if key in old_data:
                    old_data[key] = new_data[key]
            return True
        return False

    def in_urls(url_list):
        _current_url = BROWSER.get_current_page()
        if _current_url:
            _split_current_url = _current_url.split('/')[-1]
            if _split_current_url in url_list:
                return True
        else:
            RECORDER.stop_recording()

    def auto_record(time_out: int = 3):
        _time_out = time_out
        while True:
            time.sleep(2)
            if not DATA['auto_record']:
                continue
            search_url_list = [(url.split("/")[-1]) for url in list(DATA['recording_urls'].split(','))]
            if RECORDER.is_recording():
                if in_urls(search_url_list):
                    _time_out = time_out
                else:
                    if _time_out > 0:
                        _time_out -= 1
                        print(f'Waiting for teleop, time left:{_time_out}')
                        window_update_icon(r'images\tortoise_waiting.png')
                    else:
                        RECORDER.stop_recording()
                        window_update_icon(r'images\tortoise.png')
            else:
                if in_urls(search_url_list):
                    _time_out = time_out
                    folder = f'{DATE.day}-{DATE.month}-{DATE.year}'
                    os.makedirs(f'{DATA["rec_folder_path"]}/{folder}', exist_ok=True)
                    file_path = f'{folder}/{DATE.hour}-{DATE.minute}-{DATE.second}'
                    RECORDER.start_recording(file_path)
                    window_update_icon(r'images\tortoise_recording.png')

    def window_update_icon(img=r'images\tortoise.png'):
        MAIN_WINDOW.Element('main_image').Update(image_filename=resource_path(img))

    """
    Program =====================================================================================
    """
    # VARIABLES
    DATE = dt.now()
    DIR = user_data_dir('Utilities', 'Tortops', roaming=True)
    os.makedirs(DIR, exist_ok=True)
    WINDOWS = {}
    DATA = {
        'window_position': (200, 200),
        'teleop_name': 'Teleop',
        'gsheet_url': '',
        'json_file': DIR,
        'gsheet_page': '',
        'rec_folder_path': DIR,
        'fps': 15,
        'recording_urls': 'teleoperation',
        'auto_record': True,
        'max_time_recording': 120,
        'save_file': rf'{DIR}\config.json',
        'config_section': 'Config'
    }
    NEW_DATA = read_file(DATA['save_file'], DATA['config_section'])
    update_data(DATA, NEW_DATA)
    SCREEN_SIZE = sg.Window.get_screen_size()
    WINDOWS_NAMES = {
        'main_window': 'Main Window',
        'report_bug': 'Reportar error',
        'config': 'Configuracion',
        'autoclick': 'Auto Click',
        'sequencer': 'Sequencias',
        'sequencer_creator': 'Creador de sequencias'
    }
    EVENTS = {
        'report_bug': 'Reportar error',
        'auto_click': 'Auto click',
        'sequencer': 'Sequencias',
        'config': 'Configuracion',
        'separator_0': '---',
        'sequencer_creator': 'Crear sequencia',
        'stop_recording': 'Detener grabacion',
        'debug': 'Consola',
        'separator_1': '---',
        'exit': 'Salir'
    }
    EVENTS_MENU = list(EVENTS.values())
    # Init Autoclick
    AUTOCLICK = AutoClick()

    # init sequencer, sequencer_creator
    SEQUENCER = Sequencer(DATA['save_file'])
    SEQUENCER_CREATOR = SequencerCreator(DATA['save_file'])

    # Init Browser
    BROWSER = Browser()
    # Init Recorder
    RECORDER = Recorder(DATA['rec_folder_path'], DATA['fps'], int(DATA['max_time_recording']) * int(DATA['fps']) * 60)
    threading.Thread(target=auto_record, daemon=True).start()

    # MAIN WINDOW
    LAYOUT = [[sg.Button('', k='main_image', image_filename=resource_path('images/tortoise.png'), image_size=(50, 50), border_width=0, enable_events=True, button_color='white', right_click_menu=['&Right', EVENTS_MENU])]]
    MAIN_WINDOW = new_window('main_window',
                             LAYOUT,
                             location=DATA['window_position'],
                             size=(50, 50),
                             grab_anywhere=True,
                             keep_on_top=True,
                             alpha_channel=0.8,
                             no_titlebar=True,
                             transparent_color='white',
                             element_padding=0,
                             margins=(0, 0),
                             finalize=True)

    # GUI LOOP
    while True:
        try:
            window, event, values = sg.read_all_windows()
        except Exception as e:
            print(e)
            break
        # print(f'Window: {window.Title}, Event: {event}')
        if window.Title == WINDOWS_NAMES['main_window']:
            MAIN_WINDOW.move(SCREEN_SIZE[0] - 50, max(0, min(window.current_location()[1], SCREEN_SIZE[1] - 50)))
            if event == EVENTS['report_bug']:
                windows_bug()
            elif event == EVENTS['config']:
                windows_config(data=DATA)
            elif event == EVENTS['stop_recording']:
                RECORDER.stop_recording()
                window_update_icon('images/tortoise.png')
            elif event == EVENTS['debug']:
                print_window('[CONSOLA]')
            elif event == EVENTS['auto_click']:
                window_autoclick()
            elif event == EVENTS['sequencer']:
                window_sequencer()
                SEQUENCER.load_sequences()
            elif event == EVENTS['sequencer_creator']:
                window_sequencer_creator()
                SEQUENCER_CREATOR.load_sequences()
            elif event == sg.WINDOW_CLOSED or event == 'Quit' or event == EVENTS['exit']:
                save_file(DATA['save_file'], DATA['config_section'], {'window_position': window.current_location()})
                break

        elif window.Title == 'Debug Window':
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                window.close()

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
                    format_data = {'A': values['id'], 'D': values['error'], 'E': DATA['teleop_name'], 'F': date}
                    if g_sheet.send_report(DATA['gsheet_page'], format_data):
                        destroy_window('report_bug', window)

            elif event == sg.WINDOW_CLOSED:
                destroy_window('report_bug', window)

        elif window.Title == WINDOWS_NAMES['autoclick']:
            AUTOCLICK.run(event)
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                destroy_window('autoclick', window)

        elif window.Title == WINDOWS_NAMES['sequencer']:
            SEQUENCER.run(event, values)
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                destroy_window('sequencer', window)

        elif window.Title == WINDOWS_NAMES['sequencer_creator']:
            SEQUENCER_CREATOR.run(event, values)
            if event == sg.WINDOW_CLOSED or event == 'Quit':
                destroy_window('sequencer_creator', window)

    # Ensure all windows to close
    for name in WINDOWS:
        for win in WINDOWS[name]:
            win.close()


if __name__ == '__main__':
    main()
