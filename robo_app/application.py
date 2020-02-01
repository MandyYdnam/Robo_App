import tkinter as tk
from tkinter import ttk
from . import controller as c
from .constants import AppConfig


class Application(tk.Tk):
    """Application Root Window"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Robot Executor")
        self.batchmonitor = None
        self.create_batch = None
        self.resizable(width=False, height=False)
        self.geometry("+%d+%d" % (100, 50))
        # ttk.Label(self, text="Create Batch", font=("TkDefaultFont", 16)).grid(row=0)
        frm_options = ttk.Frame(self)
        frm_options.grid(row=0, sticky=tk.W)
        self.btn_create_batch = tk.Button(frm_options, text="Create Batch", command=self._activate_create_batch, relief=tk.RAISED)
        self.btn_create_batch.grid(row=0, column=0)
        self.btn_batch_monitor = tk.Button(frm_options, text="Batch Monitor", command=self._activate_batch_monitor,relief=tk.RAISED)
        self.btn_batch_monitor.grid(row=0, column=1)
        ttk.Label(self, text="Developed By: Mandeep Dhiman",font=("TkDefaultFont", 8,'bold')).grid(row=2, column=0, sticky=tk.E)

        self.create_batch = c.CreateBatchController(self)
        self.create_batch.createbatch_view.grid(row=1, column=0)

        if AppConfig.USE_ALM:
            self.alm_login_controller = c.ALMLoginController(self)

    def _activate_create_batch(self):
        if self.create_batch is None:
            self.create_batch = c.CreateBatchController(self)
        if self.batchmonitor is not None:
            self.batchmonitor.batch_monitor_view.grid_remove()
        self.create_batch.createbatch_view.grid(row=1, column=0)

    def _activate_batch_monitor(self):
        if self.batchmonitor is None:
            self.batchmonitor = c.BatchMonitorController(self)
        else:
            self.batchmonitor.populate_batch_data()
        if self.create_batch is not None:
            self.create_batch.createbatch_view.grid_remove()
        self.batchmonitor.batch_monitor_view.grid(row=1, column=0)

