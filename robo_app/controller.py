from . import views as v
from . import models as m
from . import network as n
from tkinter import messagebox
import itertools
import webbrowser
import os
from . import robot_util as r
from .util import AppConfigParser
from .util import Bookmarks
from .util import RunTimeData
from .constants import AppConfig
import re
from sys import platform
from . import util as u
from collections import Counter
from numpy import add as num_py_add
from textwrap import wrap
import tkinter as tk
from .util import RobotLogger
from .constants import BatchStatus


class CreateBatchController:
    """The input form for the Batch Widgets"""

    def __init__(self, parent, *args, **kwargs):

        self.bookmark_dd = {}
        # self.load_bookmarks_data()
        self.logger = RobotLogger(__name__).logger
        callbacks = {'btn_createBatch': self.callback_create_batch2,
                     'btn_createBatch_Bookmark': self.cmd_insert_batch_details,
                     'SearchBtn': self.callback_search_script,
                     'AddSelected': self.callback_add_selected,
                     'cb_bookMark': self.callback_populate_bookmarked_tests,
                     'btn_createBookmark': self.callback_create_bookmark,
                     'btn_projLocation': self.call_back_select_folder,
                     'ckb_loadfrombookMark': self.call_back_on_select_load_book_marks}
        self.createbatch_view = v.CreateBatchForm(parent, callbacks, *args, **kwargs)
        self.batch_model = m.CreateBatchDetailsModel()
        proj_loc = self._get_project_location()
        RunTimeData().setdata('user_proj_location', proj_loc)
        self.tags = r.get_project_tags(proj_loc)
        self.createbatch_view.populate_data(proj_loc, list(self.bookmark_dd.keys()),
                                            self.tags)
        # self.createbatch_view.grid(row=1, column=0)

    def call_back_select_folder(self, folder_selected):
        # Update Config  File
        parser = AppConfigParser(AppConfig.user_config_file)
        parser.add_configuration(AppConfig.INI_APP_SETTING_SECTION, AppConfig.INI_PROJECT_LOCATION, folder_selected)
        # Update RunTime Data
        RunTimeData().setdata('user_proj_location', folder_selected)
        self.load_bookmarks_data()
        self.tags = r.get_project_tags(folder_selected)
        self.createbatch_view.populate_data(folder_selected, list(self.bookmark_dd.keys()),
                                            self.tags)

    def call_back_on_select_load_book_marks(self):
        self.load_bookmarks_data()
        self.createbatch_view.populate_data(self._get_project_location(), list(self.bookmark_dd.keys()), self.tags)

    def load_bookmarks_data(self):
        project_path = self._get_project_location()
        project_bookmark_file = os.path.join(project_path, 'bookmarks.json')
        user_bookmark_file = os.path.join(AppConfig.user_bookmarks_path, os.path.basename(project_path),
                                          'bookmarks.json')
        self.bookmark_dd = {}
        if os.path.isfile(project_bookmark_file):
            self.bookmark_dd = Bookmarks(project_bookmark_file).get_bookmarks()
        if os.path.isfile(user_bookmark_file):
            self.bookmark_dd.update(Bookmarks(user_bookmark_file).get_bookmarks())

    def callback_populate_bookmarked_tests(self, bm_name):
        """Callback for Loading BM Scripts"""
        test_list = self.bookmark_dd[bm_name]
        self.createbatch_view.insert_tests_to_batch2(test_list)

    def callback_search_script(self):
        """Callback when User hits Search"""
        folder_search_path = self.createbatch_view.get_selected_folder_path()
        tags_to_be_searched = self.createbatch_view.get_tags().split('|')
        test_list = r.get_robot_test_list(folder_search_path, test_tags=tags_to_be_searched)
        # self.createbatch_view.populate_scripts_table(test_list)
        self.createbatch_view.populate_scripts_table2(test_list)

    # Callback when User hits Add Selected
    def callback_add_selected(self):
        test_list = self.createbatch_view.get_selected_search_tests()
        # self.createbatch_view.insert_tests_to_batch(test_list)
        self.createbatch_view.insert_tests_to_batch2(test_list)

    def _get_project_location(self):
        parser = AppConfigParser(AppConfig.user_config_file)
        parser.readfile()
        proj_loc = parser.get_configuration_value(AppConfig.INI_APP_SETTING_SECTION, AppConfig.INI_PROJECT_LOCATION)
        if proj_loc:
            # return the Value
            return proj_loc
        else:
            return AppConfig.user_folder_path

    def callback_create_batch2(self):
        if len(self.createbatch_view.get_batch_tests()) > 0:

            widget_data = self.createbatch_view.get()
            batch_data = {'test_list': self.createbatch_view.get_batch_tests(),
                          'result_location': widget_data['tbx_resultLocation'],
                          'project_location': widget_data['txb_ProjectLocation']}

            CreateBatchDetailsController(self.createbatch_view, batch_data=batch_data)
        else:
            messagebox.showinfo("Create Batch Error",
                                "Are you sure you want to create empty batch. I don't think so. Please add some "
                                "scripts.",
                                parent=self.createbatch_view)

    def callback_create_bookmark(self):
        test_list = self.createbatch_view.get_batch_tests()
        proj_loc = os.path.realpath(self._get_project_location())
        for test in test_list:
            test['source'] = test['source'].replace(proj_loc, '').strip(os.path.sep)
        if len(test_list) > 0:
            self.createbookmark_controller = CreateBookMarkController(self.createbatch_view, test_list)
        else:
            messagebox.showinfo("Create Batch Error",
                                "Are you sure you want to create empty bookmark. I don't think so. Please add some "
                                "scripts.",
                                parent=self.createbatch_view)

    def cmd_insert_batch_details(self):

        error_list = self.createbatch_view.get_errors()

        # Removing the Rquired Error If its not Mobile App
        if self.createbatch_view.inputs['rb_applicationTypeWeb'].variable.get() != 'Mobile':
            error_list.pop('txb_mc_user_name', '')
            error_list.pop('txb_mc_user_pass', '')
        else:
            error_list.pop('lstbx_url_center', '')

        if len(error_list) == 0:
            """Controls Batch Creation"""
            batch_name = self.createbatch_view.inputs['txb_batchName'].variable.get()
            test_type = self.createbatch_view.inputs['rb_applicationTypeWeb'].variable.get()
            browser_device_list = self.createbatch_view.inputs['lstbx_device'].get_selected_values().replace("\n",
                                                                                                             ';') if \
                self.createbatch_view.inputs['rb_applicationTypeWeb'].variable.get() == 'Mobile' else \
                self.createbatch_view.inputs['lstbx_browser'].get_selected_values().replace("\n", ';')
            thread_count = self.createbatch_view.inputs['txb_batchNumberOfThreads'].variable.get()
            result_location = self.createbatch_view.inputs['tbx_resultLocation'].variable.get()
            project_location = self.createbatch_view.inputs['txb_ProjectLocation'].variable.get()
            batch_id = self.batch_model.cmd_insert_batch_details(batch_name, test_type, browser_device_list,
                                                                 thread_count, result_location, project_location)
            if batch_id:
                browser_device_list = itertools.cycle(browser_device_list.split(";"))
                test_list = self.createbatch_view.get_batch_tests()
                # self.batch_model.cmd_insert_scripts_in_batch(batch_id, browser_device_list, test_list)
                self.batch_model.cmd_insert_scripts_in_batch2(batch_id, browser_device_list, test_list)
                # Adding ALM and Mobile Center Components
                alm_test_plan = self.createbatch_view.inputs['txb_alm_plan_path'].variable.get()
                alm_test_lab = self.createbatch_view.inputs['txb_alm_lab_path'].variable.get()
                alm_test_set = self.createbatch_view.inputs['txb_alm_test_set_name'].variable.get()
                test_language = self.createbatch_view.inputs['rb_application_lang_EN'].variable.get()
                env_url = self.createbatch_view.inputs['lstbx_url_center'].variable.get()
                if self.createbatch_view.inputs['rb_applicationTypeWeb'].variable.get() == 'Mobile':
                    mc_server_url = self.createbatch_view.inputs['lstbx_mobile_center'].get()
                    mc_server_user = self.createbatch_view.inputs['txb_mc_user_name'].variable.get()
                    mc_server_pass = self.createbatch_view.inputs['txb_mc_user_pass'].variable.get()
                    self.batch_model.cmd_insert_command_variable(batch_id, alm_test_plan_path=alm_test_plan,
                                                                 alm_test_lab_path=alm_test_lab,
                                                                 alm_test_set_name=alm_test_set,
                                                                 test_lang=test_language, mc_server_url=mc_server_url,
                                                                 mc_server_user_name=mc_server_user,
                                                                 mc_server_user_pass=mc_server_pass,
                                                                 alm_url=AppConfig.ALM_URI + "/qcbin",
                                                                 alm_user=RunTimeData().getdata('alm_user'),
                                                                 alm_pass=RunTimeData().getdata('alm_password'),
                                                                 alm_domain=RunTimeData().getdata('alm_domain'),
                                                                 alm_proj=RunTimeData().getdata('alm_project'))
                else:
                    self.batch_model.cmd_insert_command_variable(batch_id, alm_test_plan_path=alm_test_plan,
                                                                 alm_test_lab_path=alm_test_lab,
                                                                 alm_test_set_name=alm_test_set,
                                                                 test_lang=test_language,
                                                                 alm_url=AppConfig.ALM_URI + "/qcbin",
                                                                 alm_user=RunTimeData().getdata('alm_user'),
                                                                 alm_pass=RunTimeData().getdata('alm_password'),
                                                                 alm_domain=RunTimeData().getdata('alm_domain'),
                                                                 alm_proj=RunTimeData().getdata('alm_project'),
                                                                 env_url=env_url)
                messagebox.showinfo('Batch Create', "Batch has been created with Batch ID:{}".format(batch_id),
                                    parent=self.createbatch_view)
            else:
                messagebox.showerror('Error', 'Unable to Create Batch')
            self.createbatch_view.inputs['win_batchdetails'].destroy()
        else:
            messagebox.showerror('Error', 'Hold On. Understand you are in Hurry but I think you forgot something',
                                 parent=self.createbatch_view)

    def get_device_list(self):
        patrn = "[\dA-Za-z-]+"
        file_loc = os.path.join(self.createbatch_view.inputs['txb_ProjectLocation'].variable.get(),
                                r'Resources/ConfigFiles/DeviceCapList.py')
        if not os.path.exists(file_loc):
            device_list = AppConfig.DEVICE_LIST
        else:
            with open(file_loc, 'r') as device_file:
                device_list = [re.findall(patrn, line[line.find("==") + 2:].strip())[0] for line in device_file
                               if 'arg1' in line and '==' in line]
        return device_list


