from .constants import DatabaseConfig
import sqlite3
import itertools
from .constants import AppConfig
from .util import AppConfigParser
import os
from .util import Bookmarks
import sqlite3 as sq
import logging
from .util import RunTimeData
from .util import RobotLogger
from .robot_util import ScriptStatus
import json



class Robo_Executor_SQLLiteDB():

    def __init__(self, db_name=DatabaseConfig.sqllite_db_location):
        self.db_name = db_name
        self.connection = None
        self.curs = None
        self.logger = RobotLogger(__name__).logger

    def open_connection(self):
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        self.curs = self.connection.cursor()

    def run_sql(self, sql_query, commit=False):
        self.curs.execute(sql_query)
        if commit:
            self.connection.commit()
        return self.curs.fetchall()

    def insert_To_db(self, table_name, kwargs):
        if kwargs:
            sql_string = "Insert Into {}({}) VALUES({})".format(table_name, ",".join(kwargs.keys()),
                                                                ",".join('?' * len(kwargs.keys())))
            self.logger.debug("Sql String%s", sql_string)
            values = tuple(kwargs.values())
            self.logger.debug(values)
            self.curs.execute(sql_string, values)
            self.connection.commit()
        else:
            self.logger.error('Incorrect SQL Format. Missing SQL kwargs:')
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

    def run_update_sql(self, sql_query, commit=False):
        self.connection.row_factory = self._named_tuple_factory
        self.curs.execute(sql_query)
        if commit:
            self.connection.commit()
        return self.curs.rowcount

    def query(self, query, parameters=None):
        try:
            self.curs.execute(query, parameters)

        except sqlite3.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()
            if self.curs.description is not None:
                return self.curs.fetchall()


class InitializeModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def update_query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.rowcount is not None:
            return cursor.rowcount

    def is_batch_table(self):
        try:
            sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_batch'"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def is_script_table(self):
        try:
            sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_scripts'"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def is_command_var_table(self):
        try:
            sql_query = """SELECT name FROM sqlite_master WHERE type='table' AND name='tbl_command_variables'"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_batch_table(self):
        try:
            sql_query = """CREATE TABLE "tbl_batch" (
	"Batch_ID"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	"TestType"	VARCHAR(255),
	"Browsers_OR_Devices"	VARCHAR(255),
	"CreationDate"	TEXT DEFAULT CURRENT_TIMESTAMP,
	"ThreadCount"	INTEGER,
	"Batch_Name"	TEXT,
	"Result_Location"	TEXT,
	"Project_Location"	TEXT,
	"USER_NAME"	TEXT,
	FOREIGN KEY("USER_NAME") REFERENCES "tbl_users"("USER_NAME")
)"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_scripts_table(self):
        try:
            sql_query = """CREATE TABLE "tbl_scripts" (
	"Script_ID"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"ScriptName"	VARCHAR(255),
	"Documentation"	TEXT,
	"Source"	VARCHAR(255),
	"Tag"	VARCHAR(255),
	"CreationDate"	TEXT DEFAULT CURRENT_TIMESTAMP
)"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_command_var_table(self):
        try:
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

            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_user_table(self):
        try:
            sql_query = """CREATE TABLE "tbl_users" (
	"USER_NAME"	TEXT NOT NULL UNIQUE,
	"EMAIL"	TEXT,
	"LAST_LOGIN"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("USER_NAME")
);"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_test_run_table(self):
        try:
            sql_query = """CREATE TABLE "tbl_testruns" (
	"RUN_ID"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	"Script_ID"	INTEGER,
	"Batch_ID"	INTEGER,
	"Status"	VARCHAR(255),
	"Start_Time"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"End_Time"	DATETIME,
	"Device_Browser"	VARCHAR(255),
	"Log_Path"	TEXT,
	"USER_NAME"	TEXT,
	"Run_Count"	INTEGER DEFAULT 0,
	FOREIGN KEY("USER_NAME") REFERENCES "tbl_users"("USER_NAME"),
	FOREIGN KEY("Script_ID") REFERENCES "tbl_scripts"("Script_ID"),
	FOREIGN KEY("Batch_ID") REFERENCES "tbl_batch"("Batch_ID")
)"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def add_user_details(self, user_data):
        try:
            user_query = 'SELECT * FROM tbl_users WHERE USER_NAME=?'
            user_query_result = self.query(user_query, (user_data['user_name'],))
            if not user_query_result:
                sql_query = "INSERT INTO tbl_users (USER_NAME,EMAIL) VALUES (?,?)"
                self.query(sql_query, (user_data['user_name'], user_data.get('user_email', None)))
            else:
                sql_query = "UPDATE tbl_users SET LAST_LOGIN=CURRENT_TIMESTAMP WHERE USER_NAME=?"
                return self.update_query(sql_query, (user_data['user_name'],))
        except Exception as e:
            raise e

    def cmd_create_test_run_index(self):
        try:
            sql_query = """CREATE INDEX "indx_test_runs" ON "tbl_testruns" (
	"Script_ID"	ASC,
	"Batch_ID"	ASC,
	"RUN_ID"	ASC,
	"Start_Time"	ASC
);"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_scripts_index(self):
        try:
            sql_query = """CREATE INDEX "indx_scripts" ON "tbl_scripts" (
	"ScriptName"	ASC,
	"Source"	ASC
);"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

    def cmd_create_batch_index(self):
        try:
            sql_query = """CREATE INDEX "indx_batch" ON "tbl_batch" (
	"Batch_ID"	ASC
);"""
            return self.query(sql_query, ())
        except Exception as e:
            raise e

class CreateBatchDetailsModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def cmd_insert_batch_details(self, batch_data):
        try:
            db_query = 'INSERT INTO tbl_batch (Batch_Name,TestType,Browsers_OR_Devices,Result_Location,Project_Location,User_Name, ThreadCount) VALUES(?,?,?,?,?,?,?)'
            cur = self.connection.cursor()
            cur.execute(db_query, (batch_data['batch_name'],
                                   batch_data['test_type'],
                                   batch_data['browser_device_list'],
                                   batch_data['result_location'],
                                   batch_data['project_location'],
                                   batch_data['user_name'],
                                   batch_data['thread_count']))

            return cur.lastrowid
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

    def insert_script(self, batch_id, browser_device_list, test_list):
        """Update All No Run Scripts to Stop"""
        try:

            device_browser_generator = itertools.cycle(browser_device_list)
            for test in test_list:
                sql_query = "SELECT * FROM tbl_scripts WHERE ScriptName=? AND Source LIKE ?"

                script_result = self.query(sql_query, (test['name'], '%' + test['source']))
                if not script_result:
                    query = "INSERT INTO tbl_scripts(ScriptName,Documentation,Source,Tag) VALUES (?,?,?,?)"
                    self.query(query, (test['name'], test['doc'], test['source'], test['tags']))

                script_result = self.query(sql_query, (test['name'], '%' + test['source']))
                # Insert Data into Run Table
                test_run_query = "INSERT INTO tbl_testruns (Script_ID,Batch_ID,Status,Device_Browser,USER_NAME) VALUES (?,?,?,?,?)"
                self.query(test_run_query, (script_result[0]['Script_ID'],
                                            batch_id,
                                            'Not Run',
                                            next(device_browser_generator),
                                            RunTimeData().getdata('alm_user', RunTimeData().getdata('system_user'))))
        except Exception as e:
            self.logger.error(e)
            raise e

    def cmd_insert_command_variable(self, batch_id, alm_test_plan_path, alm_test_lab_path, alm_test_set_name,
                                    test_lang, alm_url, alm_user, alm_pass, alm_domain, alm_proj,
                                    mc_server_url='', mc_server_user_name='', mc_server_user_pass='', env_url=''):
        """Command line Variable for Batch"""

        try:
            db_query = 'INSERT INTO tbl_command_variables(ALMTestPlanPath,ALMTestLabPath,ALMTestSetName,ENV_MC_SERVER,ENV_MC_USER_NAME,ENV_MC_USER_PASS,ENV_URL,ENV_LANGUAGE,AlmUrl,almuserid,almuserpswd,almdomain,almproject,Batch_ID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            self.query(db_query, (alm_test_plan_path,
                                  alm_test_lab_path,
                                  alm_test_set_name,
                                  mc_server_url,
                                  mc_server_user_name,
                                  mc_server_user_pass,
                                  env_url,
                                  test_lang,
                                  alm_url,
                                  alm_user,
                                  alm_pass,
                                  alm_domain,
                                  alm_proj,
                                  str(batch_id)))

            return True
        except Exception as e:
            self.logger.error(e)
            return False


class BatchMonitorModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def get_batches(self, MaxRows=20):
        """Update All No Run Scripts to Stop"""
        try:
            sql_query = """Select tbl_batch.Batch_ID, Batch_Name, CreationDate, ThreadCount, TestType, Browsers_OR_Devices , COUNT(tbl_testruns.Script_ID) AS ScriptCount from tbl_batch LEFT JOIN tbl_testruns ON tbl_batch.Batch_ID=tbl_testruns.Batch_ID GROUP BY tbl_batch.Batch_ID, Batch_Name, CreationDate, ThreadCount, TestType, Browsers_OR_Devices ORDER BY tbl_batch.Batch_ID DESC"""
            return self.query(sql_query, ())
        except Exception as e:
            self.logger.error(e)
            raise e

    def stop_batch(self, batch_id):
        try:
            sql_query = "Update tbl_testruns SET Status =? WHERE batch_id=? AND Status IN (?,?,?)"
            return self.query(sql_query, (ScriptStatus.STOPPED, batch_id, ScriptStatus.NOT_RUN, ScriptStatus.RERUN,
                                          ScriptStatus.RUNNING))
        except Exception as e:
            self.logger.error(e)
            raise e

    def rerun_batch(self, batch_id):

        try:
            sql_query = "Update tbl_testruns SET Status =? WHERE batch_id=?"
            return self.query(sql_query, (ScriptStatus.RERUN, batch_id))
        except Exception as e:
            self.logger.error(e)
            raise e

    def get_scripts(self, batch_id, re_run_scripts=False):
        try:

            if re_run_scripts:
                sql_query = """Select 
