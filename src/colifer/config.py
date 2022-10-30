import errno
import os

import yaml


class Config:

    def __init__(self):
        super().__init__()
        config_yaml_stream = open('configs/colifer.yaml', "r")
        self.entries = yaml.safe_load(config_yaml_stream)

    @staticmethod
    def get_param_recursive(entry, elements):
        if len(elements) > 0 and type(entry) is dict:
            return Config.get_param_recursive(entry[elements[0]], elements[1:])
        else:
            return entry

    def get_param(self, path):
        elements = path.split('.')
        return Config.get_param_recursive(self.entries, elements)

    @staticmethod
    def get_section_param(section_entries, path):
        elements = path.split('.')
        return Config.get_param_recursive(section_entries, elements)

    @staticmethod
    def make_dir(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise
