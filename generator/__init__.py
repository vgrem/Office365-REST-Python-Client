import os
from configparser import ConfigParser


def load_settings():
    cp = ConfigParser()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(root_dir, "settings.cfg")
    cp.read(config_file)
    return cp
