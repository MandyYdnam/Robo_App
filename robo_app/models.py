from .constants import FieldTypes as FT
from .constants import DatabaseConfig
import sqlite3
from collections import namedtuple
import itertools
from .constants import AppConfig
from .util import AppConfigParser
import os
from .util import Bookmarks
import logging


class Robo_Executor_SQLLiteDB():
    def __init__(self, db_name=DatabaseConfig.sqllite_db_location):
        self.db_name = db_name

    def open_connection(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = self._named_tuple_factory
        self.curs = self.connection.cursor()

    def _named_tuple_factory(self,cursor, row):
        """
            Usage:
            con.row_factory = namedtuple_factory
            """
        fields = [col[0] for col in cursor.description]
        Row = namedtuple("Row", fields)
        return Row(*row)

    def run_sql(self, sql_query, commit=False):
        self.connection.row_factory= self._named_tuple_factory
        self.curs.execute(sql_query)
        if commit:
            self.connection.commit()
        return self.curs.fetchall()

    def insert_To_db(self,table_name, kwargs):
        if kwargs:
            # sql_string="Insert Into {}({}) VALUES({})".format(table_name, ",".join(kwargs.keys()),",".join(kwargs.values()))
            #
            # # print(sql_string)
            # self.curs.execute(sql_string)

            # sql_string = "Insert Into {}({}) VALUES({})".format(table_name, ",".join(kwargs.keys()),
            #                                                     ",".join(kwargs.values()))
            # print(",".join(kwargs.keys()))
            # print(",".join(kwargs.values()))
            sql_string = "Insert Into {}({}) VALUES({})".format(table_name,",".join(kwargs.keys()), ",".join('?'* len(kwargs.keys())))
            # print(sql_string)
            values = tuple(kwargs.values())
            # print(values)
            self.curs.execute(sql_string,values)
            self.connection.commit()
        else:
            print('Incorrect SQL Format. Missing SQL kwargs:' )
        return self.curs.lastrowid

    def close_connection(self):
        if self.connection:
            self.connection.close()

    def insert_batch(self, kwargs):
        batch_id = self.insert_To_db("tbl_batch", kwargs)
        if batch_id:
           return batch_id
        else:
            raise NameError("Unable to Create Batch")


    def insert_script(self, kwargs):
        self.insert_To_db("tbl_scripts", kwargs)

    def run_update_sql(self, sql_querry, commit=False):
        self.connection.row_factory= self._named_tuple_factory
        self.curs.execute(sql_querry)
        if commit:
            self.connection.commit()
        return self.curs.rowcount

class InitializeModel:
    fields = {
        "Name": {'req':True, 'type': FT.string},
        "DeviceList":{'req':False, 'type':FT.string_list, 'values':[]},
        "BrowserList":{'req':False, 'type':FT.string_list, 'values':['Chrome','Internet Explorer', 'FireFox']},
        "TestType" : {'req':True, 'type':FT.string},
        "BatchCreationDate":{'req': True, 'type': FT.dateTime},
        "ThreadsCount" : {'req':True, 'type' : FT.integer, 'min': 0, 'max': 4},
        "Batch_ID": {'req': True, 'type': FT.integer}
    }

    def __init__(self):
        self.db_con = Robo_Executor_SQLLiteDB()



    def is_batch_table(self):
        try:
            self.db_con.open_connection()
            sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_batch'"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def is_script_table(self):
        try:
            self.db_con.open_connection()
            sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_scripts'"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def is_command_var_table(self):
        try:
            self.db_con.open_connection()
            sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_command_variables'"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def cmd_create_batch_table(self):
        try:
            self.db_con.open_connection()
            sql_query = """CREATE TABLE "tbl_batch" (
	"Batch_ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"TestType"	VARCHAR(255),
	"Browsers_OR_Devices"	VARCHAR(255),
	"CreationDate"	TEXT DEFAULT CURRENT_TIMESTAMP,
	"ThreadCount"	INTEGER,
	"Batch_Name"	TEXT,
	"Result_Location"	TEXT,
	"Project_Location"	TEXT
)"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def cmd_create_scripts_table(self):
        try:
            self.db_con.open_connection()
            sql_query = """CREATE TABLE "tbl_scripts" (
	"Script_ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"ScriptName"	VARCHAR(255),
	"Documentation"	TEXT,
	"Source"	VARCHAR(255),
	"Tag"	VARCHAR(255),
	"Status"	VARCHAR(255),
	"StartTime"	DATETIME,
	"End_Time"	DATETIME,
	"Device_Browser"	VARCHAR(255),
	"Run_Count"	INTEGER,
	"Log_path"	VARCHAR(255),
	"Batch_ID"	INTEGER,
	FOREIGN KEY("Batch_ID") REFERENCES "tbl_batch"("Batch_ID")
)"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def cmd_create_command_var_table(self):
        try:
            self.db_con.open_connection()
            sql_query = """CREATE TABLE "tbl_command_variables" (
	"ENV_MC_SERVER"	VARCHAR(255),
	"ENV_MC_USER_NAME"	VARCHAR(255),
	"ENV_MC_USER_PASS"	VARCHAR(255),
	"ENV_LANGUAGE"	VARCHAR(255),
	"ENV_URL"	TEXT,
	"ALMTestSetName"	TEXT,
	"ALMTestLabPath"	TEXT,
	"ALMTestPlanPath"	TEXT,
	"Batch_ID"	INTEGER,
	"AlmUrl"	NUMERIC,
	"almuserid"	TEXT,
	"almuserpswd"	TEXT,
	"almdomain"	TEXT,
	"almproject"	TEXT,
	FOREIGN KEY("Batch_ID") REFERENCES "tbl_batch"("Batch_ID")
)"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

class BatchModel:
    fields = {
        "Name": {'req':True, 'type': FT.string},
        "DeviceList":{'req':False, 'type':FT.string_list, 'values':[]},
        "BrowserList":{'req':False, 'type':FT.string_list, 'values':['Chrome','Internet Explorer', 'FireFox']},
        "TestType" : {'req':True, 'type':FT.string},
        "BatchCreationDate":{'req': True, 'type': FT.dateTime},
        "ThreadsCount" : {'req':True, 'type' : FT.integer, 'min': 0, 'max': 4},
        "Batch_ID": {'req': True, 'type': FT.integer}
    }

    def __init__(self):
        self.db_con = Robo_Executor_SQLLiteDB()

    def cmd_insert_batch_details(self, batch_name, test_type, browser_device_list, thread_count, result_location,
                                 project_location):

        try:
            self.db_con.open_connection()
            batchID = self.db_con.insert_batch(
                {'Batch_Name': "{}".format(batch_name),
                 'TestType': "{}".format(test_type),
                 'Browsers_OR_Devices': "{}".format(browser_device_list),
                 'Result_Location': "{}".format(result_location),
                 'Project_Location': "{}".format(project_location),
                 'ThreadCount': "{}".format(thread_count)})
            return batchID

        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def cmd_insert_scripts_in_batch(self, batch_id, browser_device_list, test_list):
        """Insert Scripts in the Batch"""

        try:
            self.db_con.open_connection()
            device_browser_generator = itertools.cycle(browser_device_list)
            for test in test_list:
                self.db_con.insert_script({'ScriptName': "{}".format(test.name),
                                      'Documentation': "{}".format(test.doc),
                                      'Source': "{}".format(test.source),
                                      'Tag': "{}".format(";".join(test.tags)),
                                      'Status': "No Run",
                                      'Device_Browser': "{}".format(next(device_browser_generator)),
                                      'Run_Count': "0",
                                      'Batch_ID': str(batch_id)})

            return True
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()


    def cmd_insert_scripts_in_batch2(self, batch_id, browser_device_list, test_list):
        """Insert Scripts in the Batch"""
        """Takes Test as List"""

        try:
            self.db_con.open_connection()
            device_browser_generator = itertools.cycle(browser_device_list)
            for test in test_list:
                # print(test)
                self.db_con.insert_script({'ScriptName': "{}".format(test['name']),
                                      'Documentation': "{}".format((test['doc'])),
                                      'Source': "{}".format(test['source']),
                                      'Tag': "{}".format(test['tags']),
                                      'Status': "No Run",
                                      'Device_Browser': "{}".format(next(device_browser_generator)),
                                      'Run_Count': "0",
                                      'Batch_ID': str(batch_id)})

            return True
        except Exception as e:
            logging.error('Exception occured', exc_info=True)
            print(e)
        finally:
            self.db_con.close_connection()

    def cmd_insert_command_variable(self, batch_id, alm_test_plan_path, alm_test_lab_path, alm_test_set_name,
                                    test_lang, alm_url, alm_user, alm_pass, alm_domain, alm_proj,
                                    mc_server_url='', mc_server_user_name='', mc_server_user_pass='', env_url=''):
        """Command line Variable for Batch"""

        try:
            self.db_con.open_connection()

            self.db_con.insert_To_db("tbl_command_variables",{'ALMTestPlanPath': "{}".format(alm_test_plan_path),
                                                              'ALMTestLabPath': "{}".format(alm_test_lab_path),
                                                              'ALMTestSetName': "{}".format(alm_test_set_name),
                                                              'ENV_MC_SERVER': "{}".format(mc_server_url),
                                                              'ENV_MC_USER_NAME': "{}".format(mc_server_user_name),
                                                              'ENV_MC_USER_PASS': "{}".format(mc_server_user_pass),
                                                              'ENV_URL':'{}'.format(env_url),
                                                              'ENV_LANGUAGE':"{}".format(test_lang),
                                                              'AlmUrl':"{}".format(alm_url),
                                                              'almuserid':"{}".format(alm_user),
                                                              'almuserpswd':"{}".format(alm_pass),
                                                              'almdomain':"{}".format(alm_domain),
                                                              'almproject':"{}".format(alm_proj),
                                                              'Batch_ID': str(batch_id)})

            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self.db_con.close_connection()


class BatchMonitorModel:
    fields = {
        "Name": {'req':True, 'type': FT.string},
        "DeviceList":{'req':False, 'type':FT.string_list, 'values':[]},
        "BrowserList":{'req':False, 'type':FT.string_list, 'values':['Chrome','Internet Explorer', 'FireFox']},
        "TestType" : {'req':True, 'type':FT.string},
        "BatchCreationDate":{'req': True, 'type': FT.dateTime},
        "ThreadsCount" : {'req':True, 'type' : FT.integer, 'min': 0, 'max': 4},
        "Batch_ID": {'req': True, 'type': FT.integer}
    }

    def __init__(self):
        self.db_con = Robo_Executor_SQLLiteDB()

    def get_batches(self, MaxRows=20):
        """Update All No Run Scripts to Stop"""
        try:
            self.db_con.open_connection()
            sql_query = """Select tbl_batch.Batch_ID, Batch_Name, CreationDate, ThreadCount, TestType, Browsers_OR_Devices , COUNT(tbl_scripts.Script_ID) AS ScriptCount from tbl_batch LEFT JOIN tbl_scripts ON tbl_batch.Batch_ID=tbl_scripts.Batch_ID GROUP BY tbl_batch.Batch_ID, Batch_Name, CreationDate, ThreadCount, TestType, Browsers_OR_Devices ORDER BY tbl_batch.Batch_ID DESC"""
            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def stop_batch(self, batch_id):

        try:
            self.db_con.open_connection()
            sql_query = "Update tbl_scripts SET Status ='Stopped' WHERE batch_id={} AND Status IN ('No Run','Re Run','Running')".format(batch_id)
            return self.db_con.run_sql(sql_query, commit=True)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()

    def rerun_batch(self, batch_id):

        try:
            self.db_con.open_connection()
            sql_query = "Update tbl_scripts SET Status ='Re Run' WHERE batch_id={}".format(batch_id)
            return self.db_con.run_sql(sql_query, commit=True)
        except Exception as e:
            print( e)
        finally:
            self.db_con.close_connection()

    def get_scripts(self,batch_id,re_run_scripts=False):
        try:
            self.db_con.open_connection()
            if not re_run_scripts:
                sql_query = "Select tbl_batch.Batch_ID, tbl_batch.Result_Location, tbl_batch.ThreadCount,tbl_batch.TestType,tbl_batch.Project_Location ,tbl_scripts.ScriptName,tbl_scripts.Device_Browser,tbl_scripts.Source,tbl_command_variables.ENV_MC_SERVER,tbl_command_variables.ENV_MC_USER_NAME,tbl_command_variables.ENV_MC_USER_PASS,tbl_command_variables.ENV_URL,tbl_command_variables.ENV_LANGUAGE,tbl_command_variables.ALMTestPlanPath,tbl_command_variables.ALMTestLabPath,tbl_command_variables.ALMTestSetName, tbl_command_variables.AlmUrl, tbl_command_variables.almuserid, tbl_command_variables.almuserpswd,tbl_command_variables.almdomain, tbl_command_variables.almproject from tbl_batch ,tbl_scripts,tbl_command_variables  WHERE tbl_batch.Batch_ID=tbl_scripts.Batch_ID  AND tbl_batch.Batch_ID=tbl_command_variables.Batch_ID AND tbl_batch.Batch_ID={}".format(batch_id)
            else:
                sql_query = "Select tbl_batch.Batch_ID, tbl_batch.Result_Location, tbl_batch.ThreadCount,tbl_batch.TestType, tbl_batch.Project_Location, tbl_scripts.ScriptName,tbl_scripts.Device_Browser,tbl_scripts.Source,tbl_command_variables.ENV_MC_SERVER,tbl_command_variables.ENV_MC_USER_NAME,tbl_command_variables.ENV_MC_USER_PASS,tbl_command_variables.ENV_URL,tbl_command_variables.ENV_LANGUAGE,tbl_command_variables.ALMTestPlanPath,tbl_command_variables.ALMTestLabPath,tbl_command_variables.ALMTestSetName,tbl_command_variables.AlmUrl,tbl_command_variables.almuserid,tbl_command_variables.almuserpswd,tbl_command_variables.almdomain,tbl_command_variables.almproject from tbl_batch ,tbl_scripts, tbl_command_variables  WHERE tbl_batch.Batch_ID=tbl_scripts.Batch_ID  AND tbl_batch.Batch_ID=tbl_command_variables.Batch_ID  AND tbl_scripts.Status NOT IN ('Passed', 'Failed','Stopped') AND tbl_batch.Batch_ID={}".format(batch_id)

            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print( e)
        finally:
            self.db_con.close_connection()

    def get_batch_details(self,batch_id):
        try:
            self.db_con.open_connection()
            sql_query = "Select* from tbl_batch WHERE  tbl_batch.Batch_ID={}".format(batch_id)

            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print( e)
        finally:
            self.db_con.close_connection()

    def get_commnad_variables(self,batch_id):
        try:
            self.db_con.open_connection()
            sql_query = "SELECT ENV_MC_SERVER, ENV_MC_USER_NAME, ENV_MC_USER_PASS, ENV_LANGUAGE, ENV_URL, ALMTestPlanPath, ALMTestLabPath, ALMTestSetName FROM tbl_command_variables WHERE Batch_ID={}".format(batch_id)

            return self.db_con.run_sql(sql_query)
        except Exception as e:
            print( e)
            return False
        finally:
            self.db_con.close_connection()


class BatchExecutionMonitorModel:

    def __init__(self):
        self.db_con = Robo_Executor_SQLLiteDB()


    def get_batch_details(self, batch_id, MaxRows=20):
        """Get batch Data by batch ID"""
        try:
            self.db_con.open_connection()
            sql_query = 'Select tbl_batch.Batch_ID, Batch_Name, CreationDate, ThreadCount, Browsers_OR_Devices , COUNT(tbl_scripts.Script_ID) AS ScriptCount from tbl_batch LEFT JOIN tbl_scripts ON tbl_batch.Batch_ID=tbl_scripts.Batch_ID  GROUP BY tbl_batch.Batch_ID, Batch_Name, CreationDate, ThreadCount, TestType, Browsers_OR_Devices HAVING tbl_scripts.Batch_ID=?'
            return self.db_con.curs.execute(sql_query,(batch_id,)).fetchone()
        except:
            return False
        finally:
            self.db_con.close_connection()


    def get_script_count_by_status(self, batch_id, status='Passed'):
        """Get batch Data by batch ID"""
        try:
            self.db_con.open_connection()
            sql_query = """Select  COUNT(tbl_scripts.Status) AS ScriptCount from tbl_scripts WHERE Status = ? AND tbl_scripts.Batch_ID=?"""
            return self.db_con.curs.execute(sql_query,(status, batch_id,)).fetchone()
        except Exception as e:
            return e
        finally:
            self.db_con.close_connection()

    def get_test_scripts(self,batch_id,  MaxRows=500):
        """Get the All the Scripts by batch Id"""
        try:
            self.db_con.open_connection()
            sql_query = 'Select Script_ID,ScriptName, Documentation, Source, Status, StartTime , End_Time, Device_Browser, Run_Count, Log_path from tbl_scripts WHERE tbl_scripts.Batch_ID=?'
            return self.db_con.curs.execute(sql_query,(batch_id,)).fetchall()
        except Exception as e:
            return e
        finally:
            self.db_con.close_connection()

    def stop_script(self, batch_id, script_id):
        """Stops the Script based on ID"""
        try:
            self.db_con.open_connection()
            sql_query = "Update tbl_scripts SET Status ='Stopped' WHERE batch_id={} AND Script_ID={} AND Status IN ('No Run','Re Run','Running')".format(batch_id,script_id)

            return self.db_con.run_sql(sql_query, commit=True)
        except Exception as e:
            return e
        finally:
            self.db_con.close_connection()
    def rerun_script(self, batch_id, script_id):
        """Stops the Script based on ID"""
        try:
            self.db_con.open_connection()
            sql_query = "Update tbl_scripts SET Status ='Re Run'  WHERE batch_id={} AND Script_ID={}".format(batch_id, script_id)

            return self.db_con.run_sql(sql_query, commit=True)
        except Exception as e:
            print(e)
        finally:
            self.db_con.close_connection()


class BatchUpdateModel:

    def __init__(self):
        self.db_con = Robo_Executor_SQLLiteDB()

    def cmd_update_batch_details(self,batch_id, test_type, browser_device_list, thread_count):

        try:
            self.db_con.open_connection()

            sql_query="UPDATE tbl_batch SET TestType=?, ThreadCount=?,Browsers_OR_Devices=? WHERE Batch_ID=?"
            data_tup = (test_type, thread_count, browser_device_list, batch_id)
            self.db_con.curs.execute(sql_query, data_tup)
            self.db_con.connection.commit()
            return self.db_con.curs.rowcount
        except Exception as e:
            if self.db_con:
                self.db_con.connection.rollback()
                print(e)
                raise (e)
        finally:
            self.db_con.close_connection()

    def cmd_update_command_variable(self, batch_id, alm_test_plan_path, alm_test_lab_path, alm_test_set_name,

                                    test_lang, mc_server_url='', mc_server_user_name='', mc_server_user_pass='', env_url=''):
        try:
            self.db_con.open_connection()

            sql_query = "UPDATE tbl_command_variables SET ENV_MC_SERVER=?, ENV_MC_USER_NAME=?, ENV_MC_USER_PASS=?, ENV_LANGUAGE=?, ALMTestPlanPath=?, ALMTestLabPath=?, ALMTestSetName=?, ENV_URL=? WHERE Batch_ID=?"
            data_tup = (mc_server_url, mc_server_user_name, mc_server_user_pass, test_lang, alm_test_plan_path,
                        alm_test_lab_path, alm_test_set_name, env_url, batch_id)
            self.db_con.curs.execute(sql_query, data_tup)
            self.db_con.connection.commit()
            return self.db_con.curs.rowcount
        except Exception as e:
            if self.db_con:
                self.db_con.connection.rollback()
                print(e)
                raise (e)
        finally:
            self.db_con.close_connection()

    def cmd_update_scripts(self, batch_id, device_browser_list):
        try:
            self.db_con.open_connection()

            #Get Script to be updated for batch
            sql_query = 'Select Script_ID from tbl_scripts WHERE tbl_scripts.Batch_ID=?'
            scripts= self.db_con.curs.execute(sql_query, (batch_id,)).fetchall()
            device_browser_generator = itertools.cycle(device_browser_list)
            for script in scripts:
                sql_query = "UPDATE tbl_scripts SET Device_Browser=? WHERE Script_ID=?"
                data_tup = (next(device_browser_generator),script.Script_ID)
                self.db_con.curs.execute(sql_query, data_tup)

            self.db_con.connection.commit()
            return self.db_con.curs.rowcount
        except Exception as e:
            if self.db_con:
                self.db_con.connection.rollback()
                print(e)
                raise (e)
        finally:
            self.db_con.close_connection()

    def get_batch(self, batch_id):
        try:
            self.db_con.open_connection()
            sql_query = "SELECT tbl_batch.Batch_Name, tbl_batch.ThreadCount, tbl_batch.Project_Location, tbl_batch.TestType, tbl_command_variables.ENV_LANGUAGE, tbl_command_variables.ENV_URL, tbl_command_variables.ALMTestLabPath,tbl_command_variables.ALMTestPlanPath,tbl_command_variables.ALMTestSetName,tbl_command_variables.ENV_MC_SERVER,tbl_command_variables.ENV_MC_USER_NAME,tbl_command_variables.ENV_MC_USER_PASS FROM tbl_batch,tbl_command_variables WHERE tbl_batch.Batch_ID=tbl_command_variables.Batch_ID AND tbl_batch.Batch_ID={}".format(batch_id)
            return self.db_con.run_sql(sql_query, commit=True)

        except Exception as e:
            print( e)
        finally:
            self.db_con.close_connection()



class ScriptUpdateModel:

    def __init__(self):
        self.db_con = Robo_Executor_SQLLiteDB()

    def cmd_update_script(self, script_id, device_browser):
        try:
            self.db_con.open_connection()

            sql_query = "UPDATE tbl_scripts SET Device_Browser=? WHERE Script_ID=?"
            data_tup = (device_browser,script_id)
            self.db_con.curs.execute(sql_query, data_tup)

            self.db_con.connection.commit()
            return self.db_con.curs.rowcount
        except Exception as e:
            if self.db_con:
                self.db_con.connection.rollback()
                print(e)
                raise (e)
        finally:
            self.db_con.close_connection()

    def get_script_details(self, script_id):
        try:
            self.db_con.open_connection()
            sql_query = "SELECT tbl_scripts.ScriptName, tbl_batch.TestType, tbl_command_variables.ALMTestLabPath, tbl_command_variables.ALMTestPlanPath, tbl_command_variables.ALMTestSetName, tbl_command_variables.ENV_LANGUAGE,tbl_command_variables.ENV_URL, tbl_command_variables.ENV_MC_SERVER, tbl_command_variables.ENV_MC_USER_NAME, tbl_command_variables.ENV_MC_USER_PASS FROM tbl_batch, tbl_command_variables, tbl_scripts WHERE tbl_batch.Batch_ID=tbl_scripts.Batch_ID AND tbl_scripts.Batch_ID=tbl_command_variables.Batch_ID AND tbl_scripts.Script_ID={}".format(script_id)
            return self.db_con.run_sql(sql_query, commit=True)

        except Exception as e:
            print( e)
        finally:
            self.db_con.close_connection()

    def get_batch(self, batch_id):
        try:
            self.db_con.open_connection()
            sql_query = "SELECT tbl_batch.Batch_Name, tbl_batch.ThreadCount, tbl_batch.Project_Location, tbl_batch.TestType, tbl_command_variables.ENV_LANGUAGE, tbl_command_variables.ENV_URL, tbl_command_variables.ALMTestLabPath,tbl_command_variables.ALMTestPlanPath,tbl_command_variables.ALMTestSetName,tbl_command_variables.ENV_MC_SERVER,tbl_command_variables.ENV_MC_USER_NAME,tbl_command_variables.ENV_MC_USER_PASS FROM tbl_batch,tbl_command_variables WHERE tbl_batch.Batch_ID=tbl_command_variables.Batch_ID AND tbl_batch.Batch_ID={}".format(batch_id)
            return self.db_con.run_sql(sql_query, commit=True)

        except Exception as e:
            print( e)
        finally:
            self.db_con.close_connection()


class CreateBookMarkModel:
    def __init__(self, project_bm_file=None, user_bm_file=None):
        self.project_bm_file= project_bm_file or os.path.join(self._get_project_location(),'bookmarks.json')
        self.user_bm_file = user_bm_file or os.path.join(AppConfig.user_bookmarks_path, os.path.basename(self._get_project_location()),'bookmarks.json')
        self.project_bm_dd = Bookmarks(self.project_bm_file)
        self.user_bm_dd = Bookmarks(self.user_bm_file)


    def _get_project_location(self):
        parser = AppConfigParser(AppConfig.user_config_file)
        parser.readfile()
        if parser.has_option(AppConfig.INI_APP_SETTING_SECTION, AppConfig.INI_PROJECT_LOCATION):
            #return the Value
            return parser[AppConfig.INI_APP_SETTING_SECTION][AppConfig.INI_PROJECT_LOCATION]
        else:
            return AppConfig.user_folder_path

    def exiting_bookmark(self, bm_name):
        return bm_name in self.project_bm_dd.get_bookmarks()

    def add_project_book_mark(self, data_dict):
        return self.project_bm_dd.update_bookmarks(data_dict)

    def add_user_book_mark(self, data_dict):
        base_dir = os.path.dirname(self.user_bm_file)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return  self.user_bm_dd.update_bookmarks(data_dict)

