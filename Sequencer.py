import PySimpleGUI as sg
from GPEmu import GamePad
from utilities import resource_path


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
            if self.window:
                self.window.close()
                self.window = None


class SequencerCreator:
    def __init__(self):
        self.window = None
        self.sequence_commands = []

    def InitLayout(self):
        command_list = list(GamePad().button_value)
        command_range = (0, 0)
        table_headings = ['command', 'value']

        _layout = [[sg.Titlebar('Creador de sequencias')],
                   [sg.Combo(command_list, k='command_list', expand_x=True, expand_y=False, enable_events=True, readonly=True),
                    sg.Text('0.0', auto_size_text=True, k='s_text'),
                    sg.Slider(command_range, s=(10, None), enable_events=True, orientation='h', disable_number_display=True, k='command_options')],

                   [sg.Button('Agregar', k='add', expand_x=True, disabled=True),
                    sg.Text('Sleep (ms):'), sg.Spin(list(range(5, 100, 5)), initial_value=5, readonly=True, k='sleep', size=4),
                    sg.Button('Agregar [Update]', k='add_update', disabled=True)
                    ],

                   [sg.Table(self.sequence_commands, k='sequence_commands', justification="center", enable_events=True, headings=table_headings, auto_size_columns=True, expand_x=True, expand_y=True)],

                   [sg.Button('Quitar', k='remove', disabled=True, expand_x=True)]]
        return _layout

    def update_element(self, k, **kwargs):
        self.window.Element(k).update(**kwargs)

    def update_table(self, values, index: int = 0):
        self.update_element('sequence_commands', values=values)
        if len(values) > index >= 0:
            self.update_element('sequence_commands', select_rows=[index])

    def run(self, event, values):
        # print(values)
        if event == 'command_list':
            command_selected = values['command_list']
            self.update_element('s_text', value=0.0)
            self.update_element('add', disabled=False)
            self.update_element('add_update', disabled=False)
            self.update_element('remove', disabled=False)
            if command_selected in list(GamePad().buttons):
                self.update_element('command_options', value=0, range=(0, 1), visible=True)
            elif command_selected in list(GamePad().triggers):
                self.update_element('command_options', value=0, range=(0, 100), visible=True)
            elif command_selected in list(GamePad().joysticks):
                self.update_element('command_options', value=0, range=(-50, 50), visible=True)
            else:
                self.update_element('add', disabled=True)
                self.update_element('add_update', disabled=True)
                self.update_element('remove', disabled=True)
        elif event == 'add':
            # checar si existe un <update>

            # si no existe un <update> ==> leer que el comando no este repetido

            # si existe un <update> ==> seleccionar la lista de comandos a partir del ultimo update que esiste

            # leer que el comando no este repetido


            self.sequence_commands.append([values['command_list'], values['command_options']])
            self.update_table(self.sequence_commands, len(self.sequence_commands) - 1)

        elif event == 'add_update':
            self.sequence_commands.append(['UPDATE', values['sleep']])
            self.update_table(self.sequence_commands, len(self.sequence_commands) - 1)

        elif event == 'command_options':
            self.update_element('s_text', value=values['command_options'])

        elif event == 'remove':
            if values['sequence_commands']:
                rows = values['sequence_commands']
                print(rows)
                for i in reversed(rows):
                    self.sequence_commands.pop(i)
                remain_rows = len(self.sequence_commands) - 1
                selected_row = remain_rows if remain_rows < rows[0] else rows[0]
                self.update_table(self.sequence_commands, selected_row)


        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            if self.window:
                self.sequence_commands = []
                self.window.close()
                self.window = None
