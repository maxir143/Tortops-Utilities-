import PySimpleGUI as sg
from GPEmu import GamePad
from utilities import resource_path, save_file, read_file


class Sequencer:
    def __init__(self):
        self.window = None
        self.sequences = []

    def InitLayout(self):
        sequence_list = []
        table_headings = ['sequence', 'state', 'loop']
        _layout = [[sg.Titlebar('Sequencias', icon=resource_path(r'images\gamepad_ico.png'))],
                   [sg.DropDown(sequence_list, expand_x=True), sg.Checkbox('Loop', key='loop'), sg.Button('Comenzar', k='start', disabled=True)],
                   [sg.Table(self.sequences, headings=table_headings, expand_x=True, expand_y=True)],
                   [sg.Button('Detener/Continuar', k='stop', expand_x=True, disabled=True), sg.Button('Quitar', k='remove', disabled=True)]]
        return _layout

    def run(self, event):
        # TODO: read files
        # TODO: run files
        if event == sg.WINDOW_CLOSED or event == 'Quit':
            if self.window:
                self.window.close()
                self.window = None


class SequencerCreator:
    def __init__(self, file: str = None):
        self.window = None
        self.sequence_commands = []
        self.sequences = None
        self.file = file

    def InitLayout(self):
        command_list = list(GamePad().button_value)
        command_range = (0, 0)
        table_headings = ['command', 'value']

        _layout = [[sg.Titlebar('Creador de sequencias')],
                   [sg.Combo(command_list, k='command_list', expand_x=True, expand_y=False, enable_events=True, readonly=True),
                    sg.Text('0.0', auto_size_text=True, k='s_text'),
                    sg.Slider(command_range, s=(10, None), enable_events=True, orientation='h', disable_number_display=True, k='command_options')],
                   [sg.Button('Agregar Comando', k='add', expand_x=True, disabled=True),
                    sg.Text('Espera (ms):'), sg.Spin(list(range(5, 100, 5)), initial_value=5, readonly=True, k='sleep', size=4),
                    sg.Button('Agregar [Update]', k='add_update', disabled=True)],
                   [sg.Button('Quitar', k='remove', disabled=True, expand_x=True)],
                   [sg.InputText('', k='seq_name', s=20), sg.Button('Salvar', k='save', disabled=True, expand_x=True)],
                   [sg.Table(self.sequence_commands, k='sequence_commands', justification="center", enable_events=True, headings=table_headings, auto_size_columns=True, expand_x=True, expand_y=True)],
                   [sg.Combo([], k='loaded_sequences', enable_events=True, expand_x=True), sg.Button('Cargar', k='load')]]
        return _layout

    def load_sequences(self):
        if self.file:
            self.sequences = read_file(self.file, 'SEQUENCES')
            sequences_name = list(self.sequences.keys())
            if sequences_name:
                self.update_element('loaded_sequences', values=sequences_name)

    def update_element(self, e, **kwargs):
        self.window.Element(e).update(**kwargs)

    def update_table(self, values, index: int = 0):
        self.update_element('sequence_commands', values=values)
        if len(values) > index >= 0:
            self.update_element('sequence_commands', select_rows=[index])

    def update_buttons(self, buttons: list, value: bool):
        for b in buttons:
            self.update_element(b, disabled=value)

    def run(self, event, values):
        # print(event, values)
        if event == 'command_list':
            command_selected = values['command_list']
            self.update_element('s_text', value=0.0)
            self.update_buttons(['add'], False)
            if command_selected in list(GamePad().buttons):
                self.update_element('command_options', value=0, range=(0, 1), visible=True)
            elif command_selected in list(GamePad().triggers):
                self.update_element('command_options', value=0, range=(0, 100), visible=True)
            elif command_selected in list(GamePad().joysticks):
                self.update_element('command_options', value=0, range=(-50, 50), visible=True)
            else:
                self.update_buttons(['add', 'add_update', 'remove'], True)
        elif event == 'add':
            search = [command[0] for command in self.sequence_commands]
            if 'UPDATE' in search:
                for command in reversed(search):
                    if command == values['command_list']:
                        break
                    elif command == 'UPDATE':
                        self.sequence_commands.append([values['command_list'], values['command_options']])
                        break
            else:
                if values['command_list'] not in search:
                    self.sequence_commands.append([values['command_list'], values['command_options']])

            if len(self.sequence_commands) > 0:
                self.update_buttons(['add_update', 'remove', 'save'], False)
            self.update_table(self.sequence_commands, len(self.sequence_commands) - 1)

        elif event == 'add_update':
            search = [command[0] for command in self.sequence_commands]
            if 'UPDATE' in search:
                for index, command in enumerate(reversed(search)):
                    if command == 'UPDATE' and index == 0:
                        break
                    self.sequence_commands.append(['UPDATE', values['sleep']])
                    break
            else:
                self.sequence_commands.append(['UPDATE', values['sleep']])

            self.update_table(self.sequence_commands, len(self.sequence_commands) - 1)

        elif event == 'command_options':
            self.update_element('s_text', value=values['command_options'])

        elif event == 'remove':
            if values['sequence_commands']:
                rows = values['sequence_commands']
                for i in reversed(rows):
                    self.sequence_commands.pop(i)
                remain_rows = len(self.sequence_commands) - 1
                selected_row = remain_rows if remain_rows < rows[0] else rows[0]
                self.update_table(self.sequence_commands, selected_row)
            if len(self.sequence_commands) <= 0:
                self.update_buttons(['add_update', 'remove', 'save'], True)

        elif event == 'save':
            if self.file:
                name = values['seq_name']
                print(name)
                save_file(self.file, 'SEQUENCES', {name: self.sequence_commands})

        elif event == 'load':
            self.load_sequences()

        elif event == 'loaded_sequences':
            print(self.sequences)
            print(values['loaded_sequences'])
            if values['loaded_sequences'] in self.sequences.keys():
                self.sequence_commands = self.sequences[values['loaded_sequences']]
                self.update_table(self.sequence_commands, 0)

        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            if self.window:
                self.sequence_commands = []
                self.window.close()
                self.window = None
