from configparser import ConfigParser
import json
from json import JSONDecodeError
from datetime import datetime


class AppConfigParser(ConfigParser):
    def __init__(self, file_name, *args, **kwargs):
        super(AppConfigParser, self).__init__(*args, **kwargs)
        self.file_name = file_name

    def readfile(self, encoding=None):
        return self.read(filenames=self.file_name, encoding=encoding)

    def writefile(self):
        with open(self.file_name, 'w') as file:
            self.write(file)

    def get_configuration_value(self, config_section, config_key):
        self.__readfile()
        if self.has_option(config_section, config_key):
            # return the Value
            return self[config_section][config_key]
        else:
            return None

    def add_configuration(self, config_section, config_key, config_value):
        self.__readfile()
        if not self.has_section(config_section):
            # add Section
            self.add_section(config_section)
        # else:
        self[config_section][config_key] = config_value
        self.writefile()

    def __readfile(self, encoding=None):
        return self.read(filenames=self.file_name, encoding=encoding)


class Bookmarks:
    def __init__(self, file):
        self.file = file

    def __get_json_as_dict(self):
        """Function to get bookmarks dict from json"""
        try:
            with open(self.file, 'r') as fp:
                return json.load(fp)
        except (JSONDecodeError, FileNotFoundError) as e:
            print(e)
            return {}

    def __dump_json(self, data_dict):
        with open(self.file, 'w') as fp:
            json.dump(data_dict, fp, indent=4, separators=(",", ":"))

    def update_bookmarks(self, data_dict):

        exiting_data = self.__get_json_as_dict()

        try:
            exiting_data.update(data_dict)
            self.__dump_json(exiting_data)
            return True
        except Exception as e:
            print(e)
            return False

    def get_bookmarks(self):
        try:
            return self.__get_json_as_dict()
        except JSONDecodeError:
            return {}


class RunTimeData(object):
    __instance = None
    __data = {}

    def __new__(cls):
        if RunTimeData.__instance is None:
            RunTimeData.__instance = object.__new__(cls)
        return RunTimeData.__instance

    def getdata(self, key, default=None):
        return RunTimeData.__data.get(key, default)

    def setdata(self, key, value):
        RunTimeData.__data[key] = value


def format_date(str_date, frmt='%Y-%m-%d'):
    '''Returns date as string in the desired format'''
    return datetime.strptime(str_date, frmt).strftime(frmt)


class FileNameNotFoundException(Exception):
    pass