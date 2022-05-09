import time
import PySimpleGUI as sg
from GPEmu import GamePad
from utilities import resource_path, save_file, read_file
import threading


class Sequencer:
    def __init__(self, file: str = None):
        self.window = None
        self.file = file
        self.sequences = []
        self.sequences_names = []
        self.sequences_table = []
        self.game_pad = GamePad()

    def init_layout(self):
        table_headings = ['sequence', 'state', 'loop']
        _layout = [[sg.Titlebar('Sequencias', icon=resource_path(r'images\gamepad_ico.png'))],
                   [sg.DropDown(self.sequences_names, k='sequence_list', expand_x=True), sg.Checkbox('Iniciar', key='auto_start'), sg.Checkbox('Infinito', key='loop'), sg.Button('Agregar', k='add', disabled=True)],
                   [sg.Button('Comenzar', k='start', disabled=True), sg.Button('Detener', k='stop', disabled=True), sg.Button('Quitar', k='remove', disabled=True)],
                   [sg.Table(self.sequences_table, k='sequences_table', headings=table_headings, expand_x=True, expand_y=True)]]
        return _layout

    def update_element(self, e, **kwargs):
        try:
            self.window.Element(e).update(**kwargs)
        except Exception as e:
            print(e)

    def load_sequences(self):
        if self.file:
            data = read_file(self.file)
            if 'SEQUENCES' not in data:
                return
            self.sequences = data['SEQUENCES']
            self.sequences_names = list(self.sequences.keys())
            if self.sequences_names:
                self.update_element('sequence_list', values=self.sequences_names, value=self.sequences_names[-1])
                self.update_element('add', disabled=False)

    def add_sequence(self, seq_name, seq_state, seq_loop):
        if self.get_sequence(seq_name):
            self.update_sequence(seq_name, seq_state, seq_loop)
        else:
            self.sequences_table.append([seq_name, seq_state, seq_loop])
            self.update_table()
        if seq_state is True:
            self.start_sequence(seq_name)

    def get_sequence(self, seq_name):
        for index, row_data in enumerate(self.sequences_table):
            if row_data[0] == seq_name:
                return row_data, index

    def update_sequence(self, seq_name, seq_state=None, seq_loop=None):
        old_data, index = self.get_sequence(seq_name)
        if old_data:
            self.sequences_table[index] = [seq_name, old_data[1] if seq_state is None else seq_state, old_data[2] if seq_loop is None else seq_loop]
            self.update_table()
            return True

    def start_sequence(self, seq_name):
        self.update_sequence(seq_name, seq_state=True)
        threading.Thread(target=lambda: self.run_sequence(seq_name)).start()

    def update_table(self):
        self.update_element('start', disabled=True)
        self.update_element('stop', disabled=True)
        self.update_element('remove', disabled=True)
        if self.sequences_table:
            self.update_element('start', disabled=False)
            self.update_element('stop', disabled=False)
            self.update_element('remove', disabled=False)
        self.update_element('sequences_table', values=self.sequences_table)

    def remove_sequence(self, seq_name):
        data, index = self.get_sequence(seq_name)
        if not data[1]:
            self.sequences_table.pop(index)
            print(self.sequences_table)
            self.update_table()

    def run_sequence(self, seq_name):
        gp = self.game_pad
        if not gp.gamepad():
            gp.connect()
            time.sleep(.1)
        seq = self.sequences[seq_name]
        for step in seq:
            if self.get_sequence(seq_name)[0][1] is False:
                break
            command = step[0]
            value = step[1]
            if command == 'UPDATE':
                gp.update()
                time.sleep(value / 100)
            elif command in gp.buttons:
                gp.button(command, value)
            elif command in gp.triggers:
                gp.set_trigger(command, value / 100)
            elif command in gp.joysticks_xy:
                gp.set_joystick_xy(command, value / 100)
        if self.get_sequence(seq_name)[0][2] is True:
            self.start_sequence(seq_name)
        self.update_sequence(seq_name, seq_state=False)
        for row in self.sequences_table:
            if row[1]:
                return
        gp.disconnect()

    def run(self, event, values):
        # print(event, values)
        if event == 'start':
            for seq in values['sequences_table']:
                self.start_sequence(self.sequences_table[seq][0])

        elif event == 'stop':
            for seq in values['sequences_table']:
                self.update_sequence(self.sequences_table[seq][0], seq_state=False)

        elif event == 'add':
            if values['sequences_table']:
                for seq in values['sequences_table']:
                    self.add_sequence(self.sequences_table[seq][0], values['auto_start'], values['loop'])
            else:
                self.add_sequence(values['sequence_list'], values['auto_start'], values['loop'])

        elif event == 'remove':
            for seq in values['sequences_table'][::-1]:
                self.remove_sequence(self.sequences_table[seq][0])

        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            if self.window:
                self.sequences_table = []
                self.window.close()
                self.window = None