class CreateBatchDetailsController:
    """The input form for the Create Batch Details"""

    def __init__(self, parent, batch_data, *args, **kwargs):
        self.logger = RobotLogger(__name__).logger
        self.batch_data = batch_data if batch_data else {}
        callbacks = {'btn_createBatch_Bookmark': self.callback_create_batch
                     }

        self.create_batch_details_view = v.CreateBatchDetailsForm(parent, callbacks, *args, **kwargs)
        self.create_batch_details_view.load_device_list(self.get_device_list())

        self.create_batch_details_model = m.CreateBatchDetailsModel()

    def get_device_list(self):
        patrn = "[\dA-Za-z-]+"
        file_loc = os.path.join(self.batch_data.get('project_location'),
                                r'Resources/ConfigFiles/DeviceCapList.py')
        if not os.path.exists(file_loc):
            device_list = AppConfig.DEVICE_LIST
        else:
            with open(file_loc, 'r') as device_file:
                device_list = [re.findall(patrn, line[line.find("==") + 2:].strip())[0] for line in device_file
                               if 'arg1' in line and '==' in line]
        return device_list

    # def load_gui(self):
    #     # Load Create Batch Details in UI
    #     self.populate_batch_data()
    #     self.batch_monitor_view.grid(row=1, column=0)

    def callback_create_batch(self):

        error_list = self.create_batch_details_view.get_errors()
        view_data = self.create_batch_details_view.get()
        # Removing the Rquired Error If its not Mobile App
        if view_data['rb_applicationTypeWeb'] == 'Web':
            error_list.pop('txb_mc_user_name', '')
            error_list.pop('txb_mc_user_pass', '')
        elif view_data['rb_applicationTypeWeb'] == 'Mobile':
            error_list.pop('lstbx_url_center', '')
        else:
            error_list.pop('lstbx_url_center', '')
            error_list.pop('txb_mc_user_name', '')
            error_list.pop('txb_mc_user_pass', '')

        if len(error_list) == 0:
            """Controls Batch Creation"""
            # browser_device_list = self.create_batch_details_view.inputs['lstbx_device'].get_selected_values().replace(
            #     "\n",
            #     ';') if \
            #     self.create_batch_details_view.inputs['rb_applicationTypeWeb'].variable.get() == 'Mobile' else \
            #     self.create_batch_details_view.inputs['lstbx_browser'].get_selected_values().replace("\n", ';')

            browser_device_list = view_data['lstbx_device'].replace("\n", ';') if view_data[
                                                                                      'rb_applicationTypeWeb'] == 'Mobile' else \
            view_data['lstbx_browser'].replace("\n", ';')

            self.batch_data['batch_name'] = view_data['txb_batchName']
            self.batch_data['test_type'] = view_data['rb_applicationTypeWeb']
            self.batch_data['browser_device_list'] = browser_device_list
            self.batch_data['thread_count'] = view_data['txb_batchNumberOfThreads']
            self.batch_data['user_name'] = RunTimeData().getdata('alm_user', RunTimeData().getdata('system_user'))
            batch_id = self.create_batch_details_model.cmd_insert_batch_details(self.batch_data)

            if batch_id:
                browser_device_list = itertools.cycle(browser_device_list.split(";"))
                test_list = self.batch_data.get('test_list', [])
                '''Inserting Scripts'''
                self.create_batch_details_model.insert_script(batch_id, browser_device_list, test_list)
                '''Inserting Commnad Variables'''

                self.create_batch_details_model.cmd_insert_command_variable(batch_id,
                                                                            alm_test_plan_path=view_data.get('txb_alm_plan_path', ''),
                                                                            alm_test_lab_path=view_data.get('txb_alm_lab_path',''),
                                                                            alm_test_set_name=view_data.get('txb_alm_test_set_name', ''),
                                                                            test_lang=view_data.get('rb_application_lang_EN', ''),
                                                                            mc_server_url=view_data.get('lstbx_mobile_center', ''),
                                                                            mc_server_user_name=view_data.get('txb_mc_user_name', ''),
                                                                            mc_server_user_pass=view_data.get('txb_mc_user_pass',''),
                                                                            env_url=view_data.get('lstbx_url_center', ''),
                                                                            alm_url=AppConfig.ALM_URI + "/qcbin",
                                                                            alm_user=RunTimeData().getdata(
                                                                                'alm_user'),
                                                                            alm_pass=RunTimeData().getdata(
                                                                                'alm_password'),
                                                                            alm_domain=RunTimeData().getdata(
                                                                                'alm_domain'),
                                                                            alm_proj=RunTimeData().getdata(
                                                                                'alm_project'))

                messagebox.showinfo('Batch Create', "Batch has been created with Batch ID:{}".format(batch_id),
                                    parent=self.create_batch_details_view)

                # # Adding ALM and Mobile Center Components
                # alm_test_plan = view_data['txb_alm_plan_path']
                # alm_test_lab = view_data['txb_alm_lab_path']
                # alm_test_set = view_data['txb_alm_test_set_name']
                # test_language = view_data['rb_application_lang_EN']
                # env_url = view_data['lstbx_url_center']
                #
                # if view_data['rb_applicationTypeWeb'] == 'Mobile':
                #     mc_server_url = self.create_batch_details_view.inputs['lstbx_mobile_center'].get()
                #     mc_server_user = view_data['txb_mc_user_name']
                #     mc_server_pass = view_data['txb_mc_user_pass']
                #     self.create_batch_details_model.cmd_insert_command_variable(batch_id,
                #                                                                 alm_test_plan_path=alm_test_plan,
                #                                                                 alm_test_lab_path=alm_test_lab,
                #                                                                 alm_test_set_name=alm_test_set,
                #                                                                 test_lang=test_language,
                #                                                                 mc_server_url=mc_server_url,
                #                                                                 mc_server_user_name=mc_server_user,
                #                                                                 mc_server_user_pass=mc_server_pass,
                #                                                                 alm_url=AppConfig.ALM_URI + "/qcbin",
                #                                                                 alm_user=RunTimeData().getdata(
                #                                                                     'alm_user'),
                #                                                                 alm_pass=RunTimeData().getdata(
                #                                                                     'alm_password'),
                #                                                                 alm_domain=RunTimeData().getdata(
                #                                                                     'alm_domain'),
                #                                                                 alm_proj=RunTimeData().getdata(
                #                                                                     'alm_project'))
                # else:
                #     self.create_batch_details_model.cmd_insert_command_variable(batch_id,
                #                                                                 alm_test_plan_path=alm_test_plan,
                #                                                                 alm_test_lab_path=alm_test_lab,
                #                                                                 alm_test_set_name=alm_test_set,
                #                                                                 test_lang=test_language,
                #                                                                 alm_url=AppConfig.ALM_URI + "/qcbin",
                #                                                                 alm_user=RunTimeData().getdata(
                #                                                                     'alm_user'),
                #                                                                 alm_pass=RunTimeData().getdata(
                #                                                                     'alm_password'),
                #                                                                 alm_domain=RunTimeData().getdata(
                #                                                                     'alm_domain'),
                #                                                                 alm_proj=RunTimeData().getdata(
                #                                                                     'alm_project'),
                #                                                                 env_url=env_url)
                # messagebox.showinfo('Batch Create', "Batch has been created with Batch ID:{}".format(batch_id),
                #                     parent=self.create_batch_details_view)
            else:
                messagebox.showerror('Error', 'Unable to Create Batch')
            self.create_batch_details_view.unload_gui()
        else:
            messagebox.showerror('Error', 'Hold On. Understand you are in Hurry but I think you forgot something',
                                 parent=self.create_batch_details_view)


