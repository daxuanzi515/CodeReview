import configparser
import os


class Config:
    def __init__(self):
        super(Config, self).__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path = os.path.join(script_dir, 'config.ini')
    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        return config