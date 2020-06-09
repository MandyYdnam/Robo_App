import tkinter as tk
from tkinter import ttk
from . import controller as c
from .constants import AppConfig
from . import models as m
from .util import RunTimeData


class Application(tk.Tk):
    """Application Root Window"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Robot Executor")
        self.batchmonitor = None
        self.create_batch = None
        self.stats = None
        # self.resizable(width=False, height=False)
        # self.geometry("+%d+%d" % (100, 50))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        frm_options = ttk.Frame(self)
        frm_options.grid(row=0, sticky=tk.W)
        self.btn_create_batch = tk.Button(frm_options, text="Create Batch", command=self._activate_create_batch, relief=tk.RAISED)
        self.btn_create_batch.grid(row=0, column=0)
        self.btn_batch_monitor = tk.Button(frm_options, text="Batch Monitor", command=self._activate_batch_monitor,relief=tk.RAISED)
        self.btn_batch_monitor.grid(row=0, column=1)
        self.btn_stats = tk.Button(frm_options, text="Stats", command=self._activate_stats,
                                           relief=tk.RAISED)
        self.btn_stats.grid(row=0, column=2)

        # ttk.Label(self, text="Developed By: Mandeep Dhiman",font=("TkDefaultFont", 8,'bold')).grid(row=2, column=0, sticky=tk.E)

        self.create_batch = c.CreateBatchController(self)
        self.create_batch.createbatch_view.grid(row=1, column=0, sticky=tk.NSEW)

        if AppConfig.USE_ALM:
            self.alm_login_controller = c.ALMLoginController(self)
        'Update user information to the DB'
        m.InitializeModel(AppConfig.user_db_location).add_user_details(
            {'user_name': RunTimeData().getdata('alm_user', RunTimeData().getdata('system_user'))})

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