class BatchMonitorController:
    """The input form for the Batch Widgets"""

    def __init__(self, parent, *args, **kwargs):
        self.logger = RobotLogger(__name__).logger
        callbacks = {'btn_open_selected': self.callback_open_selected,
                     'Open': self.callback_tree_open,
                     'Start': self.callback_tree_start,
                     'Stop': self.callback_tree_stop,
                     'Rerun': self.callback_tree_rerun,
                     'Update Details': self.callback_tree_update,
                     'btn_refresh': self.populate_batch_data,
                     'on_double_click': self.callback_tree_on_double_click,
                     'Clone Batch': self.callback_clone_batch}

        self.batch_monitor_view = v.BatchMonitor(parent, callbacks, *args, **kwargs)

        self.batch_monitor_model = m.BatchMonitorModel()
        self.batch_execution_monitor_controller = {}
        self.execution_threads = {}
        self.load_gui()


    def load_gui(self):
        # Load batches in UI
        self.populate_batch_data()
        # self.batch_monitor_view.grid(row=1, column=0)

    def populate_batch_data(self):
        batches = self.batch_monitor_model.get_batches()
        batches = [dict(batch) for batch in batches]    #Converting SQL lite Row into Dictonary
        for batch in batches:
            if batch['Batch_ID'] in self.execution_threads and self.execution_threads[batch['Batch_ID']].remaining_task()>0 :
                batch['Status'] = BatchStatus.RUNNING
            else:
                batch['Status'] = BatchStatus.NOT_RUNNING

        if batches:
            self.batch_monitor_view.populate_batch_information(batches)
        else:
            messagebox.showinfo("Batch Monitor", "No Batch Found")

    def callback_open_selected(self):
        row = self.batch_monitor_view.inputs['trv_batches'].get_selected_items()
        if not row:
            messagebox.showwarning("Batch Monitor", "Please Select a batch.")
            return

        if row[0]['Batch_ID'] not in self.batch_execution_monitor_controller:
            self.logger.info('Opening Batch ID:%s', row[0]['Batch_ID'])
            '''Open the window if not opened yet'''
            self.batch_execution_monitor_controller[row[0]['Batch_ID']] = BatchExecutionMonitorController(self.batch_monitor_view,
                                                                                          batch_id=row[0]['Batch_ID'])

        elif not bool(self.batch_execution_monitor_controller[row[0]['Batch_ID']].batch_exec_monitor_view.winfo_exists()):
            '''Open the window if closed'''
            self.batch_execution_monitor_controller[row[0]['Batch_ID']] = BatchExecutionMonitorController(self.batch_monitor_view,
                                                                                                batch_id=row[0][
                                                                                                    'Batch_ID'])
        else:
            self.batch_execution_monitor_controller[row[0]['Batch_ID']].lift_gui()

    def callback_tree_update(self):
        row = self.batch_monitor_view.inputs['trv_batches'].entries[
            self.batch_monitor_view.inputs['trv_batches'].cMenu.selection]
        callback = {'refresh': self.populate_batch_data}
        self.batch_update_controller = BatchUpdateController(self.batch_monitor_view, batch_id=row['Batch_ID'],
                                                             callbacks=callback)

    def callback_tree_open(self):
        row = self.batch_monitor_view.inputs['trv_batches'].entries[
            self.batch_monitor_view.inputs['trv_batches'].cMenu.selection]
        batch_id = row['Batch_ID']
        self.logger.info('Opening Batch ID:%s', batch_id)
        if batch_id and batch_id not in self.batch_execution_monitor_controller:
            '''Open the window if not opened yet'''
            self.batch_execution_monitor_controller[batch_id] = BatchExecutionMonitorController(self.batch_monitor_view,
                                                                                  batch_id=row['Batch_ID'])

        elif not bool(self.batch_execution_monitor_controller[batch_id].batch_exec_monitor_view.winfo_exists()):
            '''Open the window if closed'''
            self.batch_execution_monitor_controller[batch_id] = BatchExecutionMonitorController(self.batch_monitor_view,
                                                                                                batch_id=row[
                                                                                                    'Batch_ID'])
        else:
            self.batch_execution_monitor_controller[batch_id].lift_gui()

    def callback_tree_on_double_click(self):
        row = self.batch_monitor_view.inputs['trv_batches'].get_selected_items()[0]
        batch_id = row['Batch_ID']
        # self.logger.info('Opening Batch ID:%s', batch_id)
        self.logger.info('Opening Batch ID')
        if batch_id and batch_id not in self.batch_execution_monitor_controller:
            '''Open the window if not opened yet'''
            self.batch_execution_monitor_controller[batch_id] = BatchExecutionMonitorController(self.batch_monitor_view,
                                                                                   batch_id=row['Batch_ID'])
        elif not bool(self.batch_execution_monitor_controller[batch_id].batch_exec_monitor_view.winfo_exists()):
            '''Open the window if closed'''
            self.batch_execution_monitor_controller[batch_id] = BatchExecutionMonitorController(self.batch_monitor_view,
                                                                                                batch_id=row[
                                                                                                    'Batch_ID'])
        else:
            self.batch_execution_monitor_controller[batch_id].lift_gui()

    def callback_tree_rerun(self):
        row = self.batch_monitor_view.inputs['trv_batches'].entries[
            self.batch_monitor_view.inputs['trv_batches'].cMenu.selection]
        # self.batch_monitor_model.rerun_batch(row.Batch_ID)
        if messagebox.askokcancel('Batch Rerun', 'Are you sure that you want run Batch ID:{}. \n This will run all '
                                                 'the test in the batch.'.format(row['Batch_ID'])):
            if not self.execution_threads.get(row['Batch_ID'], None) or self.execution_threads.get(row['Batch_ID'],
                                                                                                   None).remaining_task() == 0:
                batch_details = self.batch_monitor_model.get_batch_details(row['Batch_ID'])[0]
                test_list = self.batch_monitor_model.get_scripts(row['Batch_ID'], re_run_scripts=True)
                self.execution_threads[row['Batch_ID']] = r.ExecutionPool(task_list=test_list,
                                                                          processes=batch_details['ThreadCount'])

                self.execution_threads[row['Batch_ID']].run_command()
            else:
                messagebox.showwarning("Batch Execution Monitor", "Batch is already running. Please try later after "
                                                                  "stopping the batch")

    def callback_tree_stop(self):
        row = self.batch_monitor_view.inputs['trv_batches'].entries[
            self.batch_monitor_view.inputs['trv_batches'].cMenu.selection]
        self.batch_monitor_model.stop_batch(row['Batch_ID'])
        if self.execution_threads.get(row['Batch_ID'], None):
            self.execution_threads[row['Batch_ID']].terminate_batch()
            # Remove the Batch From the Execution Thread
            self.execution_threads.pop(row['Batch_ID'])

    def callback_tree_start(self):
        row = self.batch_monitor_view.inputs['trv_batches'].entries[
            self.batch_monitor_view.inputs['trv_batches'].cMenu.selection]
        if messagebox.askokcancel('Batch Start', "Are you sure that you want run Batch ID:{}. \n This will run all "
                                                 "the test with Status 'Not Run' and 'Re Run' in the batch.".format(row['Batch_ID'])):
            if not self.execution_threads.get(row['Batch_ID'], None) or self.execution_threads.get(row['Batch_ID'],
                                                                                                   None).remaining_task() == 0:
                self.logger.info('Starting Execution of Batch:%s', row['Batch_ID'])
                batch_details = self.batch_monitor_model.get_batch_details(row['Batch_ID'])[0]
                test_list = self.batch_monitor_model.get_scripts(row['Batch_ID'])
                self.execution_threads[row['Batch_ID']] = r.ExecutionPool(task_list=test_list,
                                                                          processes=batch_details['ThreadCount'])

                self.execution_threads[row['Batch_ID']].run_command()

    def callback_clone_batch(self):
        row = self.batch_monitor_view.inputs['trv_batches'].entries[
            self.batch_monitor_view.inputs['trv_batches'].cMenu.selection]
        data_rows = self.batch_monitor_model.get_clone_data(row['Batch_ID'])
        # test_list = [{'name': row.name, 'doc': row.doc, 'tags': row.tags, 'source': row.source} for row in data_rows]

        batch_data = {'test_list': data_rows,
                      'result_location': data_rows[0]['result_Location'],
                      'project_location': data_rows[0]['project_Location']}
        CreateBatchDetailsController(self.batch_monitor_view, batch_data=batch_data)