class SequencerCreator:
    def __init__(self, file: str = None):
        self.window = None
        self.sequence_commands = []
        self.sequences = None
        self.file = file

    def init_layout(self):
        command_list = ['UPDATE'] + list(GamePad().buttons) + list(GamePad().triggers) + list(GamePad().joysticks_xy)
        command_range = (0, 0)
        table_headings = ['command', 'value']
        _layout = [[sg.Titlebar('Creador de sequencias')],
                   [sg.Combo(command_list, default_value=command_list[0], k='command_list', expand_x=True, expand_y=False, enable_events=True, readonly=True),
                    sg.Text('0.0', auto_size_text=True, k='s_text'),
                    sg.Slider(command_range, s=(10, None), enable_events=True, orientation='h', disable_number_display=True, k='command_options')],
                   [sg.Button('Agregar Comando', k='add', expand_x=True, disabled=True), sg.Button('Quitar', k='remove', disabled=True, s=15)],
                   [sg.Spin((100, 5, 50, 100, 200, 300, 400, 500), initial_value=5, readonly=True, k='sleep', size=4), sg.Text('ms')],
                   [sg.Table(self.sequence_commands, k='sequence_commands', justification="center", bind_return_key=True, headings=table_headings, auto_size_columns=True, expand_x=True, expand_y=True)],
                   [sg.Combo([], k='loaded_sequences', enable_events=True, expand_x=True), sg.Button('Salvar', k='save', disabled=True), sg.Button('Eliminar', k='delete'), sg.Button('Cargar', k='load')]]
        return _layout

    def load_sequences(self, seq_name: str = None):
        if self.file:
            self.sequences = read_file(self.file)
            if self.sequences:
                sequences_name = list(self.sequences.keys())
                if 'SEQUENCES' not in sequences_name:
                    return
                self.sequences = self.sequences['SEQUENCES']
                sequences_name = list(self.sequences.keys())
                if sequences_name:
                    def_seq = seq_name if seq_name in sequences_name else sequences_name[-1]
                    self.sequence_commands = self.sequences[def_seq] if def_seq in self.sequences else self.sequences[sequences_name[-1]]
                    self.update_element('loaded_sequences', values=sequences_name, value=def_seq)
                    self.update_buttons(['remove', 'add', 'save', 'sleep'], False)
                    self.update_table(self.sequence_commands, 0)

    def update_element(self, e, **kwargs):
        self.window.Element(e).update(**kwargs)

    def update_table(self, values, index: int = 0):
        self.update_element('sequence_commands', values=values)
        if len(values):
            index = max(min(index, len(values)), 0)
            self.update_element('sequence_commands', select_rows=[index])

    def update_buttons(self, buttons: list, value: bool):
        for b in buttons:
            self.update_element(b, disabled=value)

    def save_sequence(self, seq_name: str = None):
        seq_name = seq_name.lstrip()
        seq_name = seq_name.rstrip()
        seq_name = seq_name.replace(' ', '_')
        if seq_name == '':
            return
        save_file(self.file, 'SEQUENCES', {seq_name: self.sequence_commands})
        self.load_sequences(seq_name)

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
            elif command_selected in list(GamePad().joysticks_xy):
                self.update_element('command_options', value=0, range=(-100, 100), visible=True)
            elif command_selected == 'UPDATE':
                print('holi')
            else:
                self.update_buttons(['add', 'remove'], True)

        elif event == 'add':
            values['command_options'] = values['sleep'] if values['command_list'] == 'UPDATE' else values['command_options']
            pos = values['sequence_commands'][-1] + 1 if values['sequence_commands'] else 0
            last_pos = len(self.sequence_commands)
            select = last_pos
            if pos < last_pos:
                self.sequence_commands.insert(pos, [values['command_list'], values['command_options']])
                select = pos
            else:
                self.sequence_commands.append([values['command_list'], values['command_options']])
            if last_pos > 0:
                self.update_buttons(['remove', 'save'], False)
            self.update_table(self.sequence_commands, select)
            # TODO: smart command list selection
            #   if update then select last pressed button to release
            #   set and check for  common chain reaction keys
            self.update_element('command_list', value='UPDATE')

        elif event == 'command_options':
            self.update_element('s_text', value=values['command_options'])

        elif event == 'remove':
            if values['sequence_commands']:
                rows = values['sequence_commands']
                for i in reversed(rows):
                    self.sequence_commands.pop(i)
                remain_rows = len(self.sequence_commands) - 1
                selected_row = remain_rows if remain_rows < rows[0] else rows[0] - 1
                self.update_table(self.sequence_commands, selected_row)
            if len(self.sequence_commands) <= 0:
                self.update_buttons(['remove', 'save'], True)

        elif event == 'save':
            if self.file:
                self.save_sequence(values['loaded_sequences'])

        elif event == 'sequence_commands':
            if values['command_list'] and values['command_options']:
                self.sequence_commands[values['sequence_commands'][0]] = [values['command_list'], values['command_options']]
                self.update_table(self.sequence_commands, values['sequence_commands'][0])

        elif event == 'load':
            # TODO: cargar scripts de archivos externos y guardarlos a memoria interna
            pass
            # self.load_sequences()

        elif event == 'loaded_sequences':
            self.load_sequences(values['loaded_sequences'])

        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            if self.window:
                self.sequence_commands = []
                self.window.close()
                self.window = None
