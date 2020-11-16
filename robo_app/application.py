import tkinter as tk
from tkinter import ttk, messagebox
from . import controller as c
from . import views as v
from .constants import AppConfig
from . import models as m
from .util import RunTimeData
import sys


class Application(tk.Tk):
    """Application Root Window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Robot Executor")
        self.batchmonitor = None
        self.create_batch = None
        self.stats = None
        # self.resizable(width=False, height=False)
        if sys.platform == 'linux':
            self.attributes('-zoomed', True)
        else:
            self.state('zoomed')
        # self.geometry("+%d+%d" % (100, 50))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        frm_options = ttk.Frame(self)
        frm_options.grid(row=0, sticky=tk.W)
        self.btn_create_batch = tk.Button(frm_options, text="Create Batch", command=self._activate_create_batch,
                                          relief=tk.RAISED)
        self.btn_create_batch.grid(row=0, column=0)
        self.btn_batch_monitor = tk.Button(frm_options, text="Batch Monitor", command=self._activate_batch_monitor,
                                           relief=tk.RAISED)
        self.btn_batch_monitor.grid(row=0, column=1)
        self.btn_stats = tk.Button(frm_options, text="Statistics", command=self._activate_stats,
                                   relief=tk.RAISED)
        self.btn_stats.grid(row=0, column=2)

        # ttk.Label(self, text="Developed By: Mandeep Dhiman",font=("TkDefaultFont", 8,'bold')).grid(row=2, column=0, sticky=tk.E)

        self.create_batch = c.CreateBatchController(self)
        self.create_batch.createbatch_view.grid(row=1, column=0, sticky=tk.NSEW)

        # Menu Settings variables and Call backs
        self.settings_model = m.SettingsModel()
        self.load_settings()
        # self.settings = {'use alm': tk.BooleanVar()} Now this is being created in  self.load_settngs() function
        self.callbacks = {'file->quit': self.quit,
                          'options->use_alm': self.callback_use_aml,
                          'options->preferences': self.callback_preference}
        # Creating Menu Object:
        menu = v.MainMenu(self, self.settings, self.callbacks)
        self.configure(menu=menu)
        if AppConfig.USE_ALM:
            self.alm_login_controller = c.ALMLoginController(self)
        'Update user information to the DB'
        m.InitializeModel(AppConfig.user_db_location).add_user_details(
            {'user_name': RunTimeData().getdata('alm_user', RunTimeData().getdata('system_user'))})

    def load_settings(self):
        '''Loads the settings into self.settings dict'''
        '''There is pusrpose of not using the () in the end to the tk variable because we will initialize it with the
        value coming from setting model. Look this line self.settings[key] = vartype(value=data['value']) and this 
        is similar to saying tk.BooleanVar(value=data['value'])'''
        vartypes = {'bool': tk.BooleanVar,
                    'str': tk.StringVar,
                    'int': tk.IntVar,
                    'float': tk.DoubleVar}
        self.settings = {}
        for key, data in self.settings_model.variables.items():
            vartype = vartypes.get(data['type'], tk.StringVar)
            self.settings[key] = vartype(value=data['value'])

        # Adding a Trace in the these variable so that if it changed in the UI so it can tracker
        for var in self.settings.values():
            var.trace('w', self.save_settings)
        self.load_configurations()

    def save_settings(self, *args):
        """Save the current settings to a preferences file"""
        for key, variable in self.settings.items():
            self.settings_model.set(key, variable.get())

        self.settings_model.save()

    def load_configurations(self):
        """Load the App config Object"""
        AppConfig.USE_ALM = self.settings['use alm'].get()
        AppConfig.ALM_URI = self.settings['alm_url'].get()
        AppConfig.BROWSER_LIST = self.settings['browser_list'].get().split('||')
        AppConfig.URL_LIST = self.settings['url_list'].get().split('||')
        AppConfig.DEVICE_LIST = self.settings['device_list'].get().split('||')
        AppConfig.SERVER_LIST = self.settings['device_Server_list'].get().split('||')

    def callback_use_aml(self):
        """show warning Dialouge"""
        about_message = 'Warning!!!!'
        about_details = ('Restart Required.\n'
                         'Please restart application for ALM Settings to take effect.')
        messagebox.showwarning(title='Warning!!!', message=about_message, detail=about_details)
        self.quit()

    def callback_preference(self):
        """Call back function for the Preferences"""
        v.Preferences(self, self.settings, {'preference->save': self.callback_save_preference})

    def callback_save_preference(self):
        """Load new configuration"""
        self.load_configurations()

    def _activate_create_batch(self):
        if self.create_batch is None:
            self.create_batch = c.CreateBatchController(self)
            self.create_batch.createbatch_view.grid(row=1, column=0, sticky=tk.NSEW)
        else:
            self.create_batch.createbatch_view.tkraise()

    def _activate_batch_monitor(self):
        if self.batchmonitor is None:
            self.batchmonitor = c.BatchMonitorController(self)
            self.batchmonitor.batch_monitor_view.grid(row=1, column=0, sticky=tk.NSEW)
        else:
            self.batchmonitor.batch_monitor_view.tkraise()

    def _activate_stats(self):
        if self.stats is None:
            self.stats = c.StatisticsController(self)
            self.stats.stats_view.grid(row=1, column=0, sticky=tk.NSEW)
        else:
            self.stats.stats_view.tkraise()