class BatchExecutionMonitorController:
    """The input form for the Batch Execution Monitor Widgets"""

    def __init__(self, parent, batch_id, *args, **kwargs):
        # super().__init__(parent, *args, **kwargs)
        self.logger = RobotLogger(__name__).logger
        self.batch_id = batch_id
        self.logger = u.RobotLogger(__name__).logger
        callbacks = {'Open': self.callback_tree_open,
                     'Re-Run': self.callback_tree_re_run,
                     'Update': self.callback_tree_update,
                     'Stop': self.callback_tree_stop,
                     'Refresh': self.refresh_script,
                     'on_double_click': self.callback_tree_open_on_double_click}
        self.batch_exec_monitor_view = v.BatchExecutionMonitor(parent, callbacks, batch_id=self.batch_id, *args,
                                                               **kwargs)
        self.batch_exec_monitor_model = m.BatchExecutionMonitorModel()
        # Load batches details in UI
        self.load_gui()

    def load_gui(self):
        self._load_batch_information()
        self._load_scripts_information()

    def lift_gui(self):
        '''Funtion the show the view on the top if view already exists'''
        self.batch_exec_monitor_view.lift()

    def _load_batch_information(self):
        batch_data = self.batch_exec_monitor_model.get_batch_details(self.batch_id)

        passed_scripts = self.batch_exec_monitor_model.get_script_count_by_status(self.batch_id, "Passed")[
            'ScriptCount']
        failed_scripts = self.batch_exec_monitor_model.get_script_count_by_status(self.batch_id, "Failed")[
            'ScriptCount']

        self.batch_exec_monitor_view.load_batch_information(batch_data['Batch_Name'],
                                                            batch_data['CreationDate'],
                                                            batch_data['ScriptCount'],
                                                            passed_scripts, failed_scripts)

    def _load_scripts_information(self):

        scripts = self.batch_exec_monitor_model.get_test_scripts(self.batch_id)
        if scripts:
            self.batch_exec_monitor_view.load_scripts_information(scripts)
        else:
            messagebox.showinfo("Batch Execution Monitor", "No Scripts Found")

    def refresh_script(self):
        scripts = self.batch_exec_monitor_model.get_test_scripts(self.batch_id)
        if scripts:
            self.batch_exec_monitor_view.refresh_scripts(scripts)

        else:
            messagebox.showinfo("Batch Execution Monitor", "No Scripts Found")

    def callback_tree_open(self):
        # if self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection != "":
        row = self.batch_exec_monitor_view.inputs['trv_batchScripts'].entries[
            self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection]
        if row['Log_path'] and os.path.exists(row['Log_path']):
            self.logger.debug("Log File Path:%s", row['Log_path'])
            if platform == 'darwin':
                log_path = "file:///" + row['Log_path']
            else:
                log_path = row['Log_path']
            webbrowser.open(log_path)
        else:
            messagebox.showinfo("Log Not Found", "Log file not found.")

    def callback_tree_open_on_double_click(self):
        row = self.batch_exec_monitor_view.inputs['trv_batchScripts'].get_selected_items()[0]
        if row['Log_path'] and os.path.exists(row['Log_path']):
            self.logger.debug("Log File Path:%s", row['Log_path'])
            if platform == 'darwin':
                log_path = "file:///" + row['Log_path']
            else:
                log_path = row['Log_path']
            webbrowser.open(log_path)
        else:
            messagebox.showinfo("Log Not Found", "Log file not found.")

    def callback_tree_re_run(self):
        if self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection != "":
            row = self.batch_exec_monitor_view.inputs['trv_batchScripts'].entries[
                self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection]
            self.batch_exec_monitor_model.rerun_script(row['RUN_ID'])
            messagebox.showinfo("Test Updated", "Test is marked as Re-run.\nThis will not start the execution."
                                "In order to start execution of this test, Go to 'Batch Monitor-->Right Click->Start'")
            self.refresh_script()
            self._load_batch_information()

    def callback_tree_update(self):
        if self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection != "":
            row = self.batch_exec_monitor_view.inputs['trv_batchScripts'].entries[
                self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection]
            # callback = {'refresh': self.refresh_script}
            callback = {}
            self.script_update_controller = ScriptUpdateController(self.batch_exec_monitor_view, self.batch_id,
                                                                   row['RUN_ID'], callbacks=callback)

    def callback_tree_stop(self):
        if self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection != "":
            row = self.batch_exec_monitor_view.inputs['trv_batchScripts'].entries[
                self.batch_exec_monitor_view.inputs['trv_batchScripts'].cMenu.selection]
            self.batch_exec_monitor_model.stop_script(row['RUN_ID'])
            self.refresh_script()
            self._load_batch_information()


