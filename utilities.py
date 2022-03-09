import os
import sys
from configparser import ConfigParser


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def save_file(file: str = '', section: str = '', data: dict = None):
    if data is None or section == '':
        return
    config = ConfigParser()
    config.read(file)

    data = {v.strip():k for v,k in data.items()}
    data = {v.replace(' ', '-'):k for v, k in data.items()}

    print(f'data : {data}')

    if section not in config.sections():
        config.add_section(section)
    for key, value in data.items():
        config.set(section, key, str(value))
    with open(file, 'w') as f:
        config.write(f)
    return True


def read_file(file: str, section: str):
    if not os.path.exists(file):
        return False
    config = ConfigParser()
    config.read(file)
    sections = config.sections()
    if section in sections:
        return dict(config.items(section))
    elif sections is not []:
        values = []
        for s in sections:
            values.append(dict(config.items(s)))
        return values
