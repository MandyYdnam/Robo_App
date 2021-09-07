import tkinter as tk
from tkinter import ttk
from . import widgets as w
from . import constants as c
import os
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from .util import FileNameNotFoundException
from datetime import datetime
import robo_app


class CreateBatchForm(tk.Frame):
    """The input form for the Batch Widgets"""

    def __init__(self, parent, callbacks, fields=None, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)
        # Dictionary to keep tracK of input Widgets

        self.inputs = {}
        self.callbacks = callbacks
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        ########################
        # Project Information Frame
        #######################
        frame_projectinfo = tk.LabelFrame(self, text="Project Information")

        self.inputs['txb_ProjectLocation'] = w.LabelInput(frame_projectinfo, "Project Location:",
                                                          input_class=w.ValidEntry,
                                                          input_var=tk.StringVar(),
                                                          input_arg={'state': 'readonly'})

        self.inputs['txb_ProjectLocation'].grid(row=0, column=0, sticky=tk.NSEW)
        self.inputs['btn_projLocation'] = w.LabelInput(frame_projectinfo, "Browse", input_class=ttk.Button,
                                                       input_var=tk.StringVar()
                                                       , input_arg={
                'command': lambda: self.select_folder('txb_ProjectLocation')})
        self.inputs['btn_projLocation'].grid(row=0, column=1, pady=20, sticky=tk.NS)

        self.inputs['tbx_resultLocation'] = w.LabelInput(frame_projectinfo, "Results Location:",
                                                         input_class=w.ValidEntry,
                                                         input_var=tk.StringVar(),
                                                         input_arg={'state': 'readonly'})

        self.inputs['tbx_resultLocation'].variable.set(c.AppConfig.result_location)
        self.inputs['tbx_resultLocation'].grid(row=1, column=0, sticky=tk.NSEW)
        # frame_projectinfo.grid(row=0, sticky=(tk.W + tk.E), padx=10, pady=2)  # Display Project Info Frame
        frame_projectinfo.grid(row=0, sticky=tk.NSEW, padx=10, pady=2)  # Display Project Info Frame
        frame_projectinfo.columnconfigure(0, weight=1)

        ########################
        # Search Scripts Frame
        #######################

        self.inputs['frm_searchscripts'] = tk.LabelFrame(self, text="Search Scripts")

        # Adding the Folder Structure
        self.inputs['FolderStructure'] = w.FolderTreeView(self.inputs['frm_searchscripts'])

        self.inputs['FolderStructure'].grid(row=0, column=0, sticky=tk.NSEW)

        # Adding the Search Button
        self.inputs['SearchBtn'] = w.LabelInput(self.inputs['frm_searchscripts'], "Search", input_class=ttk.Button,
                                                input_var=tk.StringVar(),
                                                input_arg={'command': self.callbacks['SearchBtn']})
        self.inputs['SearchBtn'].grid(row=1, column=0, sticky=(tk.N + tk.E + tk.W))

        # Adding Tags Box
        self.inputs['cb_tags'] = w.LabelInput(self.inputs['frm_searchscripts'], "", input_class=ttk.Combobox,
                                              input_var=tk.StringVar())
        self.inputs['cb_tags'].grid(row=1, column=1)

        # Adding DataTable For Searched Scripts

        self.inputs['SearchScripts'] = w.TabularTreeView(self.inputs['frm_searchscripts'],
                                                         ('Name',
                                                          'Documentation'
                                                          , 'Tags'
                                                          , 'Suite'))
        self.inputs['SearchScripts'].set_column_width('Name', 400)

        self.inputs['SearchScripts'].grid(row=0, column=1, sticky=tk.NSEW)

        # Adding the Search Button
        self.inputs['AddSelectedBtn'] = w.LabelInput(self.inputs['frm_searchscripts'], "Add Selected"
                                                     , input_class=ttk.Button
                                                     , input_var=tk.StringVar()
                                                     , input_arg={'command': self.callbacks['AddSelected']})

        self.inputs['AddSelectedBtn'].grid(row=0, column=2)
        # self.inputs['frm_searchscripts'].grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=2)  # Display the Search Frame
        self.inputs['frm_searchscripts'].grid(row=1, padx=10, pady=2, sticky=tk.NSEW)  # Display the Search Frame
        self.inputs['frm_searchscripts'].columnconfigure(0, weight=1)
        self.inputs['frm_searchscripts'].columnconfigure(1, weight=3)
        ########################
        # Batch Frame
        #######################
        self.inputs['frm_cb_batchscripts'] = tk.LabelFrame(self, text="Batch")

        # Adding load from Book Marks Checkbox
        self.inputs['ckb_loadfrombookMark'] = w.LabelInput(self.inputs['frm_cb_batchscripts'],
                                                           label='Load from Bookmark'
                                                           , input_class=ttk.Checkbutton, input_var=tk.IntVar()
                                                           , input_arg={'command': self.cmd_load_from_bookmark})
        self.inputs['ckb_loadfrombookMark'].variable.set(0)
        self.inputs['ckb_loadfrombookMark'].grid(row=0)

        # Adding Book Maks Comobox

        self.inputs['cb_bookMark'] = w.LabelInput(self.inputs['frm_cb_batchscripts'], label='',
                                                  input_class=ttk.Combobox,
                                                  input_var=tk.StringVar(),
                                                  input_arg={'state': "readonly"}
                                                  )
        self.inputs['cb_bookMark'].variable.set("Select Bookmark")

        self.inputs['cb_bookMark'].bind("<<ComboboxSelected>>", self.__on_combobox_selected)
        # Adding DataTable For BAtch Scripts
        self.inputs['trv_batchScripts'] = w.TabularTreeView(self.inputs['frm_cb_batchscripts'],
                                                            ('Name', 'Documentation', 'Tags', 'Suite'))
        self.inputs['trv_batchScripts'].set_column_width('Name', 500)
        self.inputs['trv_batchScripts'].set_column_width('Suite', 320)
        self.inputs['trv_batchScripts'].grid(row=1, column=0, sticky=tk.NSEW)

        # Adding the Remove Button
        self.inputs['btn_removeSelected'] = w.LabelInput(self.inputs['frm_cb_batchscripts'], "Remove Selected",
                                                         input_class=ttk.Button,
                                                         input_var=tk.StringVar(),
                                                         input_arg={'command': self.remove_test_from_batch})
        self.inputs['btn_removeSelected'].grid(row=1, column=1, sticky=tk.E)

        # Adding the Create Batch Button
        frm_bottom_btns = ttk.Frame(self.inputs['frm_cb_batchscripts'])
        frm_bottom_btns.grid(row=3, sticky=tk.W)

        self.inputs['btn_createBatch'] = w.LabelInput(frm_bottom_btns, "Create Batch",
                                                      input_class=ttk.Button,
                                                      input_var=tk.StringVar(),
                                                      input_arg={'command': self.callbacks['btn_createBatch']}
                                                      )

        self.inputs['btn_createBatch'].grid(row=0, column=0)

        # Adding the Create BookMark Button
        self.inputs['btn_createBookmark'] = w.LabelInput(frm_bottom_btns, "Create Bookmark",
                                                         input_class=ttk.Button,
                                                         input_var=tk.StringVar(),
                                                         input_arg={'command': self.callbacks['btn_createBookmark']}
                                                         )

        self.inputs['btn_createBookmark'].grid(row=0, column=1)

        # self.inputs['frm_cb_batchscripts'].grid(row=3, sticky=(tk.W + tk.E), padx=10,
        #                                         pady=2)  # Display the Search Frame

        self.inputs['frm_cb_batchscripts'].grid(row=3, padx=10, sticky=tk.NSEW,
                                                pady=2)  # Display the Search Frame
        self.inputs['frm_cb_batchscripts'].columnconfigure(0, weight=1)
        self.inputs['frm_cb_batchscripts'].rowconfigure(1, weight=1)

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            # print(widget.widgetName)
            if widget.widgetName in ('labelframe',):
                pass
            # elif hasattr(widget,'tree') and 'foldertreeview'in str(widget).split('!'):
            #     data[key] = widget.get_selected_item_path()
            # elif hasattr(widget, 'tree') and 'tabulartreeview' in str(widget).split('!'):
            #     data[key] = widget.get_selected_items()
            else:
                data[key] = widget.get()
        return data

    def reset(self):
        for widget in self.inputs.values():
            widget.set('')

    def populate_data(self, proj_location, bm_list, tags):
        # print("tags", tags)
        self.inputs['txb_ProjectLocation'].variable.set(proj_location)
        self.inputs['cb_bookMark'].set(bm_list)
        self.inputs['cb_tags'].set(tags)
        self.inputs['FolderStructure'].update_tree(proj_location,
                                                   sfilter=['.git', '.settings', 'libspecs', '__pycache__',
                                                            '.png'])
        self.inputs['SearchScripts'].clear_items()
        self.inputs['trv_batchScripts'].clear_items()

    def __on_combobox_selected(self, *args):
        self.callbacks['cb_bookMark'](self.inputs['cb_bookMark'].get())

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors

    def select_folder(self, entry_name):
        """command to Browser the Folder Structure"""
        folder_selected = filedialog.askdirectory()
        if folder_selected != '':
            self.inputs[entry_name].variable.set(folder_selected)
            self.inputs['FolderStructure'].update_tree(folder_selected,
                                                       sfilter=['.git', '.settings', 'libspecs', '__pycache__',
                                                                '.png'])

            self.callbacks['btn_projLocation'](folder_selected)

    def populate_scripts_table(self, test_list):
        """Function to populate Scripts Table for the Searched Scripts"""
        self.inputs['SearchScripts'].clear_items()
        for test in test_list:
            self.inputs['SearchScripts'].insert_item(test, values=(test.name
                                                                   , test.doc
                                                                   , test.tags
                                                                   , test.source))

    def populate_scripts_table2(self, test_list):
        """Function to populate Scripts Table for the Searched Scripts"""
        self.inputs['SearchScripts'].clear_items()
        for test in test_list:
            self.inputs['SearchScripts'].insert_item(test, values=(test['name']
                                                                   , test['doc']
                                                                   , test['tags']
                                                                   , test['source']))

    def get_selected_folder_path(self):
        return self.inputs['FolderStructure'].get_selected_item_path()

    def get_tags(self):
        return self.inputs['cb_tags'].get()

    def get_selected_search_tests(self):
        """Function to Return Selected Tests"""
        return self.inputs['SearchScripts'].get_selected_items()

    def get_batch_tests(self):
        """Funtion will return all the items from batch Scripts Tree View"""
        return self.inputs['trv_batchScripts'].get_items()

    def insert_tests_to_batch(self, test_list):
        for test in test_list:
            self.inputs['trv_batchScripts'].insert_item(test, allow_duplicates=False, values=(test.name
                                                                                              , test.doc
                                                                                              , test.tags
                                                                                              , test.source))

    def insert_tests_to_batch2(self, test_list):
        """Takes Test as List of Dict"""
        for test in test_list:
            self.inputs['trv_batchScripts'].insert_item(test, allow_duplicates=False, values=(test['name']
                                                                                              , test['doc']
                                                                                              , test['tags']
                                                                                              , test['source']))

    def remove_test_from_batch(self):
        """function to Remove Test Case From Batch """
        self.inputs['trv_batchScripts'].delete_selected_item()

    def cmd_select_application_type(self):
        if self.inputs['rb_applicationTypeWeb'].variable.get() == 'Mobile':
            self.inputs['lstbx_browser'].grid_remove()
            self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)
            self.inputs['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['frame_url_details'].grid_remove()

        else:
            self.inputs['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_device'].grid_remove()
            self.inputs['lstbx_browser'].grid(row=0, column=0, padx=10)
            self.inputs['frame_mc_details'].grid_remove()

    def cmd_load_from_bookmark(self):
        if self.inputs['ckb_loadfrombookMark'].variable.get() == 1:
            self.callbacks['ckb_loadfrombookMark']()
            self.inputs['cb_bookMark'].grid(row=0, column=0, sticky=tk.E)

        else:
            self.inputs['cb_bookMark'].grid_remove()

    def load_device_list(self, device_list):
        device_list = device_list if device_list else []
        self.inputs['lstbx_device'].variable.set(device_list)


class CreateBatchDetailsForm(tk.Frame):

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.inputs = {}
        self.callbacks = callbacks
        #############################
        # Create a top Level window
        ############################
        win_batchdetails = tk.Toplevel(self)
        self.win_batchdetails = win_batchdetails
        # self.inputs['win_batchdetails'] = win_batchdetails
        win_batchdetails.title = "Create Batch"
        win_batchdetails.lift()
        win_batchdetails.grab_set()
        win_batchdetails.geometry('%dx%d+%d+%d' % (600, 850, self.winfo_rootx(), self.winfo_rooty()))
        win_batchdetails.resizable(width=False, height=False)
        win_batchdetails.columnconfigure(0, weight=1)
        ttk.Label(win_batchdetails, text="Enter the batch details", font=("TkDefaultFont", 16)).grid(row=0)

        #############################
        # Create a Batch Info Frame
        ############################
        frame_batch_info = tk.LabelFrame(win_batchdetails, text="Batch Information")
        frame_batch_info.grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=10)
        frame_batch_info.columnconfigure(0, weight=1)
        self.inputs['txb_batchName'] = w.LabelInput(frame_batch_info, "Name:", input_class=w.ValidEntry,
                                                    input_var=tk.StringVar())
        self.inputs['txb_batchName'].columnconfigure(0, weight=1)
        self.inputs['txb_batchName'].grid(row=0, column=0)

        self.inputs['txb_batchNumberOfThreads'] = w.LabelInput(frame_batch_info, "Number of Processes:",
                                                               input_class=w.ValidSpinbox,
                                                               input_var=tk.StringVar(),
                                                               input_arg={"from_": '1', "to": '4', "increment": '1'})
        self.inputs['txb_batchNumberOfThreads'].grid(row=0, column=1)

        #############################
        # Create a Application Type Frame
        ############################
        frame_application_type = tk.LabelFrame(win_batchdetails, text="Application Type & Language")
        frame_application_type.grid(row=3, sticky=(tk.W + tk.E), padx=10, pady=10)
        # frame_application_type.columnconfigure(4, weight=1)

        self.inputs['rb_applicationTypeWeb'] = w.LabelInput(frame_application_type, "Web",
                                                            input_class=ttk.Radiobutton,
                                                            input_var=tk.StringVar()
                                                            , input_arg={"value": "Web",
                                                                         'command': self.cmd_select_application_type})
        self.inputs['rb_applicationTypeWeb'].grid(row=0, column=2)

        self.inputs['rb_applicationTypeMobile'] = w.LabelInput(frame_application_type, "Mobile",
                                                               input_class=ttk.Radiobutton,
                                                               input_var=self.inputs['rb_applicationTypeWeb'].variable,
                                                               input_arg={"value": "Mobile",
                                                                          'command': self.cmd_select_application_type})
        self.inputs['rb_applicationTypeMobile'].grid(row=0, column=1)

        self.inputs['rb_applicationTypeOthers'] = w.LabelInput(frame_application_type, "Others",
                                                               input_class=ttk.Radiobutton,
                                                               input_var=self.inputs['rb_applicationTypeWeb'].variable,
                                                               input_arg={"value": "Others",
                                                                          'command': self.cmd_select_application_type})
        self.inputs['rb_applicationTypeOthers'].grid(row=0, column=0)


        self.inputs['rb_application_lang_FR'] = w.LabelInput(frame_application_type, "FR",
                                                             input_class=ttk.Radiobutton,
                                                             input_var=tk.StringVar()
                                                             , input_arg={"value": "FR"})
        self.inputs['rb_application_lang_FR'].grid(row=1, column=1)

        self.inputs['rb_application_lang_EN'] = w.LabelInput(frame_application_type, "EN",
                                                             input_class=ttk.Radiobutton,
                                                             input_var=self.inputs['rb_application_lang_FR'].variable,
                                                             input_arg={"value": "EN"})
        self.inputs['rb_application_lang_EN'].grid(row=1, column=0)

        #############################
        # Create a Select Device/Browser Type Frame
        ############################
        self.inputs['frame_device_browser'] = tk.LabelFrame(win_batchdetails, text="Select Device / Browser ")
        # self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['frame_device_browser'].columnconfigure(0, weight=1)
        self.inputs['lstbx_device'] = w.LabelInput(self.inputs['frame_device_browser'], "Device List", input_class=tk.Listbox
                                                   , input_var=tk.StringVar(), input_arg={"selectmode": "multiple",
                                                                                          'exportselection': 0})
        # self.inputs['lstbx_device'].variable.set(self._load_device_list())

        self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)

        self.inputs['lstbx_browser'] = w.LabelInput(self.inputs['frame_device_browser'], "Internet Explorer", input_class=tk.Listbox
                                                    , input_var=tk.StringVar(), input_arg={"selectmode": "multiple",
                                                                                           'exportselection': 0})
        self.inputs['lstbx_browser'].variable.set(c.AppConfig.BROWSER_LIST)

        #####################################
        # Mobile Center Detials
        #####################################
        self.inputs['frame_mc_details'] = tk.LabelFrame(win_batchdetails, text="Mobile Server Details")
        self.inputs['frame_mc_details'].columnconfigure(0, weight=1)
        self.inputs['frame_mc_details'].columnconfigure(1, weight=1)
        # self.inputs['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['lstbx_mobile_center'] = w.LabelInput(self.inputs['frame_mc_details'], "Select Server:"
                                                          , input_class=ttk.Combobox
                                                          , input_var=tk.StringVar(),
                                                          input_arg={'values': c.AppConfig.SERVER_LIST})

        # self.inputs['lstbx_mobile_center'].columnconfigure(0, weight=1)
        self.inputs['lstbx_mobile_center'].grid(row=0, column=0, padx=10, columnspan=2)

        self.inputs['txb_mc_user_name'] = w.LabelInput(self.inputs['frame_mc_details'], "User Name:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar())

        self.inputs['txb_mc_user_name'].grid(row=1, column=0, padx=10)

        self.inputs['txb_mc_user_pass'] = w.LabelInput(self.inputs['frame_mc_details'], "User Password:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar(),
                                                       input_arg={'show': '*'})
        self.inputs['txb_mc_user_pass'].grid(row=1, column=1, padx=10)

        #####################################
        # URL Detials
        #####################################
        self.inputs['frame_url_details'] = tk.LabelFrame(win_batchdetails, text="URL Details")
        self.inputs['frame_url_details'].columnconfigure(0, weight=1)
        self.inputs['frame_url_details'].columnconfigure(1, weight=1)
        # self.inputs['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['lstbx_url_center'] = w.LabelInput(self.inputs['frame_url_details'], "Select URL:"
                                                       , input_class=ttk.Combobox
                                                       , input_var=tk.StringVar(),
                                                       input_arg={'values': c.AppConfig.URL_LIST})

        self.inputs['lstbx_url_center'].grid(row=0, column=0, padx=10, columnspan=2)

        #####################################
        # ALM  Detials
        #####################################
        self.inputs['frame_alm_details'] = tk.LabelFrame(win_batchdetails, text="ALM Details")
        self.inputs['frame_alm_details'].columnconfigure(0, weight=1)
        self.inputs['frame_alm_details'].columnconfigure(1, weight=1)

        if c.AppConfig.USE_ALM:
            self.inputs['frame_alm_details'].grid(row=6, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['txb_alm_plan_path'] = w.LabelInput(self.inputs['frame_alm_details'], "Test Plan Path:",
                                                        input_class=w.ValidEntry,
                                                        input_var=tk.StringVar())
        self.inputs['txb_alm_plan_path'].variable.set("Subject\Demo")

        self.inputs['txb_alm_plan_path'].grid(row=0, column=0, padx=10)

        self.inputs['txb_alm_lab_path'] = w.LabelInput(self.inputs['frame_alm_details'], "Test Lab Path:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar())
        self.inputs['txb_alm_lab_path'].variable.set("Root\Demo")

        self.inputs['txb_alm_lab_path'].grid(row=0, column=1, padx=10)

        self.inputs['txb_alm_test_set_name'] = w.LabelInput(self.inputs['frame_alm_details'], "Test Set Name:",
                                                            input_class=w.ValidEntry,
                                                            input_var=tk.StringVar())
        self.inputs['txb_alm_test_set_name'].variable.set("Demo_Test_Set")

        self.inputs['txb_alm_test_set_name'].grid(row=0, column=3, padx=10)

        # Adding the Create Batch/ Book Mark Button
        self.inputs['btn_createBatch_Bookmark'] = w.LabelInput(win_batchdetails, "Create Batch", input_class=ttk.Button,
                                                               input_var=tk.StringVar(),
                                                               input_arg={'command': self.callbacks[
                                                                   'btn_createBatch_Bookmark']})

        self.inputs['btn_createBatch_Bookmark'].grid(row=8, column=0, sticky=(tk.W), padx=10)

    def cmd_select_application_type(self):
        if self.inputs['rb_applicationTypeWeb'].variable.get() == 'Mobile':
            self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_browser'].grid_remove()
            self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)
            self.inputs['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['frame_url_details'].grid_remove()

        elif self.inputs['rb_applicationTypeWeb'].variable.get() == 'Web':
            self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_device'].grid_remove()
            self.inputs['lstbx_browser'].grid(row=0, column=0, padx=10)
            self.inputs['frame_mc_details'].grid_remove()

        else:
            self.inputs['frame_device_browser'].grid_remove()
            self.inputs['frame_url_details'].grid_remove()
            self.inputs['lstbx_device'].grid_remove()
            self.inputs['lstbx_browser'].grid_remove()
            self.inputs['frame_mc_details'].grid_remove()

    def load_device_list(self, device_list):
        device_list = device_list if device_list else []
        self.inputs['lstbx_device'].variable.set(device_list)

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            # print(widget.widgetName)
            if widget.widgetName in ('labelframe',):
                pass
            # elif hasattr(widget,'tree') and 'foldertreeview'in str(widget).split('!'):
            #     data[key] = widget.get_selected_item_path()
            # elif hasattr(widget, 'tree') and 'tabulartreeview' in str(widget).split('!'):
            #     data[key] = widget.get_selected_items()
            else:
                data[key] = widget.get()
        return data

    def unload_gui(self):
        self.win_batchdetails.destroy()


class BatchMonitor(tk.Frame):
    """The input form for the Batch Widgets"""

    def __init__(self, parent, callbacks, fields=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets

        self.inputs = {}
        self.callbacks = callbacks
        ########################
        # Batch Frame
        #######################
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        frame_projectinfo = tk.LabelFrame(self, text="Batches")
        frame_projectinfo.grid(row=0, sticky=tk.NSEW, padx=10, pady=10)  # Display Project Info Frame
        frame_projectinfo.columnconfigure(0, weight=1)
        frame_projectinfo.rowconfigure(0, weight=1)

        # Adding Table For Searched Batches

        self.inputs['trv_batches'] = w.BatchTabularTreeView(frame_projectinfo,
                                                            ('Batch ID',
                                                             'Name',
                                                             'Status',
                                                             'Creation Date',
                                                             '#Processes',
                                                             '#Scripts',
                                                             'Application Type',
                                                             'Device/Browsers'), selection_mode='browse',
                                                            **kwargs)

        self.inputs['trv_batches'].set_column_width('Batch ID', 60)
        self.inputs['trv_batches'].set_column_width('Name', 300)
        self.inputs['trv_batches'].set_column_width('#Processes', 60)
        self.inputs['trv_batches'].set_column_width('#Scripts', 55)
        self.inputs['trv_batches'].set_column_width('Application Type', 100)
        self.inputs['trv_batches'].set_column_width('Creation Date', 120)
        self.inputs['trv_batches'].grid(row=0, column=0, sticky=tk.NSEW)

        self.inputs['trv_batches'].add_cmd(label="Open",
                                           command=self.callbacks['Open'])

        self.inputs['trv_batches'].add_cmd(label="Start",
                                           command=self.callbacks['Start'])

        self.inputs['trv_batches'].add_cmd(label="Stop",
                                           command=self.callbacks['Stop'])

        self.inputs['trv_batches'].add_cmd(label="Rerun Batch",
                                           command=self.callbacks['Rerun'])
        self.inputs['trv_batches'].add_cmd(label="Update Details",
                                           command=self.callbacks['Update Details'])
        self.inputs['trv_batches'].add_cmd(label="Clone Batch",
                                           command=self.callbacks['Clone Batch'])
        self.inputs['trv_batches'].tree.bind("<Double-1>", self.on_double_click_record)

        frame_batch_buttons = tk.Frame(self)
        frame_batch_buttons.grid(row=1, column=0, sticky=(tk.W + tk.E), padx=10, pady=10)
        # Adding the Open Selected Batch
        self.inputs['btn_open_selected'] = w.LabelInput(frame_batch_buttons, "Open Selected"
                                                        , input_class=ttk.Button
                                                        , input_var=tk.StringVar()
                                                        , input_arg={'command': self.callbacks['btn_open_selected']})
        self.inputs['btn_open_selected'].grid(row=0, column=0)
        self.inputs['btn_refresh'] = w.LabelInput(frame_batch_buttons, "Refresh"
                                                  , input_class=ttk.Button
                                                  , input_var=tk.StringVar()
                                                  , input_arg={'command': self.callbacks['btn_refresh']})
        self.inputs['btn_refresh'].grid(row=0, column=1)
        self.inputs['btn_download'] = w.LabelInput(frame_batch_buttons, "Download"
                                                   , input_class=ttk.Button
                                                   , input_var=tk.StringVar()
                                                   , input_arg={'command': self.download_detail_report})
        self.inputs['btn_download'].grid(row=0, column=2)

    def download_detail_report(self):
        try:
            self.inputs['trv_batches'].to_csv()
            messagebox.showinfo('Success.', 'Download Completed!!!', parent=self)
        except PermissionError as e:
            messagebox.showerror('PermissionError', "{}. Please close file if already opened".format(e.strerror),
                                 parent=self)
        except FileNameNotFoundException:
            pass

    def on_double_click_record(self, *args):
        self.callbacks['on_double_click']()

    def populate_batch_information(self, batches):
        """Remove Existing Batches"""
        self.inputs['trv_batches'].clear_items()
        for batch in batches:
            self.inputs['trv_batches'].insert_item(batch, allow_duplicates=False,
                                                   values=(batch['Batch_ID'],
                                                           batch['Batch_Name'],
                                                           batch['Status'],
                                                           batch['CreationDate'],
                                                           batch['ThreadCount'],
                                                           batch['ScriptCount'],
                                                           batch['TestType'],
                                                           batch['Browsers_OR_Devices']))


class BatchExecutionMonitor(tk.Toplevel):
    """Class for Batch Execution Monitor"""

    def __init__(self, parent, callbacks, batch_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets
        self.inputs = {}
        self.callbacks = callbacks
        self.title("Batch Exexution Monitor:{}".format(batch_id))
        self.lift()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.Batch_ID = batch_id

        frame_batch_execution_details = tk.LabelFrame(self, text="Batch Execution Details")
        frame_batch_execution_details.grid(row=1, sticky=tk.NSEW, padx=10, pady=10)
        frame_batch_execution_details.columnconfigure(0, weight=1)
        frame_batch_execution_details.rowconfigure(0, weight=1)

        ###################################################
        # Batch Information Section
        #################################################
        frame_batch_info = tk.LabelFrame(self, text="Batch Infromation")
        frame_batch_info.columnconfigure(5, weight=1)
        frame_batch_info.grid(row=0, sticky=(tk.W + tk.E), padx=10, pady=10)
        ttk.Label(frame_batch_info, text="Batch Name:", font=("TkDefaultFont", 9, 'bold')).grid(row=0, column=0,
                                                                                                padx=50,
                                                                                                sticky=tk.W)
        self.inputs["lbl_batchName"] = w.LabelInput(frame_batch_info, "", input_class=ttk.Label,
                                                    input_var=tk.StringVar())
        self.inputs["lbl_batchName"].grid(row=0, column=1)

        ttk.Label(frame_batch_info, text="Creation Date:", font=("TkDefaultFont", 9, 'bold')).grid(row=0, column=2,
                                                                                                   padx=50,
                                                                                                   sticky=tk.W)
        self.inputs["lbl_creationDate"] = w.LabelInput(frame_batch_info, "", input_class=ttk.Label,
                                                       input_var=tk.StringVar())
        self.inputs["lbl_creationDate"].grid(row=0, column=3)

        ttk.Label(frame_batch_info, text="Total Scripts:", font=("TkDefaultFont", 9, 'bold')).grid(row=0, column=4,
                                                                                                   padx=50,
                                                                                                   sticky=tk.W)
        self.inputs["lbl_totalScripts"] = w.LabelInput(frame_batch_info, "", input_class=ttk.Label,
                                                       input_var=tk.IntVar())
        self.inputs["lbl_totalScripts"].grid(row=0, column=5)

        ttk.Label(frame_batch_info, text="Passed:", font=("TkDefaultFont", 9, 'bold')).grid(row=1, column=0,
                                                                                            padx=50,
                                                                                            sticky=tk.W)
        self.inputs["lbl_totalpassed"] = w.LabelInput(frame_batch_info, "", input_class=ttk.Label,
                                                      input_var=tk.IntVar())
        self.inputs["lbl_totalpassed"].grid(row=1, column=1)

        ttk.Label(frame_batch_info, text="Failed:", font=("TkDefaultFont", 9, 'bold')).grid(row=1, column=2,
                                                                                            padx=50,
                                                                                            sticky=tk.W)
        self.inputs["lbl_totalFailed"] = w.LabelInput(frame_batch_info, "", input_class=ttk.Label,
                                                      input_var=tk.IntVar())
        self.inputs["lbl_totalFailed"].grid(row=1, column=3)

        ttk.Label(frame_batch_info, text="Pass Percentage:", font=("TkDefaultFont", 9, 'bold')).grid(row=1, column=4,
                                                                                                     padx=50,
                                                                                                     sticky=tk.W)

        self.inputs["lbl_passpercent"] = w.LabelInput(frame_batch_info, "", input_class=ttk.Label,
                                                      input_var=tk.IntVar())
        self.inputs["lbl_passpercent"].grid(row=1, column=5)

        # *****************************
        # Scripts Gui
        # *****************************
        self.inputs['trv_batchScripts'] = w.ScriptTabularTreeView(frame_batch_execution_details,
                                                                  ('S.No',
                                                                   'Name',
                                                                   'Documentation',
                                                                   'Module',
                                                                   'Status',
                                                                   'Start Date',
                                                                   'End Date',
                                                                   'Device/Browser',
                                                                   'Run Count'), selection_mode='browse', height=30)

        self.inputs['trv_batchScripts'].set_column_width('S.No', 60)
        self.inputs['trv_batchScripts'].set_column_width('Name', 300)
        self.inputs['trv_batchScripts'].set_column_width('Documentation', 300)
        self.inputs['trv_batchScripts'].set_column_width('Module', 100)
        self.inputs['trv_batchScripts'].set_column_width('Status', 80)
        self.inputs['trv_batchScripts'].set_column_width('Start Date', 100)
        self.inputs['trv_batchScripts'].set_column_width('End Date', 100)
        self.inputs['trv_batchScripts'].set_column_width('Device/Browser', 100)
        self.inputs['trv_batchScripts'].set_column_width('Run Count', 60)

        self.inputs['trv_batchScripts'].grid(row=0, column=0, sticky=tk.NSEW)

        self.inputs['trv_batchScripts'].add_cmd(label="Open",
                                                command=self.callbacks['Open'])
        self.inputs['trv_batchScripts'].add_cmd(label="Re-Run",
                                                command=self.callbacks['Re-Run'])
        self.inputs['trv_batchScripts'].add_cmd(label="Update",
                                                command=self.callbacks['Update'])
        self.inputs['trv_batchScripts'].add_cmd(label="Stop",
                                                command=self.callbacks['Stop'])
        self.inputs['trv_batchScripts'].tree.bind("<Double-1>", self.on_double_click_record)

        frame_btns_batch_execution_details = tk.Frame(self)
        frame_btns_batch_execution_details.grid(row=2, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['btn_refresh'] = w.LabelInput(frame_btns_batch_execution_details, "Refresh"
                                                  , input_class=ttk.Button
                                                  , input_var=tk.StringVar()
                                                  , input_arg={'command': self.callbacks['Refresh']})
        self.inputs['btn_refresh'].grid(row=0, column=0)
        self.inputs['btn_download_to_csc'] = w.LabelInput(frame_btns_batch_execution_details, "Download"
                                                          , input_class=ttk.Button
                                                          , input_var=tk.StringVar()
                                                          , input_arg={'command': self.download_detail_report})
        self.inputs['btn_download_to_csc'].grid(row=0, column=1)

    def download_detail_report(self):
        try:
            self.inputs['trv_batchScripts'].to_csv()
            messagebox.showinfo('Success.', 'Download Completed!!!', parent=self)
        except PermissionError as e:
            messagebox.showerror('PermissionError', "{}. Please close file if already opened".format(e.strerror),
                                 parent=self)
        except FileNameNotFoundException as e:
            pass

    def on_double_click_record(self, *args):
        self.callbacks['on_double_click']()

    def load_batch_information(self, batch_name, creation_date, script_count, scripts_passed, scripts_failed):

        self.inputs["lbl_batchName"].variable.set(batch_name)
        self.inputs["lbl_creationDate"].variable.set(creation_date)
        self.inputs["lbl_totalScripts"].variable.set(script_count)
        self.inputs["lbl_totalpassed"].variable.set(scripts_passed)
        self.inputs["lbl_totalFailed"].variable.set(scripts_failed)
        pass_percentage = (scripts_passed / script_count) * 100
        self.inputs["lbl_passpercent"].variable.set(pass_percentage)

    def load_scripts_information(self, scripts):

        count = 1
        for row in scripts:
            self.inputs['trv_batchScripts'].insert_item(row, allow_duplicates=False,
                                                        values=(count, row['ScriptName'],
                                                                row['Documentation'],
                                                                os.path.split(row['Source'])[1],
                                                                row['Status'],
                                                                row['Start_Time'],
                                                                row['End_Time'],
                                                                row['Device_Browser'],
                                                                row['Run_Count']))
            count += 1

    def refresh_scripts(self, scripts):
        """Function to refresh the Batch"""
        # Delete the Scripts
        self.inputs['trv_batchScripts'].clear_items()
        # Reinsert the scripts
        count = 1
        for row in scripts:
            self.inputs['trv_batchScripts'].insert_item(row, allow_duplicates=False,
                                                        values=(count, row['ScriptName'],
                                                                row['Documentation'],
                                                                os.path.split(row['Source'])[1],
                                                                row['Status'],
                                                                row['Start_Time'],
                                                                row['End_Time'],
                                                                row['Device_Browser'],
                                                                row['Run_Count']))
            count += 1
    #
    # def refresh_batch_labels(self, batch_name, script_count, scripts_passed, scripts_failed):
    #     """KW to Update Batch Labels"""
    #     self.inputs["lbl_batchName"].variable.set(batch_name)
    #     self.inputs["lbl_totalScripts"].variable.set(script_count)
    #     self.inputs["lbl_totalpassed"].variable.set(scripts_passed)
    #     self.inputs["lbl_totalFailed"].variable.set(scripts_failed)
    #     pass_percentage = (scripts_passed / script_count) * 100
    #     self.inputs["lbl_passpercent"].variable.set(pass_percentage)


class BatchUpdate(tk.Toplevel):
    """Class for Batch Update Window"""

    def __init__(self, parent, callbacks, batch_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets
        self.inputs = {}
        self.frames = {}
        self.callbacks = callbacks
        self.title("Batch Update:{}".format(batch_id))
        self.lift()
        self.grab_set()
        self.columnconfigure(0, weight=1)
        self.Batch_ID = batch_id

        ttk.Label(self, text="Update the batch details", font=("TkDefaultFont", 16)).grid(row=0)

        #############################
        # Create a Batch Info Frame
        ############################
        frame_batch_info = tk.LabelFrame(self, text="Batch Information")
        frame_batch_info.grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=10)
        frame_batch_info.columnconfigure(0, weight=1)
        self.inputs['txb_batchName'] = w.LabelInput(frame_batch_info, "Name:", input_class=w.ValidEntry,
                                                    input_var=tk.StringVar(),
                                                    input_arg={'state': 'readonly'})
        self.inputs['txb_batchName'].columnconfigure(0, weight=1)
        self.inputs['txb_batchName'].grid(row=0, column=0)

        self.inputs['txb_batchNumberOfThreads'] = w.LabelInput(frame_batch_info, "Number of Processes:",
                                                               input_class=w.ValidSpinbox,
                                                               input_var=tk.StringVar(),
                                                               input_arg={"from_": '1', "to": '4', "increment": '1'})
        self.inputs['txb_batchNumberOfThreads'].grid(row=0, column=1)

        #############################
        # Create a Application Type Frame
        ############################
        frame_application_type = tk.LabelFrame(self, text="Application Type & Language")
        frame_application_type.grid(row=3, sticky=(tk.W + tk.E), padx=10, pady=10)
        # frame_application_type.columnconfigure(4, weight=1)

        self.inputs['rb_applicationTypeWeb'] = w.LabelInput(frame_application_type, "Web",
                                                            input_class=ttk.Radiobutton,
                                                            input_var=tk.StringVar()
                                                            , input_arg={"value": "Web",
                                                                         'command': self.cmd_select_application_type})
        self.inputs['rb_applicationTypeWeb'].grid(row=0, column=2)

        self.inputs['rb_applicationTypeMobile'] = w.LabelInput(frame_application_type, "Mobile",
                                                               input_class=ttk.Radiobutton,
                                                               input_var=self.inputs['rb_applicationTypeWeb'].variable,
                                                               input_arg={"value": "Mobile",
                                                                          'command': self.cmd_select_application_type})
        self.inputs['rb_applicationTypeMobile'].grid(row=0, column=1)

        self.inputs['rb_applicationTypeOthers'] = w.LabelInput(frame_application_type, "Others",
                                                               input_class=ttk.Radiobutton,
                                                               input_var=self.inputs['rb_applicationTypeWeb'].variable,
                                                               input_arg={"value": "Others",
                                                                          'command': self.cmd_select_application_type})
        self.inputs['rb_applicationTypeOthers'].grid(row=0, column=0)

        self.inputs['rb_application_lang_FR'] = w.LabelInput(frame_application_type, "FR",
                                                             input_class=ttk.Radiobutton,
                                                             input_var=tk.StringVar()
                                                             , input_arg={"value": "FR"})
        self.inputs['rb_application_lang_FR'].grid(row=1, column=1, padx=10)

        self.inputs['rb_application_lang_EN'] = w.LabelInput(frame_application_type, "EN",
                                                             input_class=ttk.Radiobutton,
                                                             input_var=self.inputs['rb_application_lang_FR'].variable,
                                                             input_arg={"value": "EN"})
        self.inputs['rb_application_lang_EN'].grid(row=1, column=0)

        #############################
        # Create a Select Device/Browser Type Frame
        ############################
        self.inputs['frame_device_browser'] = tk.LabelFrame(self, text="Select Device / Browser ")
        # self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['frame_device_browser'].columnconfigure(0, weight=1)
        self.inputs['lstbx_device'] = w.LabelInput(self.inputs['frame_device_browser'], "Device List", input_class=tk.Listbox
                                                   , input_var=tk.StringVar(), input_arg={"selectmode": "multiple",
                                                                                          'exportselection': 0})

        self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)

        self.inputs['lstbx_browser'] = w.LabelInput(self.inputs['frame_device_browser'], "Internet Explorer", input_class=tk.Listbox
                                                    , input_var=tk.StringVar(), input_arg={"selectmode": "multiple",
                                                                                           'exportselection': 0})
        self.inputs['lstbx_browser'].variable.set(c.AppConfig.BROWSER_LIST)

        #####################################
        # Mobile Center Detials
        #####################################

        self.frames['frame_mc_details'] = tk.LabelFrame(self, text="Mobile Center Details")
        self.frames['frame_mc_details'].columnconfigure(0, weight=1)
        self.frames['frame_mc_details'].columnconfigure(1, weight=1)
        self.frames['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['lstbx_mobile_center'] = w.LabelInput(self.frames['frame_mc_details'], "Select Server:"
                                                          , input_class=ttk.Combobox
                                                          , input_var=tk.StringVar(),
                                                          input_arg={'values': c.AppConfig.SERVER_LIST})

        self.inputs['lstbx_mobile_center'].grid(row=0, column=0, padx=10, columnspan=2)

        self.inputs['txb_mc_user_name'] = w.LabelInput(self.frames['frame_mc_details'], "User Name:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar())

        self.inputs['txb_mc_user_name'].grid(row=1, column=0, padx=10)

        self.inputs['txb_mc_user_pass'] = w.LabelInput(self.frames['frame_mc_details'], "User Password:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar(),
                                                       input_arg={'show': '*'})
        self.inputs['txb_mc_user_pass'].grid(row=1, column=1, padx=10)

        #####################################
        # URL Detials
        #####################################
        self.frames['frame_url_details'] = tk.LabelFrame(self, text="URL Details")
        self.frames['frame_url_details'].columnconfigure(0, weight=1)
        self.frames['frame_url_details'].columnconfigure(1, weight=1)
        # self.inputs['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['lstbx_url_center'] = w.LabelInput(self.frames['frame_url_details'], "Select URL:"
                                                       , input_class=ttk.Combobox
                                                       , input_var=tk.StringVar(),
                                                       input_arg={'values': c.AppConfig.URL_LIST})

        self.inputs['lstbx_url_center'].grid(row=0, column=0, padx=10, columnspan=2)

        #####################################
        # ALM  Detials
        #####################################
        frame_alm_details = tk.LabelFrame(self, text="ALM Details")
        frame_alm_details.columnconfigure(0, weight=1)
        frame_alm_details.columnconfigure(1, weight=1)
        if c.AppConfig.USE_ALM:
            frame_alm_details.grid(row=6, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['txb_alm_plan_path'] = w.LabelInput(frame_alm_details, "Test Plan Path:",
                                                        input_class=w.ValidEntry,
                                                        input_var=tk.StringVar())

        self.inputs['txb_alm_plan_path'].grid(row=0, column=0, padx=10)

        self.inputs['txb_alm_lab_path'] = w.LabelInput(frame_alm_details, "Test Lab Path:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar())

        self.inputs['txb_alm_lab_path'].grid(row=0, column=1, padx=10)

        self.inputs['txb_alm_test_set_name'] = w.LabelInput(frame_alm_details, "Test Set Name:",
                                                            input_class=w.ValidEntry,
                                                            input_var=tk.StringVar())

        self.inputs['txb_alm_test_set_name'].grid(row=0, column=3, padx=10)

        # Adding the Create Batch/ Book Mark Button
        self.inputs['btn_update'] = w.LabelInput(self, "Update",
                                                 input_class=ttk.Button,
                                                 input_var=tk.StringVar(),
                                                 input_arg={'command': self.callbacks[
                                                     'btn_update']})

        self.inputs['btn_update'].grid(row=8, column=0, sticky=(tk.W), padx=10)
        # self.bind('<Destroy>', self.on_destroy)

    def on_destroy(self, *args):
        self.callbacks['refresh']()

    def load_device_list(self, device_list):
        device_list = device_list if device_list else []
        self.inputs['lstbx_device'].variable.set(device_list)

    def cmd_select_application_type(self):
        if self.inputs['rb_applicationTypeWeb'].variable.get() == 'Mobile':
            self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_browser'].grid_remove()
            self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)
            self.frames['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.frames['frame_url_details'].grid_remove()

        elif self.inputs['rb_applicationTypeWeb'].variable.get() == 'Web':
            self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_device'].grid_remove()
            self.frames['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_browser'].grid(row=0, column=0, padx=10)
            self.frames['frame_mc_details'].grid_remove()

        else:
            self.inputs['frame_device_browser'].grid_remove()
            self.inputs['lstbx_device'].grid_remove()
            self.frames['frame_url_details'].grid_remove()
            self.inputs['lstbx_browser'].grid_remove()
            self.frames['frame_mc_details'].grid_remove()

    def populate(self, batch_details, device_list):
        self.inputs['txb_batchName'].variable.set(batch_details["Batch_Name"])
        self.inputs['txb_batchNumberOfThreads'].variable.set(batch_details["ThreadCount"])
        self.inputs['rb_applicationTypeWeb'].variable.set(batch_details["TestType"])
        self.inputs['rb_application_lang_FR'].variable.set(batch_details["ENV_LANGUAGE"])
        self.inputs['lstbx_device'].variable.set(device_list)
        if batch_details["TestType"] == 'Mobile':
            self.inputs['lstbx_mobile_center'].variable.set(batch_details["ENV_MC_SERVER"])
            self.inputs['txb_mc_user_name'].variable.set(batch_details["ENV_MC_USER_NAME"])
            self.inputs['txb_mc_user_pass'].variable.set(batch_details["ENV_MC_USER_PASS"])
            self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_browser'].grid_remove()
            self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)
            self.frames['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.frames['frame_url_details'].grid_remove()

        elif batch_details["TestType"] == 'Web':
            self.inputs['frame_device_browser'].grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.frames['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.frames['frame_mc_details'].grid_remove()
            self.inputs['lstbx_device'].grid_remove()
            self.inputs['lstbx_browser'].grid(row=0, column=0, padx=10)
            self.inputs['lstbx_url_center'].variable.set(batch_details["ENV_URL"])

        else:
            self.inputs['frame_device_browser'].grid_remove()
            self.inputs['lstbx_device'].grid_remove()
            self.frames['frame_url_details'].grid_remove()
            self.inputs['lstbx_browser'].grid_remove()
            self.frames['frame_mc_details'].grid_remove()


        self.inputs['txb_alm_plan_path'].variable.set(batch_details["ALMTestPlanPath"])
        self.inputs['txb_alm_lab_path'].variable.set(batch_details["ALMTestLabPath"])
        self.inputs['txb_alm_test_set_name'].variable.set(batch_details["ALMTestSetName"])

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors


class ScriptUpdate(tk.Toplevel):
    """Class for Script Update Window"""

    def __init__(self, parent, callbacks, script_id, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets
        self.inputs = {}
        self.frames = {}
        self.callbacks = callbacks
        self.script_id = script_id
        self.title("Script Update:{}".format(self.script_id))
        self.lift()
        self.grab_set()
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Update the Scripts details", font=("TkDefaultFont", 16)).grid(row=0)

        #############################
        # Create a Script Info Frame
        ############################
        frame_batch_info = tk.LabelFrame(self, text="Script Information")
        frame_batch_info.grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=10)
        frame_batch_info.columnconfigure(0, weight=1)
        self.inputs['txb_ScriptName'] = w.LabelInput(frame_batch_info, "Name:", input_class=w.ValidEntry,
                                                     input_var=tk.StringVar(),
                                                     input_arg={'state': 'readonly'})
        self.inputs['txb_ScriptName'].columnconfigure(0, weight=1)
        self.inputs['txb_ScriptName'].grid(row=0, column=0)

        #############################
        # Create a Application Type Frame
        ############################
        frame_application_type = tk.LabelFrame(self, text="Application Type & Language")
        frame_application_type.grid(row=3, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['rb_applicationTypeWeb'] = w.LabelInput(frame_application_type, "Web",
                                                            input_class=ttk.Radiobutton,
                                                            input_var=tk.StringVar()
                                                            , input_arg={"value": "Web",
                                                                         'state': 'disabled'
                                                                         })
        self.inputs['rb_applicationTypeWeb'].grid(row=0, column=1, padx=10)

        self.inputs['rb_applicationTypeMobile'] = w.LabelInput(frame_application_type, "Mobile",
                                                               input_class=ttk.Radiobutton,
                                                               input_var=self.inputs['rb_applicationTypeWeb'].variable,
                                                               input_arg={"value": "Mobile",
                                                                          'state': 'disabled'
                                                                          })
        self.inputs['rb_applicationTypeMobile'].grid(row=0, column=0)

        self.inputs['rb_application_lang_FR'] = w.LabelInput(frame_application_type, "FR",
                                                             input_class=ttk.Radiobutton,
                                                             input_var=tk.StringVar()
                                                             , input_arg={"value": "FR",
                                                                          'state': 'disabled'
                                                                          })
        self.inputs['rb_application_lang_FR'].grid(row=1, column=1, padx=10)

        self.inputs['rb_application_lang_EN'] = w.LabelInput(frame_application_type, "EN",
                                                             input_class=ttk.Radiobutton,
                                                             input_var=self.inputs['rb_application_lang_FR'].variable,
                                                             input_arg={"value": "EN",
                                                                        'state': 'disabled'
                                                                        })
        self.inputs['rb_application_lang_EN'].grid(row=1, column=0)

        #############################
        # Create a Select Device/Browser Type Frame
        ############################
        frame_device_browser = tk.LabelFrame(self, text="Select Device / Browser ")
        frame_device_browser.grid(row=4, sticky=(tk.W + tk.E), padx=10, pady=10)
        frame_device_browser.columnconfigure(0, weight=1)
        self.inputs['lstbx_device'] = w.LabelInput(frame_device_browser, "Device List", input_class=tk.Listbox
                                                   , input_var=tk.StringVar(), input_arg={"selectmode": "single",
                                                                                          'exportselection': 0})

        self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)

        self.inputs['lstbx_browser'] = w.LabelInput(frame_device_browser, "Internet Explorer", input_class=tk.Listbox
                                                    , input_var=tk.StringVar(), input_arg={"selectmode": "single",
                                                                                           'exportselection': 0})
        self.inputs['lstbx_browser'].variable.set("IE Chrome FireFox Safari")

        #####################################
        # Mobile Center Detials
        #####################################

        self.frames['frame_mc_details'] = tk.LabelFrame(self, text="Mobile Center Details")
        self.frames['frame_mc_details'].columnconfigure(0, weight=1)
        self.frames['frame_mc_details'].columnconfigure(1, weight=1)
        self.frames['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['lstbx_mobile_center'] = w.LabelInput(self.frames['frame_mc_details'], "Select Server:"
                                                          , input_class=ttk.Combobox
                                                          , input_var=tk.StringVar(),
                                                          input_arg={'values': c.AppConfig.SERVER_LIST,
                                                                     'state': 'disabled'})

        self.inputs['lstbx_mobile_center'].grid(row=0, column=0, padx=10, columnspan=2)

        self.inputs['txb_mc_user_name'] = w.LabelInput(self.frames['frame_mc_details'], "User Name:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar(),
                                                       input_arg={'state': 'readonly'})

        self.inputs['txb_mc_user_name'].grid(row=1, column=0, padx=10)

        self.inputs['txb_mc_user_pass'] = w.LabelInput(self.frames['frame_mc_details'], "User Password:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar(),
                                                       input_arg={'state': 'readonly',
                                                                  'show': '*'})
        self.inputs['txb_mc_user_pass'].grid(row=1, column=1, padx=10)

        #####################################
        # URL Detials
        #####################################
        self.frames['frame_url_details'] = tk.LabelFrame(self, text="URL Details")
        self.frames['frame_url_details'].columnconfigure(0, weight=1)
        self.frames['frame_url_details'].columnconfigure(1, weight=1)
        # self.inputs['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)

        self.inputs['lstbx_url_center'] = w.LabelInput(self.frames['frame_url_details'], "Select URL:"
                                                       , input_class=ttk.Combobox
                                                       , input_var=tk.StringVar(),
                                                       input_arg={'values': c.AppConfig.URL_LIST,
                                                                  'state': 'disabled'})

        self.inputs['lstbx_url_center'].grid(row=0, column=0, padx=10, columnspan=2)

        #####################################
        # ALM  Detials
        #####################################
        frame_alm_details = tk.LabelFrame(self, text="ALM Details")
        frame_alm_details.columnconfigure(0, weight=1)
        frame_alm_details.columnconfigure(1, weight=1)
        if c.AppConfig.USE_ALM:
            frame_alm_details.grid(row=6, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['txb_alm_plan_path'] = w.LabelInput(frame_alm_details, "Test Plan Path:",
                                                        input_class=w.ValidEntry,
                                                        input_var=tk.StringVar(),
                                                        input_arg={'state': 'readonly'})

        self.inputs['txb_alm_plan_path'].grid(row=0, column=0, padx=10)

        self.inputs['txb_alm_lab_path'] = w.LabelInput(frame_alm_details, "Test Lab Path:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar(),
                                                       input_arg={'state': 'readonly'})

        self.inputs['txb_alm_lab_path'].grid(row=0, column=1, padx=10)

        self.inputs['txb_alm_test_set_name'] = w.LabelInput(frame_alm_details, "Test Set Name:",
                                                            input_class=w.ValidEntry,
                                                            input_var=tk.StringVar(),
                                                            input_arg={'state': 'readonly'})

        self.inputs['txb_alm_test_set_name'].grid(row=0, column=3, padx=10)

        # Adding the Create Batch/ Book Mark Button
        self.inputs['btn_update'] = w.LabelInput(self, "Update",
                                                 input_class=ttk.Button,
                                                 input_var=tk.StringVar(),
                                                 input_arg={'command': self.callbacks[
                                                     'btn_update']})

        self.inputs['btn_update'].grid(row=8, column=0, sticky=(tk.W), padx=10)
        # self.bind('<Destroy>', self.on_destroy)

    def on_destroy(self, *args):
        self.callbacks['refresh']()

    def load_device_list(self, device_list):
        device_list = device_list if device_list else []
        self.inputs['lstbx_device'].variable.set(device_list)

    def populate(self, batch_details, device_list):
        self.inputs['txb_ScriptName'].variable.set(batch_details["ScriptName"])
        self.inputs['rb_applicationTypeWeb'].variable.set(batch_details["TestType"])
        self.inputs['rb_application_lang_FR'].variable.set(batch_details["ENV_LANGUAGE"])
        self.inputs['lstbx_device'].variable.set(device_list)
        if batch_details["TestType"] != 'Web':
            self.inputs['lstbx_mobile_center'].variable.set(batch_details["ENV_MC_SERVER"])
            self.inputs['txb_mc_user_name'].variable.set(batch_details["ENV_MC_USER_NAME"])
            self.inputs['txb_mc_user_pass'].variable.set(batch_details["ENV_MC_USER_PASS"])
            self.inputs['lstbx_browser'].grid_remove()
            self.inputs['lstbx_device'].grid(row=0, column=0, padx=10)
            self.frames['frame_mc_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.frames['frame_url_details'].grid_remove()
        else:
            self.frames['frame_mc_details'].grid_remove()
            self.frames['frame_url_details'].grid(row=5, sticky=(tk.W + tk.E), padx=10, pady=10)
            self.inputs['lstbx_device'].grid_remove()
            self.inputs['lstbx_browser'].grid(row=0, column=0, padx=10)
            self.inputs['lstbx_url_center'].variable.set(batch_details["ENV_URL"])
        self.inputs['txb_alm_plan_path'].variable.set(batch_details["ALMTestPlanPath"])
        self.inputs['txb_alm_lab_path'].variable.set(batch_details["ALMTestLabPath"])
        self.inputs['txb_alm_test_set_name'].variable.set(batch_details["ALMTestSetName"])

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors


class CreateBookMark(tk.Toplevel):
    """Class for Book mark Update Window"""

    def __init__(self, parent, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets
        self.inputs = {}
        self.frames = {}
        self.callbacks = callbacks
        self.title("Create BookMark")
        self.lift()
        self.grab_set()
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Enter Bookmark Details", font=("TkDefaultFont", 16)).grid(row=0)

        #############################
        # Create a Book Mark Frame
        ############################
        self.frames['frame_batch_info'] = tk.LabelFrame(self, text="Bookmark Information")
        self.frames['frame_batch_info'].grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.frames['frame_batch_info'].columnconfigure(0, weight=1)
        self.inputs['txb_bookmarkName'] = w.LabelInput(self.frames['frame_batch_info'], "Name:",
                                                       input_class=w.ValidEntry,
                                                       input_var=tk.StringVar())
        self.inputs['txb_bookmarkName'].columnconfigure(0, weight=1)
        self.inputs['txb_bookmarkName'].grid(row=0, column=0)

        # Adding the Create  Book Mark Button
        self.inputs['btn_createBookMark'] = w.LabelInput(self, "Create Bookmark",
                                                         input_class=ttk.Button,
                                                         input_var=tk.StringVar(),
                                                         input_arg={'command': self.callbacks[
                                                             'btn_createBookMark']})

        self.inputs['btn_createBookMark'].grid(row=2, column=0, sticky=(tk.W), padx=10)

    def load_admin_ui(self):
        return simpledialog.askstring('Admin Access Required', 'Admin Password:', parent=self, show='*')

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors


class AlmLoginForm(tk.Toplevel):
    """The input form for the Batch Widgets"""

    def __init__(self, parent, callbacks, settings, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)
        self.inputs = {}
        self.frames = {}
        self.data_dict = {}
        self.callbacks = callbacks
        self.settings = settings
        menu = MainMenu(self, self.settings, self.callbacks)
        self.configure(menu=menu)
        self.resizable(width=False, height=False)
        parent.update_idletasks()
        x = int(parent.winfo_x()) + 100
        y = int(parent.winfo_y()) + 100
        self.geometry("+%d+%d" % (x, y))
        self.grab_set()
        self.lift()
        self.columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", parent.destroy)

        ttk.Label(self, text="Application Lifecycle Management Login", font=("TkDefaultFont", 16)).grid(row=0)

        self.frames['frm_user_details'] = tk.LabelFrame(self, text="User Details")
        self.frames['frm_user_details'].grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.frames['frm_user_details'].columnconfigure(0, weight=1)
        self.inputs['txb_user_name'] = w.LabelInput(self.frames['frm_user_details'], "Name:", input_class=w.ValidEntry,
                                                    input_var=tk.StringVar()
                                                    )
        self.inputs['txb_user_name'].grid(row=0, column=0)
        self.inputs['txb_user_name'].bind('<Key>', self.__on_key_pressed)

        self.inputs['txb_user_pass'] = w.LabelInput(self.frames['frm_user_details'], "Password:", input_class=ttk.Entry,
                                                    input_var=tk.StringVar(),
                                                    input_arg={'show': '*'}
                                                    )
        self.inputs['txb_user_pass'].grid(row=1, column=0)

        self.inputs['btn_authenticate'] = w.LabelInput(self.frames['frm_user_details'], label='Authenticate',
                                                       input_class=ttk.Button,
                                                       input_var=tk.StringVar(),
                                                       input_arg={'command': self.callbacks['btn_authenticate']}
                                                       )
        self.inputs['btn_authenticate'].grid(row=2, column=0)

        self.frames['frm_project_details'] = tk.LabelFrame(self, text="Project Details")
        self.frames['frm_project_details'].grid(row=2, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.frames['frm_project_details'].columnconfigure(0, weight=1)

        self.inputs['cb_domain'] = w.LabelInput(self.frames['frm_project_details'], label='Domain:',
                                                input_class=ttk.Combobox,
                                                input_var=tk.StringVar(),
                                                input_arg={'state': 'disabled'})
        self.inputs['cb_domain'].grid(row=0, column=0)

        self.inputs['cb_domain'].bind("<<ComboboxSelected>>", self.__on_combobox_selected)

        self.inputs['cb_project'] = w.LabelInput(self.frames['frm_project_details'], label='Project:',
                                                 input_class=ttk.Combobox,
                                                 input_var=tk.StringVar(),
                                                 input_arg={'state': 'disabled'})
        self.inputs['cb_project'].grid(row=1, column=0)

        self.inputs['btn_login'] = w.LabelInput(self.frames['frm_project_details'], label='Login',
                                                input_class=ttk.Button,
                                                input_var=tk.StringVar(),
                                                input_arg={'state': 'disabled', 'command': self.callbacks['btn_login']})
        self.inputs['btn_login'].grid(row=2, column=0)

    def populate(self, data_dict):
        self.data_dict = data_dict
        self.inputs['cb_domain'].input.configure(state='readonly')
        self.inputs['cb_project'].input.configure(state='readonly')
        self.inputs['btn_login'].input.configure(state=tk.NORMAL)
        self.inputs['cb_domain'].variable.set('')
        self.inputs['cb_project'].variable.set('')
        self.inputs['cb_domain'].set(list(self.data_dict.keys()))
        self.inputs['cb_project'].set(self.data_dict.get(self.inputs['cb_domain'].get()), [])

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            if widget.widgetName in ('labelframe',):
                pass
            else:
                data[key] = widget.get()
        return data

    def reset(self):
        for widget in self.inputs.values():
            widget.set('')

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors

    def __on_combobox_selected(self, *args):
        self.inputs['cb_project'].set(self.data_dict.get(self.inputs['cb_domain'].get()), [])

    def __on_key_pressed(self, *args):
        self.inputs['cb_domain'].input.configure(state=tk.DISABLED)
        self.inputs['cb_project'].input.configure(state=tk.DISABLED)
        self.inputs['btn_login'].input.configure(state=tk.DISABLED)


class StatisticsForm(tk.Frame):
    """View for Stats Form"""

    def __init__(self, parent, callbacks, stats_type=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets
        self.inputs = {}
        self.callbacks = callbacks
        self.stats_type = stats_type if stats_type else []
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(2, weight=1)

        ########################
        # Selection Frame
        #######################
        frm_selection = tk.LabelFrame(self, text="Selection")
        frm_selection.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)  # Display Selection  Frame
        frm_selection.columnconfigure(0, weight=1)
        self.inputs['cb_select_stats'] = w.LabelInput(frm_selection, label='',
                                                      input_class=ttk.Combobox,
                                                      input_var=tk.StringVar(),
                                                      input_arg={'state': "readonly"}
                                                      )
        self.inputs['cb_select_stats'].variable.set("Select Option")
        self.inputs['cb_select_stats'].set(self.stats_type)
        self.inputs['cb_select_stats'].bind("<<ComboboxSelected>>", self.__on_combobox_selected)
        self.inputs['cb_select_stats'].grid(row=0, column=0, sticky="nsew", padx=10, pady=3)
        date_frame = ttk.Frame(frm_selection)
        date_frame.grid(row=1, column=0, sticky="nsew")
        date_frame.columnconfigure(0, weight=1)
        date_frame.columnconfigure(1, weight=1)
        self.inputs['tb_from_date'] = w.LabelInput(date_frame, label='From Date(yyyy-mm-dd):',
                                                   input_class=w.ValidDateEntry,
                                                   input_var=tk.StringVar())
        self.inputs['tb_from_date'].grid(row=1, column=0, sticky="nsew", padx=10)
        self.inputs['tb_from_date'].set(datetime.now().strftime('%Y-%m-%d'))
        self.inputs['tb_to_date'] = w.LabelInput(date_frame, label='To Date(yyyy-mm-dd):',
                                                 input_class=w.ValidDateEntry,
                                                 input_var=tk.StringVar())
        self.inputs['tb_to_date'].grid(row=1, column=1, sticky="nsew", padx=10)
        self.inputs['tb_to_date'].set(datetime.now().strftime('%Y-%m-%d'))
        self.inputs['btn_generate_report'] = w.LabelInput(date_frame, label='Generate Report',
                                                          input_class=ttk.Button,
                                                          input_var=tk.StringVar(),
                                                          input_arg={'command': self.callbacks['generate_report']})
        self.inputs['btn_generate_report'].grid(row=2, column=0, sticky="nsew", padx=10, pady=3)

        self.inputs['btn_download_report'] = w.LabelInput(date_frame, label='Download Report',
                                                          input_class=ttk.Button,
                                                          input_var=tk.StringVar(),
                                                          input_arg={'command': self.download_detail_report})
        # input_arg={'command': self.callbacks['download_report']})

        self.inputs['btn_download_report'].grid(row=2, column=1, sticky="nsew", padx=10, pady=3)

        ########################
        # Stats Frame
        #######################
        self.frm_stats = tk.LabelFrame(self, text="Statistics")
        self.frm_stats.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)  # Display Stats  Frame
        self.frm_stats.columnconfigure(0, weight=1)
        self.frm_stats.columnconfigure(1, weight=1)

        ########################
        # Graph Frame
        #######################
        self.frm_graph_frame = tk.Frame(self.frm_stats)
        self.frm_graph_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)  # Display Graph  Frame
        self.frm_graph_frame.columnconfigure(0, weight=1)
        self.bar_graph = w.BarGraph(self.frm_graph_frame)

        ########################
        # Details Frame
        #######################
        self.frm_details_grid = tk.LabelFrame(self, text="Details")
        self.frm_details_grid.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)  # Display Details  Frame
        self.frm_details_grid.columnconfigure(0, weight=1)
        self.frm_details_grid.rowconfigure(0, weight=1)

    def populate_report_table(self, data_records):
        """Function to populate report table"""
        if self.inputs.get('trv_report_table', None) is not None:
            self.inputs['trv_report_table'].destroy()
        self.inputs['trv_report_table'] = w.TabularTreeView(self.frm_details_grid,
                                                            columnNames=tuple(data_records[0].keys()))
        for data in data_records:
            self.inputs['trv_report_table'].insert_item(data, values=list(dict(data).values()))

        self.inputs['trv_report_table'].grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=5)

    def populate_statistics_data(self, data_records):
        """Function to populate stats data"""
        if self.inputs.get('trv_stats_table', None) is not None:
            self.inputs['trv_stats_table'].destroy()
        self.inputs['trv_stats_table'] = w.TabularTreeView(self.frm_stats,
                                                           columnNames=('Type', '#'))
        for key, value in data_records.items():
            self.inputs['trv_stats_table'].insert_item(data_records, values=[key, value])
        self.inputs['trv_stats_table'].grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=5)

    def download_detail_report(self):
        if self.inputs.get('trv_report_table', None) is None:
            messagebox.showerror('No Report Found', "Please Generate a report before Downloading",
                                 parent=self)
            return
        try:
            self.inputs['trv_report_table'].to_csv()
            messagebox.showinfo('Success.', 'Download Completed!!!', parent=self)
        except PermissionError as e:
            messagebox.showerror('Download Error', "{}. Please close file if already opened".format(e.strerror),
                                 parent=self)
        except FileNameNotFoundException as e:
            pass

    def add_bar_to_chart(self, title, x_label, y_label, bar_graph_data):
        # Initial Cleanup
        self.bar_graph.axes.clear()
        self.bar_graph.canvas.draw()
        self.bar_graph.set_axis_label(x_label, y_label, title)
        for bar in bar_graph_data:
            self.bar_graph.add_bar(**bar)

    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            if widget is None or widget.widgetName in ('labelframe',):
                pass
            else:
                data[key] = widget.get()
        return data

    def __on_combobox_selected(self, *args):
        self.callbacks['cb_on_select_stats'](self.inputs['cb_select_stats'].get())

    def set_date_fields_visibility(self, visible=True):
        if not visible:
            self.inputs['tb_from_date'].input.configure(state='readonly')
            self.inputs['tb_to_date'].input.configure(state='readonly')
            self.inputs['tb_from_date'].grid_forget()
            self.inputs['tb_to_date'].grid_forget()
        else:
            self.inputs['tb_from_date'].grid(row=1, column=0, sticky="nsew", padx=10)
            self.inputs['tb_to_date'].grid(row=1, column=1, sticky="nsew", padx=10)
            self.inputs['tb_from_date'].input.configure(state='default')
            self.inputs['tb_to_date'].input.configure(state='default')


class MainMenu(tk.Menu):
    """Application's Main Menu"""
    def __init__(self, parent, settings, callbacks, **kwargs):
        super().__init__(parent, **kwargs)
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=callbacks['file->quit'])
        self.add_cascade(label='File', menu=file_menu)
        options_menu = tk.Menu(self, tearoff=False)
        options_menu.add_checkbutton(label='Use ALM', variable=settings['use alm'], command=callbacks['options->use_alm'])
        options_menu.add_command(label='Preferences',
                                     command=callbacks['options->preferences'])
        self.add_cascade(label='Options', menu=options_menu)

        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label='About', command=self.show_about)
        self.add_cascade(label='About', menu=help_menu)

    def show_about(self):
        """show about dialog"""
        about_message = 'Robot Executor'
        about_details = ('By Mandeep Dhiman\n'
                         'For assistance please contact the author\n'
                         'Email: {}\n'
                         'Version :{}'.format(robo_app.__authormail__,robo_app.__version__))
        messagebox.showinfo(title='About', message=about_message, detail=about_details)


class Preferences(tk.Toplevel):
    """Class for Preferences"""

    def __init__(self, parent, settings_variable, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Dictonary to keep tracK of input Widgets
        self.inputs = {}
        self.frames = {}
        self.callbacks = callbacks
        self.title("Preferences")
        self.lift()
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Preferences", font=("TkDefaultFont", 16)).grid(row=0)

        #############################
        # Create a ALM Info Frame
        ############################
        frame_alm_info = tk.LabelFrame(self, text="ALM Settings")
        frame_alm_info.grid(row=1, sticky=(tk.W + tk.E), padx=10, pady=10)
        frame_alm_info.columnconfigure(0, weight=1)
        self.inputs['txb_alm_url'] = w.LabelInput(frame_alm_info, "ALM URL:", input_class=w.ValidEntry,
                                                     input_var=settings_variable['alm_url'])
        self.inputs['txb_alm_url'].columnconfigure(0, weight=1)
        self.inputs['txb_alm_url'].grid(row=0, column=0, sticky=(tk.W + tk.E))

        #############################
        # Create BROWSER Settings Frame
        ############################
        frame_web_info = tk.LabelFrame(self, text="Web/Browser Settings")
        frame_web_info.columnconfigure(0, weight=1)
        frame_web_info.grid(row=2, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['txb_browser_list'] = w.LabelInput(frame_web_info, "Browser List:", input_class=w.ValidEntry,
                                                  input_var=settings_variable['browser_list'])
        self.inputs['txb_browser_list'].columnconfigure(0, weight=1)
        self.inputs['txb_browser_list'].grid(row=0, column=0, sticky=(tk.W + tk.E))

        self.inputs['txb_url_list'] = w.LabelInput(frame_web_info, "URL List:", input_class=w.ValidEntry,
                                                       input_var=settings_variable['url_list'])
        self.inputs['txb_url_list'].columnconfigure(0, weight=1)
        self.inputs['txb_url_list'].grid(row=1, column=0, sticky=(tk.W + tk.E))
        tk.Label(frame_web_info, text="Add list items separated by '||'").grid(row=3, column=0, sticky=(tk.W + tk.E))
        #############################
        # Create Mobile Settings Frame
        ############################
        frame_mobile_info = tk.LabelFrame(self, text="Mobile Settings")
        frame_mobile_info.columnconfigure(0, weight=1)
        frame_mobile_info.grid(row=3, sticky=(tk.W + tk.E), padx=10, pady=10)
        self.inputs['txb_device_list'] = w.LabelInput(frame_mobile_info, "Device List:", input_class=w.ValidEntry,
                                                       input_var=settings_variable['device_list'])
        self.inputs['txb_device_list'].columnconfigure(0, weight=1)
        self.inputs['txb_device_list'].grid(row=0, column=0, sticky=(tk.W + tk.E))

        self.inputs['txb_device_Server_list'] = w.LabelInput(frame_mobile_info, "Device Server List:", input_class=w.ValidEntry,
                                                   input_var=settings_variable['device_Server_list'])
        self.inputs['txb_device_Server_list'].columnconfigure(0, weight=1)
        self.inputs['txb_device_Server_list'].grid(row=1, column=0, sticky=(tk.W + tk.E))
        tk.Label(frame_mobile_info, text="Add list items separated by '||'").grid(row=3, column=0, sticky=(tk.W + tk.E))

        self.inputs['btn_save'] = w.LabelInput(self, "Save",
                                                 input_class=ttk.Button,
                                                 input_var=tk.StringVar(),
                                                 input_arg={'command': self.save})

        self.inputs['btn_save'].grid(row=4, column=0, sticky=(tk.W), padx=10)




    # Get the data for the all the Widgets
    def get(self):
        data = {}
        for key, widget in self.inputs.items():
            data[key] = widget.get()
        return data

    def get_errors(self):
        """Get a list of field errors in the form"""
        errors = {}
        for widgetName, widget in self.inputs.items():
            if hasattr(widget, "input") and hasattr(widget.input, 'trigger_focusout_validation'):
                widget.input.trigger_focusout_validation()
            if hasattr(widget, "error") and widget.error.get():
                errors[widgetName] = widget.error.get()
        return errors

    def save(self):
        self.destroy()
        self.callbacks['preference->save']()