class BatchUpdateController:
    """The input form for the Batch Execution Monitor Widgets"""

    def __init__(self, parent, batch_id, callbacks=None, *args, **kwargs):
        self.logger = RobotLogger(__name__).logger
        self.batch_id = batch_id
        self.callbacks = callbacks if callbacks else {}
        self.callbacks['btn_update'] = self.callback_update_batch_details
        self.batch_update_view = v.BatchUpdate(parent, self.callbacks, batch_id=self.batch_id, *args, **kwargs)
        self.batch_update_model = m.BatchUpdateModel()
        device_list = self.get_device_list()
        self.batch_update_view.populate(self.batch_update_model.get_batch(self.batch_id)[0], device_list)

    def callback_update_batch_details(self):
        try:
            error_list = self.batch_update_view.get_errors()
            data = self.batch_update_view.get()
            if data['rb_applicationTypeWeb'] != 'Mobile':
                error_list.pop('txb_mc_user_name', '')
                error_list.pop('txb_mc_user_pass', '')
            if len(error_list) > 0:
                messagebox.showerror("Missing Values", "Please provide all the details")
            else:
                # Get the Data from the Widgets

                device_browser_list = data['lstbx_device'] if data['rb_applicationTypeWeb'] == 'Mobile' else data[
                    'lstbx_browser']
                bol_batch_update = self.batch_update_model.cmd_update_batch_details(self.batch_id,
                                                                                    data['rb_applicationTypeWeb'],
                                                                                    device_browser_list,
                                                                                    data['txb_batchNumberOfThreads'])
                bol_var_update = self.batch_update_model.cmd_update_command_variable(self.batch_id,
                                                                                     data['txb_alm_plan_path'],
                                                                                     data['txb_alm_lab_path'],
                                                                                     data['txb_alm_test_set_name'],
                                                                                     data['rb_application_lang_FR'],
                                                                                     data['lstbx_mobile_center'],
                                                                                     data['txb_mc_user_name'],
                                                                                     data['txb_mc_user_pass'],
                                                                                     env_url=data['lstbx_url_center'])

                bol_script_update = self.batch_update_model.cmd_update_tests(self.batch_id,
                                                                             device_browser_list.split(';'))
                self.batch_update_view.destroy()
                if bol_batch_update and bol_var_update and bol_script_update:
                    messagebox.showinfo("Success!!", "Batch has been updated")
        except Exception as e:
            messagebox.showerror("Unable to Update", "Please contact Dev's.")

    def get_device_list(self):
        project_path = self.batch_update_model.get_batch(self.batch_id)[0]["Project_Location"]
        patrn = "[\dA-Za-z-]+"
        file_loc = os.path.join(project_path, r'Resources/ConfigFiles/DeviceCapList.py')
        if not os.path.exists(file_loc):
            # file_loc = 'robo_app/devicelist.txt'
            # with open(file_loc, 'r') as file:
            #     device_list = [re.findall(patrn, line)[0] for line in file]
            device_list = AppConfig.DEVICE_LIST
        else:
            with open(file_loc, 'r') as device_file:
                device_list = [re.findall(patrn, line[line.find("==") + 2:].strip())[0] for line in device_file
                               if 'arg1' in line and '==' in line]
        return device_list