tbl_batch.Batch_ID, 
tbl_batch.Result_Location, 
tbl_batch.ThreadCount,
tbl_batch.TestType,
tbl_batch.Project_Location ,
tbl_scripts.ScriptName,
tbl_testruns.Device_Browser,
tbl_testruns.RUN_ID,
tbl_scripts.Source,
tbl_command_variables.ENV_MC_SERVER,
tbl_command_variables.ENV_MC_USER_NAME,
tbl_command_variables.ENV_MC_USER_PASS,
tbl_command_variables.ENV_URL,
tbl_command_variables.ENV_LANGUAGE,
tbl_command_variables.ALMTestPlanPath,
tbl_command_variables.ALMTestLabPath,
tbl_command_variables.ALMTestSetName,
tbl_command_variables.AlmUrl,
tbl_command_variables.almuserid,
tbl_command_variables.almuserpswd,
tbl_command_variables.almdomain,
tbl_command_variables.almproject 

from 
tbl_batch ,tbl_scripts,tbl_command_variables,tbl_testruns

WHERE 
tbl_batch.Batch_ID=tbl_testruns.Batch_ID 
AND 
tbl_batch.Batch_ID=tbl_command_variables.Batch_ID 
AND 
tbl_testruns.Script_ID=tbl_scripts.Script_ID 
AND 
tbl_batch.Batch_ID={}""".format(
                    batch_id)
            else:
                sql_query = """Select 
tbl_batch.Batch_ID, 
tbl_batch.Result_Location, 
tbl_batch.ThreadCount,
tbl_batch.TestType, 
tbl_batch.Project_Location, 
tbl_scripts.ScriptName,
tbl_testruns.Device_Browser,
tbl_testruns.RUN_ID,
tbl_scripts.Source,
tbl_command_variables.ENV_MC_SERVER,
tbl_command_variables.ENV_MC_USER_NAME,
tbl_command_variables.ENV_MC_USER_PASS,
tbl_command_variables.ENV_URL,
tbl_command_variables.ENV_LANGUAGE,
tbl_command_variables.ALMTestPlanPath,
tbl_command_variables.ALMTestLabPath,
tbl_command_variables.ALMTestSetName,
tbl_command_variables.AlmUrl,
tbl_command_variables.almuserid,
tbl_command_variables.almuserpswd,
tbl_command_variables.almdomain,
tbl_command_variables.almproject 
FROM
tbl_batch ,tbl_scripts, tbl_command_variables,tbl_testruns
WHERE tbl_batch.Batch_ID=tbl_testruns.Batch_ID  
AND 
tbl_batch.Batch_ID=tbl_command_variables.Batch_ID 
AND 
tbl_testruns.Script_ID=tbl_scripts.Script_ID 
AND 
tbl_testruns.Status NOT IN ('{}','{}','{}') 
AND tbl_batch.Batch_ID={}""".format(ScriptStatus.PASSED, ScriptStatus.FAIL, ScriptStatus.STOPPED, batch_id)

            return self.query(sql_query, ())
        except Exception as e:
            self.logger.error(e)
            raise e

    def get_clone_data(self, batch_id):
        try:
            sql_query = "SELECT ScriptName as 'name', Documentation as 'doc', Tag as 'tags', Source as 'source', tbl_batch.Result_Location as 'result_Location',tbl_batch.Project_Location as 'project_Location' FROM tbl_scripts, tbl_batch, tbl_testruns WHERE tbl_batch.Batch_ID=tbl_testruns.Batch_ID AND tbl_testruns.Script_ID=tbl_scripts.Script_ID AND tbl_batch.Batch_ID={}".format(
                batch_id)
            return self.query(sql_query, ())
        except Exception as e:
            self.logger.error(e)
            raise e

    def get_batch_details(self, batch_id):
        try:
            sql_query = "Select* from tbl_batch WHERE tbl_batch.Batch_ID={}".format(batch_id)

            return self.query(sql_query, ())
        except Exception as e:
            self.logger.error(e)
            raise


class BatchExecutionMonitorModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def get_batch_details(self, batch_id, MaxRows=20):
        """Get batch Data by batch ID"""
        try:
            sql_query = """Select 
