import os

class FieldTypes:
    string = 1
    string_list = 2
    integer = 3
    boolean = 4
    decimal = 5
    dateTime = 6
    long_string = 7

class AppConfig:
    user_folder_path = os.path.join(os.environ['USERPROFILE'], "Robot_app")
    user_db_location = os.path.join(user_folder_path, "db")
    user_temp_location = os.path.join(user_folder_path, "temp")
    result_location = os.path.join(user_folder_path, "results")
    user_config_file = os.path.join(user_folder_path,'user_setting.ini')
    user_bookmarks_path = os.path.join(user_folder_path, "bookmarks")
    INI_APP_SETTING_SECTION = 'APP_SETTINGS'
    INI_PROJECT_LOCATION = 'project_location'
    SERVER_LIST = ["Server1"
            , "Server2"
            , "Server3"]
    ALM_URI = "enter your alm url"
    BROWSER_LIST = ['Chrome','Safari', 'Firefox', 'IE']
    URL_LIST = ['URL1',
                'URL2']
    DEVICE_LIST = ['DUMMYDEVICE1', 'DUMMYDEVICE2']

class DatabaseConfig:
    sqllite_db_location  = os.path.join(AppConfig.user_db_location, "robo_executorData.db")
    db_user_name = ""
    db_user_password = ""
    db_connection_string = ""
    db_name=""