class ScriptUpdateController:
    """The input form for the Batch Execution Monitor Widgets"""

    def __init__(self, parent, batch_id, run_id, callbacks=None, *args, **kwargs):
        # super().__init__(parent, *args, **kwargs)
        self.logger = RobotLogger(__name__).logger
        self.batch_id = batch_id
        self.run_id = run_id
        self.callbacks = callbacks if callbacks else {}
        self.callbacks['btn_update'] = self.callback_update_script_details
        self.script_update_view = v.ScriptUpdate(parent, self.callbacks, self.run_id, *args, **kwargs)

        self.script_update_model = m.ScriptUpdateModel()
        device_list = self.get_device_list()

        self.script_update_view.populate(self.script_update_model.get_test_details(self.run_id), device_list)

    def callback_update_script_details(self):
        try:
            error_list = self.script_update_view.get_errors()
            data = self.script_update_view.get()
            if data['rb_applicationTypeWeb'] != 'Mobile':
                error_list.pop('txb_mc_user_name', '')
                error_list.pop('txb_mc_user_pass', '')
            if len(error_list) > 0:
                messagebox.showerror("Missing Values", "Please provide all the details")
            else:
                # Get the Data from the Widgets
                data = self.script_update_view.get()
                device_browser_list = data['lstbx_device'] if data['rb_applicationTypeWeb'] == 'Mobile' else data[
                    'lstbx_browser']
                bol_script_update = self.script_update_model.cmd_update_test(self.run_id, device_browser_list)

                self.script_update_view.destroy()
                if bol_script_update:
                    messagebox.showinfo("Sucess!!", "Script has been updated")
        except Exception as e:
            messagebox.showerror("Unable to Update", "Please contact Dev's.")

    def get_device_list(self):
        project_path = self.script_update_model.get_batch(self.batch_id)["Project_Location"]
        patrn = "[\dA-Za-z-]+"
        file_loc = os.path.join(project_path, r'Resources/ConfigFiles/DeviceCapList.py')
        if not os.path.exists(file_loc):
            device_list = AppConfig.DEVICE_LIST
        else:
            with open(file_loc, 'r') as device_file:
                device_list = [re.findall(patrn, line[line.find("==") + 2:].strip())[0] for line in device_file
                               if 'arg1' in line and '==' in line]
        return device_list


