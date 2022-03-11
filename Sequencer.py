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
        self.sequences_state = {}
        self.game_pad = GamePad()

    def init_layout(self):
        table_headings = ['sequence', 'state', 'loop']
        _layout = [[sg.Titlebar('Sequencias', icon=resource_path(r'images\gamepad_ico.png'))],
                   [sg.DropDown(self.sequences_names, k='sequence_list', expand_x=True), sg.Checkbox('Iniciar', key='auto_start'), sg.Checkbox('Infinito', key='loop'), sg.Button('Agregar', k='add', disabled=True)],
                   [sg.Button('Comenzar', k='start', disabled=True), sg.Button('Detener', k='stop', disabled=True)],
                   [sg.Table(self.sequences_table, k= 'sequences_running', headings=table_headings, expand_x=True, expand_y=True)],
                   [sg.Button('Detener/Continuar', k='stop', expand_x=True, disabled=True), sg.Button('Quitar', k='remove', disabled=True)]]
        return _layout

    def add_sequence(self, seq_name:str = None, state:bool = True, loop:bool = False):
        sequence = self.sequences[seq_name] if seq_name in self.sequences_names else None
        if seq_name in self.sequences_state or not sequence:
            return

        self.sequences_table.append([seq_name, state, loop])
        self.sequences_state[seq_name] = [state,loop]
        self.update_element('sequences_running', values=self.sequences_table)
        if self.sequences_table:
            self.update_element('start', disabled=False)
            self.update_element('stop', disabled=False)

        if state:
            threading.Thread(target=self.run_sequence, args=(sequence,seq_name)).start()

    def stop_sequence(self, seq_name):
        loop = self.sequences_state[seq_name][1]
        self.sequences_state[seq_name] = [False, loop]
        for i,v in enumerate(self.sequences_table):
            if v[0] == seq_name:
                self.sequences_table[i] = [seq_name, False, loop]
                break

        self.update_element('sequences_running', values=self.sequences_table)

    def delete_sequence(self, seq_name):
        self.update_element('sequences_running', values=self.sequences_table)

    def update_sequence(self, seq_name):
        self.update_element('sequences_running', values=self.sequences_table)

    def run_sequence(self, seq, seq_name):
        gp = self.game_pad
        if not gp.gamepad():
            gp.connect()
            time.sleep(.1)
        for step in seq:
            command = step[0]
            value = step[1]
            if command == 'UPDATE':
                gp.update()
                time.sleep(value/100)
            elif command in gp.buttons:
                gp.button(command, value)
            elif command in gp.triggers:
                gp.set_trigger(command, value/100)
            elif command in gp.joysticks_xy:
                gp.set_joystick_xy(command, value/100)
        state = self.sequences_state[seq_name][0]
        loop = self.sequences_state[seq_name][1]
        if state:
            if loop:
                self.run_sequence(seq, seq_name)
                return

        self.stop_sequence(seq_name)
        gp.disconnect()

    def update_element(self, e, **kwargs):
        self.window.Element(e).update(**kwargs)

    def load_sequences(self):
        if self.file:
            self.sequences = read_file(self.file, 'SEQUENCES')
            if self.sequences:
                self.sequences_names = list(self.sequences.keys())
                if self.sequences_names:
                    self.update_element('sequence_list', values=self.sequences_names, value=self.sequences_names[-1])
                    self.update_element('add', disabled=False)

    def run(self, event, values):
        print(event, values)
        if event == 'start':
            pass
        elif event == 'stop':
            if values['sequences_running']:
                print(self.sequences_table[values['sequences_running'][0]])
        elif event == 'add':
            self.add_sequence(values['sequence_list'], values['auto_start'], values['loop'])
        elif event == sg.WINDOW_CLOSED or event == 'Quit':
            if self.window:
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
                   [sg.Button('Agregar Comando', k='add', expand_x=True, disabled=True),  sg.Button('Quitar', k='remove', disabled=True, s=15)],
                   [sg.Spin((100, 5, 50, 100, 200, 300, 400, 500), initial_value=5, readonly=True, k='sleep', size=4), sg.Text('ms')],
                   [sg.Table(self.sequence_commands, k='sequence_commands', justification="center", bind_return_key=True, headings=table_headings, auto_size_columns=True, expand_x=True, expand_y=True)],
                   [sg.Combo([], k='loaded_sequences', enable_events=True, expand_x=True),sg.Button('Salvar', k='save', disabled=True), sg.Button('Eliminar', k='delete'), sg.Button('Cargar', k='load')]]
        return _layout

    def load_sequences(self, seq_name:str = None):
        if self.file:
            self.sequences = read_file(self.file, 'SEQUENCES')
            if self.sequences:
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
            index = max(min(index,len(values)),0)
            self.update_element('sequence_commands', select_rows=[index])

    def update_buttons(self, buttons: list, value: bool):
        for b in buttons:
            self.update_element(b, disabled=value)

    def save_sequence(self, seq_name: str = None):
        seq_name = seq_name.lstrip()
        seq_name = seq_name.rstrip()
        seq_name = seq_name.replace(' ', '_')
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
