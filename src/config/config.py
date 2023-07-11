import configparser
class Config:
    def __init__(self):
        super(Config, self).__init__()
        self.path = r'D:\PyCharmTest\PyCharmPackets\Models\StaticCodeAnalyzer\FastCodeReview\src\config\config.ini'

    def read_config(self):
        config = configparser.ConfigParser()
        config.read(self.path)
        return config