class CreateBookMarkController():
    """The input form for the Batch Execution Monitor Widgets"""

    def __init__(self, parent, tests_list, *args, **kwargs):
        self.logger = RobotLogger(__name__).logger
        callbacks = {'btn_createBookMark': self.callback_create_bm}
        self.create_bookmark_view = v.CreateBookMark(parent, callbacks, *args, **kwargs)
        self.create_bookmark_model = m.CreateBookMarkModel()
        self.tests_list = tests_list
        # logging.info("project loc : {}".format(self.proj_location))

    def callback_create_bm(self):
        error_list = self.create_bookmark_view.get_errors()
        view_data = self.create_bookmark_view.get()
        data_dict = {}
        if len(error_list) == 0:
            """Controls Batch Creation"""
            bm_name = view_data['txb_bookmarkName']
            data_dict[bm_name] = self.tests_list
            try:
                if self.create_bookmark_model.exiting_bookmark(bm_name):
                    if (messagebox.askokcancel(title="Existing BookMark Update",
                                               message="You are trying to update existing Bookmarks.Are you sure?",
                                               parent=self.create_bookmark_view)):
                        pass_word = self.create_bookmark_view.load_admin_ui()
                        if pass_word == 'Pr1y@':
                            if self.create_bookmark_model.add_project_book_mark(data_dict):
                                messagebox.showinfo("Sucess!!", "Bookmark has been created/updated.",
                                                    parent=self.create_bookmark_view)
                                self.create_bookmark_view.destroy()
                        elif pass_word is not None:
                            messagebox.showerror('Password Miss-matched',
                                                 'Please enter correct Password', parent=self.create_bookmark_view)
                            self.create_bookmark_view.grab_set()
                            self.create_bookmark_view.lift()
                else:

                    if self.create_bookmark_model.add_user_book_mark(data_dict):
                        messagebox.showinfo("Success!!", "Bookmark has been created/updated.",
                                            parent=self.create_bookmark_view)
                        self.create_bookmark_view.destroy()
            except Exception as e:
                messagebox.showerror('Error', 'Unable to Create BookMark. Please Contact Dev Team',
                                     parent=self.create_bookmark_view)

        else:
            messagebox.showerror('Error', 'Hold On. Understand you are in Hurry but I think you forgot something',
                                 parent=self.create_bookmark_view)


class ALMLoginController:
    """Controller for ALM Login Screen"""

    def __init__(self, parent, *args, **kwargs):
        self.domain_dd = {}
        self.logger = RobotLogger(__name__).logger
        callbacks = {'btn_authenticate': self.callback_authenicate,
                     'btn_login': self.callback_login,
                     'file->quit': self.callback_quit,
                     'options->use_alm': self.callback_use_aml,
                     'options->preferences': self.callback_preference
                     }
        """For Menu Login"""
        self.settings_model = m.SettingsModel()
        self.load_settings()

        self.login_view = v.AlmLoginForm(parent, callbacks, self.settings, *args, **kwargs)
        self.login_model = n.ALM_API(AppConfig.ALM_URI)

    def callback_quit(self):
        self.login_view.quit()

    def callback_authenicate(self):
        """Callback function to control the Authentication"""
        error_list = self.login_view.get_errors()
        view_data = self.login_view.get()
        if len(error_list) == 0:
            """Controls Authentication"""

            try:
                if self.login_model.authenticate(view_data['txb_user_name'], view_data['txb_user_pass']):
                    messagebox.showinfo("Success", "Successfully logged In.", parent=self.login_view)
                    self.domain_dd = self.login_model.get_domain_mapping()
                    self.login_view.populate(self.domain_dd)
                else:
                    messagebox.showerror('Error', 'Unable to Authenticate. Please check your ALM user/password',
                                         parent=self.login_view)
            except Exception as e:
                messagebox.showerror('Error', 'Unable to Authenticate. Please Contact Dev Team', parent=self.login_view)
        else:
            messagebox.showerror('Error', 'Hold On. Understand you are in Hurry but I think you forgot something',
                                 parent=self.login_view)

    def callback_login(self):
        """Callback for Login"""
        error_list = self.login_view.get_errors()
        view_data = self.login_view.get()
        if len(error_list) == 0:
            """Controls Login"""
            try:
                if self.login_model.authenticate(view_data['txb_user_name'],
                                                 view_data['txb_user_pass']) and view_data['cb_domain'] != '' and \
                        view_data['cb_project'] != '':
                    self.login_view.destroy()
                    RunTimeData().setdata('alm_user', view_data.get('txb_user_name', None))
                    RunTimeData().setdata('alm_password', view_data.get('txb_user_pass', None))
                    RunTimeData().setdata('alm_domain', view_data.get('cb_domain', None))
                    RunTimeData().setdata('alm_project', view_data.get('cb_project', None))
                else:
                    messagebox.showerror('Error', 'Unable to Authenticate. Please check your ALM Details',
                                         parent=self.login_view)
            except Exception as e:
                messagebox.showerror('Error', 'Unable to Authenticate. Please Contact Dev Team',
                                     parent=self.login_view)
        else:
            messagebox.showerror('Error', 'Hold On. Understand you are in Hurry but I think you forgot something',
                                 parent=self.login_view)

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
        self.login_view.quit()


    def callback_preference(self):
        """Call back function for the Preferences"""
        v.Preferences(self.login_view, self.settings, {'preference->save': self.callback_save_preference})

    def callback_save_preference(self):
        """Load new configuration"""
        self.load_configurations()