tbl_batch.Batch_ID, 
Batch_Name, 
CreationDate, 
ThreadCount, 
Browsers_OR_Devices , 
COUNT(tbl_testruns.RUN_ID) AS ScriptCount 
from 
tbl_batch LEFT JOIN tbl_testruns 
ON 
tbl_batch.Batch_ID=tbl_testruns.Batch_ID  
GROUP BY 
tbl_batch.Batch_ID, 
Batch_Name, 
CreationDate, 
ThreadCount, 
TestType, 
Browsers_OR_Devices 
HAVING 
tbl_testruns.Batch_ID=?"""
            result = self.query(sql_query, (batch_id,))
            return result[0] if result else {}

        except:
            return False

    def get_script_count_by_status(self, batch_id, status=ScriptStatus.PASSED):
        """Get batch Data by batch ID"""
        try:

            sql_query = """Select  COUNT(tbl_testruns.Status) AS ScriptCount from tbl_testruns WHERE Status = ? AND tbl_testruns.Batch_ID=?"""
            result = self.query(sql_query, (status, batch_id,))
            return result[0] if result else {}
        except Exception as e:
            return e

    def get_test_scripts(self, batch_id, MaxRows=500):
        """Get the All the Scripts by batch Id"""
        try:
            sql_query = """Select 
tbl_testruns.RUN_ID,            
tbl_testruns.Script_ID,
ScriptName, 
Documentation, 
Source, 
Status, 
Start_Time , 
End_Time, 
Device_Browser, 
Run_Count, 
Log_path from tbl_testruns, tbl_scripts 
WHERE 
tbl_testruns.Script_ID=tbl_scripts.Script_ID
AND
tbl_testruns.Batch_ID=?"""
            return self.query(sql_query, (batch_id,))
        except Exception as e:
            return e

    def stop_script(self, run_id):
        """Stops the Script based on ID"""
        try:
            sql_query = "Update tbl_testruns SET Status =? WHERE RUN_ID=? AND Status IN (?,?,?)"
            return self.query(sql_query, (ScriptStatus.STOPPED, run_id, ScriptStatus.NOT_RUN,
                                          ScriptStatus.RERUN,
                                          ScriptStatus.RUNNING))

        except Exception as e:
            return e

    def rerun_script(self, run_id):
        """Stops the Script based on ID"""
        try:
            sql_query = "Update tbl_testruns SET Status =?  WHERE RUN_ID=?"
            return self.query(sql_query, (ScriptStatus.RERUN, run_id))
        except Exception as e:
            self.logger.error(e)


class BatchUpdateModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def update_query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.rowcount is not None:
            return cursor.rowcount

    def cmd_update_batch_details(self, batch_id, test_type, browser_device_list, thread_count):

        try:

            sql_query = "UPDATE tbl_batch SET TestType=?, ThreadCount=?,Browsers_OR_Devices=? WHERE Batch_ID=?"
            data_tup = (test_type, thread_count, browser_device_list, batch_id)
            return self.update_query(sql_query, data_tup)

        except Exception as e:
            raise e

    def cmd_update_command_variable(self, batch_id, alm_test_plan_path, alm_test_lab_path, alm_test_set_name,

                                    test_lang, mc_server_url='', mc_server_user_name='', mc_server_user_pass='',
                                    env_url=''):
        try:

            sql_query = "UPDATE tbl_command_variables SET ENV_MC_SERVER=?, ENV_MC_USER_NAME=?, ENV_MC_USER_PASS=?, ENV_LANGUAGE=?, ALMTestPlanPath=?, ALMTestLabPath=?, ALMTestSetName=?, ENV_URL=? WHERE Batch_ID=?"
            data_tup = (mc_server_url, mc_server_user_name, mc_server_user_pass, test_lang, alm_test_plan_path,
                        alm_test_lab_path, alm_test_set_name, env_url, batch_id)
            return self.update_query(sql_query, data_tup)

        except Exception as e:
            raise e

    def cmd_update_tests(self, batch_id, device_browser_list):
        try:

            # Get Script to be updated for batch
            sql_query = 'Select RUN_ID from tbl_testruns WHERE tbl_testruns.Batch_ID=?'
            scripts = self.query(sql_query, (batch_id,))
            device_browser_generator = itertools.cycle(device_browser_list)
            records_updated = 0
            for script in scripts:
                sql_query = "UPDATE tbl_testruns SET Device_Browser=? WHERE RUN_ID=?"
                data_tup = (next(device_browser_generator), script['RUN_ID'])
                records_updated = records_updated + self.update_query(sql_query, data_tup)
            return records_updated
        except Exception as e:
            raise e

    def get_batch(self, batch_id):
        try:

            sql_query = """SELECT 
