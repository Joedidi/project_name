# -*- coding:UTF-8 -*-

import codecs
import yaml

configFile = "./config.yml"


class Config(object):
    def __init__(self):
        self.configFile = configFile
        self.load_config()

    def load_config(self):
        with codecs.open(self.configFile, 'r', encoding="utf-8") as f:
            self.conf = yaml.load(f)
        return self.conf


config = Config()