class StatisticsController:
    """The input form for the Batch Widgets"""
    stats_type = ['Test Execution', 'Test Created', 'Project Statistics']

    def __init__(self, parent, *args, **kwargs):
        self.logger = RobotLogger(__name__).logger
        callbacks = {'generate_report': self.callback_generate_report,
                     'cb_on_select_stats': self.callback_on_select_stats}
        self.stats_view = v.StatisticsForm(parent, callbacks, self.stats_type, *args, **kwargs)
        self.stats_model = m.StatisticsModel()

    def callback_generate_report(self):
        form_data = self.stats_view.get()
        if form_data['cb_select_stats'] == 'Test Execution':
            self._generate_test_execution_stats()
        elif form_data['cb_select_stats'] == 'Project Statistics':
            self._generate_project_stats()

        elif form_data['cb_select_stats'] == 'Test Created':
            self._generate_test_creation_stats()

    def _generate_test_execution_stats(self):
        form_data = self.stats_view.get()
        data_records = self.stats_model.get_test_execution_data(u.format_date(form_data['tb_from_date']),
                                                                u.format_date(form_data['tb_to_date']))
        if len(data_records) != 0:
            batch_data = Counter([data['Batch_ID'] for data in data_records])
            script_status = Counter([data['Status'] for data in data_records])
            stats_data = {'Total Batch': len(batch_data.keys()),
                          'Total Test': sum(batch_data.values()),
                          'Total Passed': script_status[r.ScriptStatus.PASSED],
                          'Total Failed': script_status[r.ScriptStatus.FAIL],
                          'Total No Run': script_status[r.ScriptStatus.NOT_RUN],
                          'Total Re-Run': script_status[r.ScriptStatus.RERUN],
                          'Total Running': script_status[r.ScriptStatus.RUNNING],
                          'Total Stopped': script_status[r.ScriptStatus.STOPPED]}
            self.stats_view.populate_statistics_data(stats_data)
            self.stats_view.populate_report_table(data_records=data_records)

            """Adding bar graph"""

            batches = list(batch_data.keys())
            passed = []
            failed = []
            not_run = []
            re_run = []

            for batch in batches:
                passed.append(len([data for data in data_records if
                                   data['Batch_ID'] == batch and data['Status'] == r.ScriptStatus.PASSED]))
                failed.append(len([data for data in data_records if
                                   data['Batch_ID'] == batch and data['Status'] == r.ScriptStatus.FAIL]))
                not_run.append(len([data for data in data_records if
                                    data['Batch_ID'] == batch and data['Status'] == r.ScriptStatus.NOT_RUN]))
                re_run.append(len([data for data in data_records if
                                   data['Batch_ID'] == batch and data['Status'] == r.ScriptStatus.RERUN]))

            bar_data = [{'x': batches, 'height': passed, 'width': .23, 'label': 'Passed'},
                        {'x': batches, 'height': failed, 'width': .23, 'label': 'Failed',
                         'bottom': passed}
                        ]
            total_bottom = num_py_add(passed, failed)
            bar_data.append({'x': batches, 'height': not_run, 'width': .23, 'label': 'Not Run',
                             'bottom': total_bottom})

            total_bottom = num_py_add(total_bottom, not_run)
            bar_data.append({'x': batches, 'height': re_run, 'width': .23, 'label': 'Re Run',
                             'bottom': total_bottom})
            self.stats_view.add_bar_to_chart('Test Execution', 'Batches', '# Test Cases', bar_data)

        else:
            messagebox.showerror('Error', 'No Record Found. Please change the selection',
                                 parent=self.stats_view)

    def _generate_test_creation_stats(self):
        form_data = self.stats_view.get()
        data_records = self.stats_model.get_test_creation_data(u.format_date(form_data['tb_from_date']),
                                                               u.format_date(form_data['tb_to_date']))
        if len(data_records) != 0:
            stats_data = {'Total Scripts': len(data_records)}
            self.stats_view.populate_statistics_data(stats_data)
            self.stats_view.populate_report_table(data_records=data_records)
            # Bar Graph Data
            script_sources = Counter([data['Source'] for data in data_records])
            # file_names = [file.split(os.sep)[-1] for file in script_sources.keys()]
            file_names = ['\n'.join(wrap(file.split(os.sep)[-1], 15)) for file in script_sources.keys()]
            bar_data = []
            for source, count in script_sources.items():
                bar_data.append({'x': file_names, 'height': count, 'width': .23})
            self.stats_view.add_bar_to_chart('Test Created', 'Source', '# Test Cases', bar_data)
        else:
            messagebox.showerror('Error', 'No Record Found. Please change the selection',
                                 parent=self.stats_view)

    def _generate_project_stats(self):
        data_records = r.get_project_stats(RunTimeData().getdata('user_proj_location'))
        if len(data_records) != 0:
            stats_data = {'Total Test Cases': sum([data['Test Cases'] for data in data_records]),
                          'Total Keywords': sum([data['Keywords'] for data in data_records])}
            self.stats_view.populate_statistics_data(stats_data)
            self.stats_view.populate_report_table(data_records=data_records)
            '''Bar Data'''
            file_names = [data['File Name'] for data in data_records]
            file_names = ['\n'.join(wrap(name, 15)) for name in file_names]
            keywords = [data['Keywords'] for data in data_records]
            test_cases = [data['Test Cases'] for data in data_records]

            bar_data = [{'x': file_names, 'height': test_cases, 'width': .23, 'label': 'Test Cases'},
                        {'x': file_names, 'height': keywords, 'width': .23, 'label': 'keywords',
                         'bottom': test_cases}
                        ]
            self.stats_view.add_bar_to_chart('Project Statstics', 'File Name', 'Test Cases/ Keywords', bar_data)

    def callback_on_select_stats(self, selected_value):
        if selected_value == 'Project Statistics':
            self.stats_view.set_date_fields_visibility(False)
        else:
            self.stats_view.set_date_fields_visibility(True)
