import os
import sys
import json


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception as e:
        print(e)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def save_file(file: str = None, section: str = None, values: dict = None):
    if file is None or file is None or values is None:
        return
    data = read_file(file)
    if data:
        if section not in data:
            data[section] = {}
        for key, value in values.items():
            data[section][key] = value
    else:
        data = {section: values}
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def read_file(file: str, section: str = None):
    try:
        with open(file) as f:
            data = json.load(f)
            if section in data and section:
                return data[section]
            return data
    except Exception as e:
        print(e)
        return
