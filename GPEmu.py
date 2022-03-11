import vgamepad as vg
import time


class GamePad:
    def __init__(self):
        self.GAMEPAD = None
        self.button_value = {
            'A': 0,
            'B': 0,
            'X': 0,
            'Y': 0,
            'UP': 0,
            'DOWN': 0,
            'LEFT': 0,
            'RIGHT': 0,
            'LS': 0,
            'RS': 0,
            'RTHUM': 0,
            'LTHUM': 0,
            'START': 0,
            'BACK': 0,
            'HOME': 0,
            'LT': 0.0,
            'RT': 0.0,
            'LJ': {'x': 0.0, 'y': 0.0},
            'RJ': {'x': 0.0, 'y': 0.0}
        }
        self.buttons = {
            'A': 0x1000,
            'B': 0x2000,
            'X': 0x4000,
            'Y': 0x8000,
            'UP': 0x0001,
            'DOWN': 0x0002,
            'LEFT': 0x0004,
            'RIGHT': 0x0008,
            'LS': 0x0100,
            'RS': 0x0200,
            'RTHUM': 0x0080,
            'LTHUM': 0x0040,
            'START': 0x0010,
            'BACK': 0x0020,
            'HOME': 0x0400
        }
        self.triggers = ('RT', 'LT')
        self.joysticks = ('RJ', 'LJ')
        self.joysticks_xy = ('RJ_X', 'LJ_X', 'RJ_Y', 'LJ_Y')

    def connect(self):
        self.GAMEPAD = vg.VX360Gamepad()

    def disconnect(self):
        self.GAMEPAD = None

    def gamepad(self):
        return self.GAMEPAD

    def update(self, wait: float = 0.001):
        if self.gamepad():
            # print('update')
            time.sleep(wait)
            self.GAMEPAD.update()

    def press_button(self, btn: str, update=True):
        if self.gamepad():
            # print(f'{btn} pressed')
            self.save_value(btn, 1)
            self.GAMEPAD.press_button(self.buttons[btn])
            if update:
                self.update()

    def release_button(self, btn: str, update=True):
        if self.gamepad():
            # print(f'{btn} release')
            self.save_value(btn, 0)
            self.GAMEPAD.release_button(self.buttons[btn])
            if update:
                self.update()

    def button(self, btn: str, value: bool, update=True):
        if self.gamepad():
            if value:
                self.press_button(btn, update)
            else:
                self.release_button(btn, update)

    def set_trigger(self, trigger: str, value=0.0, update=True):
        if self.gamepad():
            # print(f'{trigger} set to {value}')
            self.save_value(trigger, value)
            if trigger == 'RT':
                self.GAMEPAD.right_trigger_float(value)
            elif trigger == 'LT':
                self.GAMEPAD.left_trigger_float(value)
            if update:
                self.update()

    def set_joystick(self, stick: str, x: float = None, y: float = None, update=True):
        if self.gamepad():
            if x is None:
                x = self.get_value(stick)['x']
            if y is None:
                y = self.get_value(stick)['y']
            self.save_value(stick, {'x': x, 'y': y})
            # print(f'{stick} set to {x}:{y}')
            if stick == 'LJ':
                self.GAMEPAD.left_joystick_float(float(x), float(y))
            elif stick == 'RJ':
                self.GAMEPAD.right_joystick_float(float(x), float(y))
            if update:
                self.update()

    def set_joystick_xy(self, stick: str, value: bool, update=True):
        stick_parent = None
        if not self.gamepad():
            return
        if stick == 'RJ_X' or stick == 'RJ_Y':
            stick_parent = 'RJ'
        elif stick == 'LJ_X' or stick == 'LJ_Y':
            stick_parent = 'LJ'
        if not stick_parent:
            return
        x,y = self.get_value(stick_parent).values()
        if stick == 'RJ_X':
            self.GAMEPAD.right_joystick_float(float(value), float(y))
            x = value
        elif stick == 'RJ_Y':
            self.GAMEPAD.right_joystick_float(float(x), float(value))
            y = value
        elif stick == 'LJ_X':
            self.GAMEPAD.left_joystick_float(float(value), float(y))
            x = value
        elif stick == 'LJ_Y':
            self.GAMEPAD.left_joystick_float(float(x), float(value))
            y = value
        # print(f'{stick} x,y set to {x}, {y}')
        self.save_value(stick_parent, {'x': x, 'y': y})
        if update:
            self.update()

    def save_value(self, btn: str, data: [int, list]):
        self.button_value[btn] = data

    def get_value(self, btn: str):
        return self.button_value[btn]

    def reset(self):
        self.GAMEPAD.reset()
        self.update()