tbl_batch.Batch_Name, 
tbl_batch.ThreadCount, 
tbl_batch.Project_Location, 
tbl_batch.TestType, 
tbl_command_variables.ENV_LANGUAGE, 
tbl_command_variables.ENV_URL, 
tbl_command_variables.ALMTestLabPath,
tbl_command_variables.ALMTestPlanPath,
tbl_command_variables.ALMTestSetName,
tbl_command_variables.ENV_MC_SERVER,
tbl_command_variables.ENV_MC_USER_NAME,
tbl_command_variables.ENV_MC_USER_PASS 
FROM tbl_batch,tbl_command_variables 
WHERE 
tbl_batch.Batch_ID=tbl_command_variables.Batch_ID 
AND tbl_batch.Batch_ID=?"""
            return self.query(sql_query, (batch_id,))

        except Exception as e:
            raise e


class ScriptUpdateModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def update_query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.rowcount is not None:
            return cursor.rowcount


    def cmd_update_test(self, run_id, device_browser):
        try:
            sql_query = "UPDATE tbl_testruns SET Device_Browser=? WHERE RUN_ID=?"
            data_tup = (device_browser, run_id)
            return self.update_query(sql_query, data_tup)

        except Exception as e:
            raise e


    def get_test_details(self, run_id):
        try:
            sql_query = """SELECT tbl_scripts.ScriptName,
tbl_testruns.RUN_ID, 
tbl_batch.TestType, 
tbl_command_variables.ALMTestLabPath, 
tbl_command_variables.ALMTestPlanPath, 
tbl_command_variables.ALMTestSetName, 
tbl_command_variables.ENV_LANGUAGE,
tbl_command_variables.ENV_URL,
tbl_command_variables.ENV_MC_SERVER,
tbl_command_variables.ENV_MC_USER_NAME,
tbl_command_variables.ENV_MC_USER_PASS 
FROM tbl_batch, tbl_command_variables, tbl_scripts, tbl_testruns 
WHERE 
tbl_batch.Batch_ID=tbl_testruns.Batch_ID 
AND 
tbl_testruns.Script_ID=tbl_scripts.Script_ID
AND 
tbl_batch.Batch_ID=tbl_command_variables.Batch_ID 
AND tbl_testruns.RUN_ID=?"""
            result = self.query(sql_query, (run_id,))
            return result[0] if result else {}
        except Exception as e:
            raise e

    def get_batch(self, batch_id):
        try:

            sql_query = """SELECT 
