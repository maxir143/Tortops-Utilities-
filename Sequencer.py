import PySimpleGUI as sg
from GPEmu import GamePad
from main import resource_path


class Sequencer:
    def __init__(self):
        self.window = None
        self.sequences = []

    def InitLayout(self):
        sequence_list = []
        table_headings = ['sequence', 'state', 'loop']
        _layout = [[sg.Titlebar('Sequencias', icon=resource_path('images/gamepad_ico.png'))],
                   [sg.DropDown(sequence_list, expand_x=True), sg.Checkbox('Loop', key='loop'), sg.Button('Comenzar', k='start', disabled=True)],
                   [sg.Table(self.sequences, headings=table_headings, expand_x=True, expand_y=True)],
                   [sg.Button('Detener/Continuar', k='stop', expand_x=True, disabled=True), sg.Button('Quitar', k='remove', disabled=True)]]
        return _layout

    def run(self, event):
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            self.window.close()
            self.window = None


class SequencerCreator:
    def __init__(self):
        self.window = None
        self.sequence_commands = []

    def InitLayout(self):
        command_list = list(GamePad().button_value)
        command_range = (0, 0)
        table_headings = ['command', 'value', 'sleep']

        _layout = [[sg.Titlebar('Creador de sequencias')],
                   [sg.Combo(command_list, k='command_list', expand_x=True, expand_y=False, enable_events=True, readonly=True), sg.Text('', k='s_text'),
                    sg.Slider(command_range, enable_events=True, orientation='h', disable_number_display=True, k='command_options')],
                   [sg.Text('Sleep(ms):'), sg.InputText('.01', k='sleep', size=4), sg.Button('Agregar', k='add', expand_x=True, disabled=True)],
                   [sg.Table(self.sequence_commands, k='sequence_commands', headings=table_headings, expand_x=True, expand_y=True)],
                   [sg.Button('Quitar', k='remove', disabled=True, expand_x=True)]]
        return _layout

    def update_element(self, k, **kwargs):
        self.window.Element(k).update(**kwargs)

    def run(self, event, values):
        if event == 'command_list':
            command_selected = values['command_list']
            self.update_element('s_text', value=0.0)
            self.update_element('add', disabled=False)
            if command_selected in list(GamePad().buttons):
                self.update_element('command_options', value=0, range=(0, 1), visible=True)
            elif command_selected in list(GamePad().triggers):
                self.update_element('command_options', value=0, range=(0, 100), visible=True)
            elif command_selected in list(GamePad().joysticks):
                self.update_element('command_options', value=0, range=(-50, 50), visible=True)
            else:
                self.update_element('add', disabled=True)
        elif event == 'add':
            self.sequence_commands.append([values['command_list'], values['command_options'], values['sleep']])
            self.update_element('sequence_commands', values=self.sequence_commands)

        elif event == 'command_options':
            self.update_element('s_text', value=values['command_options'])

        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            self.window.close()
            self.window = None
