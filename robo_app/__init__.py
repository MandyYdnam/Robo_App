from .constants import AppConfig
from .models import InitializeModel
from .application import Application
import os

__version__ = "0.0.8"

# Making User files and directoies
if not os.path.exists(AppConfig.user_folder_path):
    os.mkdir(AppConfig.user_folder_path)

if not os.path.exists(AppConfig.user_db_location):
    os.mkdir(AppConfig.user_db_location)

# Creating INI file
if not os.path.exists(AppConfig.user_config_file):
    with open(AppConfig.user_config_file, 'a'):
        pass

# Create Tables
initialize_db_model = InitializeModel()
if not initialize_db_model.is_batch_table():
    print("initialize batch")
    initialize_db_model.cmd_create_batch_table()

if not initialize_db_model.is_script_table():
    print("initialize scripts")
    initialize_db_model.cmd_create_scripts_table()

if not initialize_db_model.is_command_var_table():
    print("initialize command")
    initialize_db_model.cmd_create_command_var_table()


def main():

    app = application.Application()
    app.mainloop()