tbl_batch.Batch_Name, 
tbl_batch.ThreadCount, 
tbl_batch.Project_Location, 
tbl_batch.TestType, 
tbl_command_variables.ENV_LANGUAGE, 
tbl_command_variables.ENV_URL, 
tbl_command_variables.ALMTestLabPath,
tbl_command_variables.ALMTestPlanPath,
tbl_command_variables.ALMTestSetName,
tbl_command_variables.ENV_MC_SERVER,
tbl_command_variables.ENV_MC_USER_NAME,
tbl_command_variables.ENV_MC_USER_PASS 
FROM tbl_batch,tbl_command_variables 
WHERE 
tbl_batch.Batch_ID=tbl_command_variables.Batch_ID 
AND tbl_batch.Batch_ID=?"""
            result = self.query(sql_query, (batch_id,))
            return result[0] if result else {}
        except Exception as e:
            raise e


class CreateBookMarkModel:
    def __init__(self, project_bm_file=None, user_bm_file=None):
        self.logger = RobotLogger(__name__).logger
        self.project_bm_file = project_bm_file or os.path.join(self._get_project_location(), 'bookmarks.json')
        self.user_bm_file = user_bm_file or os.path.join(AppConfig.user_bookmarks_path,
                                                         os.path.basename(self._get_project_location()),
                                                         'bookmarks.json')
        self.project_bm_dd = Bookmarks(self.project_bm_file)
        self.user_bm_dd = Bookmarks(self.user_bm_file)


    def _get_project_location(self):
        parser = AppConfigParser(AppConfig.user_config_file)
        parser.readfile()
        if parser.has_option(AppConfig.INI_APP_SETTING_SECTION, AppConfig.INI_PROJECT_LOCATION):
            # return the Value
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
        return self.user_bm_dd.update_bookmarks(data_dict)


class StatisticsModel:

    def __init__(self, host=None, database=DatabaseConfig.sqllite_db_location, user=None, password=None):
        self.connection = sq.connect(database)
        self.connection.row_factory = sq.Row
        self.logger = RobotLogger(__name__).logger

    def query(self, query, parameters=None):
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, parameters)
        except sq.Error as e:
            self.connection.rollback()
            raise e
        else:
            self.connection.commit()

        if cursor.description is not None:
            return cursor.fetchall()

    def get_test_execution_data(self, from_date, to_date):
        """Get test execution data"""
        try:
            sql_query = """SELECT 
tbl_testruns.Batch_ID,
tbl_scripts.ScriptName, 
tbl_scripts.Source, 
tbl_testruns.Status, 
tbl_testruns.Start_Time, 
tbl_testruns.End_Time, 
tbl_testruns.Device_Browser, 
tbl_testruns.USER_NAME, 
tbl_testruns.Run_Count  
FROM tbl_testruns, tbl_scripts 
WHERE
tbl_testruns.Script_ID=tbl_scripts.Script_ID 
AND
tbl_testruns.Start_Time BETWEEN ? AND ?"""
            return self.query(sql_query, (from_date, to_date))
        except Exception as e:
            self.logger.error(e)
            raise e

    def get_test_creation_data(self, from_date, to_date):
        """Get test execution data"""
        try:
            sql_query = """SELECT * FROM tbl_scripts WHERE tbl_scripts.CreationDate BETWEEN ? AND ?"""
            return self.query(sql_query, (from_date, to_date))
        except Exception as e:
            self.logger.error(e)
            raise e


class SettingsModel:
    variables = {'use alm': {'type': 'bool', 'value': False},
                 'project_location': {'type': 'str', 'value': '~'},
                 'alm_url': {'type': 'str', 'value': 'Enter ALM URL'},
                 'browser_list': {'type': 'str', 'value': 'Chrome||IE||Firefox||Safari'},
                 'url_list': {'type': 'str', 'value': 'DummyURL1||DummyURL2'},
                 'device_list': {'type': 'str', 'value': 'DummyDevice1||DummyDevice2'},
                 'device_Server_list': {'type': 'str', 'value': 'DummyServer1||DummyServer2'}}

    def __init__(self, filename='user_setting.json'):
        # determine the file path
        self.filepath = os.path.join(AppConfig.user_folder_path, filename)
        self.logger = RobotLogger(__name__).logger
        self.load()

    def load(self):
        """if file does not exist then retrun"""
        if not os.path.exists(self.filepath):
            return

        """Load the settings from the file"""
        with open(self.filepath, 'r') as fh:
            raw_values = json.loads(fh.read())

        # Just getting the keys that we need from the raw values
        for key in self.variables:
            if key in raw_values and 'value' in raw_values[key]:
                self.variables[key]['value'] = raw_values[key]['value']

    def save(self,setting=None):
        json_string = json.dumps(self.variables)
        with open(self.filepath,'w') as fh:
            fh.write(json_string)

    def set(self, key, value):
        if key in self.variables and type(value).__name__ == self.variables[key]['type']:
            self.variables[key]['value'] = value
        else:
            raise ValueError("Bad key or wrong variable type")
