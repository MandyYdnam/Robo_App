import os
import logging


class FieldTypes:
    string = 1
    string_list = 2
    integer = 3
    boolean = 4
    decimal = 5
    dateTime = 6
    long_string = 7


class AppConfig:
    user_folder_path = os.path.join(os.path.expanduser("~"), "Robot_app")
    user_db_location = os.path.join(user_folder_path, "db")
    user_temp_location = os.path.join(user_folder_path, "temp")
    result_location = os.path.join(user_folder_path, "results")
    user_config_file = os.path.join(user_folder_path,'user_setting.ini')
    user_bookmarks_path = os.path.join(user_folder_path, "bookmarks")
    INI_APP_SETTING_SECTION = 'APP_SETTINGS'
    INI_PROJECT_LOCATION = 'project_location'
    SERVER_LIST = []
    BROWSER_LIST = []
    URL_LIST = []
    DEVICE_LIST = []
    USE_ALM = False
    ALM_URI = ""
    ROBOT_VERSION =''
    LOG_LEVEL = logging.INFO


class DatabaseConfig:
    sqllite_db_location  = os.path.join(AppConfig.user_db_location, "robo_executorData.db")
    db_user_name = ""
    db_user_password = ""
    db_connection_string = ""
    db_name = ""


class BatchStatus:
    NOT_RUNNING = "Not Running"
    RUNNING = "Running"
    PASSED = "Passed"
    FAIL = "Failed"
    STOPPED = 'Stopped'
    SKIPPED = 'SKIP'