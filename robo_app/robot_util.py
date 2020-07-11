from datetime import datetime
from robot import run
import os
from robot.libraries.BuiltIn import BuiltIn
from robot.api import TestData, ResourceFile, TestCaseFile
from . import models as m
from multiprocessing import Pool
import multiprocessing
from operator import itemgetter
from .constants import AppConfig


def run_task(task):
    # print('worker_started:', multiprocessing.current_process().name, multiprocessing.current_process().pid)
    print("In Run task")
    print('BatchID:', task.get('Batch_ID'))
    print('RUN_ID:', task.get('RUN_ID'))
    print('Test Name', task.get('ScriptName'))
    print('Test Source:', task.get('Source'))
    variable_list = []
    print('Test Type:', task.get('TestType'))

    # Change the Execution Dir
    if task.get('Project_Location'):
        os.chdir(task.get('Project_Location'))
        # print('New dir', os.getcwd())

    if task.get('TestType') == 'Mobile':
        variable_list.append('ENV_DEVICE_UDID:{}'.format(task.get('Device_Browser')))
        variable_list.append('ENV_MC_SERVER:{}'.format(task.get('ENV_MC_SERVER')))
        variable_list.append('ENV_MC_USER_NAME:{}'.format(task.get('ENV_MC_USER_NAME')))
        variable_list.append('ENV_MC_USER_PASS:{}'.format(task.get('ENV_MC_USER_PASS')))
    else:
        variable_list.append('ENV_Browser:{}'.format(task.get('Device_Browser')))
        variable_list.append('ENV_URL:{}'.format(task.get('ENV_URL')))

    variable_list.append('ENV_LANGUAGE:{}'.format(task.get('ENV_LANGUAGE')))
    variable_list.append('ALMTestPlanPath:{}'.format(task.get('ALMTestPlanPath')))
    variable_list.append('ALMTestLabPath:{}'.format(task.get('ALMTestLabPath')))
    variable_list.append('ALMTestSetName:{}'.format(task.get('ALMTestSetName')))
    variable_list.append('AlmUrl:{}'.format(task.get('AlmUrl')))
    variable_list.append('almuserid:{}'.format(task.get('almuserid', '')))
    variable_list.append('almuserpswd:{}'.format(task.get('almuserpswd', '')))
    variable_list.append('almdomain:{}'.format(task.get('almdomain', '')))
    variable_list.append('almproject:{}'.format(task.get('almproject', '')))
    print(variable_list)
    result_folder = task.get('Result_Location', AppConfig.result_location)
    result_folder = os.path.join(result_folder, str(task.get('Batch_ID')))

    result_folder = os.path.join(result_folder,datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
                                                    task.get('ScriptName'))
    # print('Result Folder:', result_folder)
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)
    with open(os.path.join(result_folder, "console_log.txt"), 'w') as stdout:
        run(task.get('Source'), test=task.get('ScriptName'), stdout=stdout,
            variable=variable_list,  # variable=('Var1:From CMD', 'Var2:var2FromCmd'),
            outputdir=result_folder,
            listener=TestRunnerAgent(task.get('Batch_ID'), task.get('RUN_ID')))


def get_robot_test_list(suite, test_list=None):
    suite = TestData(source=suite)
    return _get_robot_test_list(suite, test_list)


def get_robot_test_list2(suite, test_tags=None, test_list=None):
    """Return Test as Dict"""
    tags = list(test_tags) or []
    suite = TestData(source=suite)
    test_list= _get_robot_test_list(suite, test_list)
    if not tags or tags == ['']:
        return sorted([{'name':test.name, 'doc':test.doc.value, 'tags':str(test.tags), 'source':test.source} for test in test_list], key=itemgetter('name'))
    else:
        tags = {tag.lower() for tag in tags}
        return sorted([{'name': test.name, 'doc': test.doc.value, 'tags': str(test.tags), 'source': test.source} for test in
             test_list if set(tags).issubset(set([tag.lower() for tag in test.tags]))], key=itemgetter('name'))


def _get_robot_test_list(suite, test_list=None):
    """
    Function to return Test List
    Ex:
    suite = TestData(source=path_suite)
    testList = self._get_robot_test_list(suite)
    """
    test_list = test_list or []
    if os.path.isfile(suite.source):
        test_list.extend(suite.testcase_table.tests)
        return test_list
    for child in suite.children:
        test_list = _get_robot_test_list(child, test_list)
    return test_list


def get_project_tags(suite):
    """Return Test as Dict"""
    suite = TestData(source=suite)
    tag_list = _get_tags(suite)
    return sorted(list(set(tag_list)))  # removing duplicates


def get_project_stats(source):
    proj_data = []
    for subdir, dirs, files in os.walk(source):
        for filename in files:
            data_object =None
            filepath = subdir + os.sep + filename
            if filepath.endswith(".resource"):
                data_object = ResourceFile(filepath).populate()

            elif filepath.endswith(".robot"):
                data_object = TestCaseFile(source=filepath).populate()

            if data_object:
                proj_data.append({'Source': filepath,
                                  'File Name': data_object.name,
                                  'Keywords': len(data_object.keyword_table),
                                  'Test Cases': len(data_object.testcase_table)})

    return proj_data


def _get_tags(suite):
    tags = []

    if suite.setting_table.force_tags:
        tags.extend(suite.setting_table.force_tags.value)

    if suite.setting_table.default_tags:
        tags.extend(suite.setting_table.default_tags.value)

    for testcase in suite.testcase_table.tests:
        if testcase.tags:
            tags.extend(testcase.tags.value)

    for child_suite in suite.children:
        tags.extend(_get_tags(child_suite))
    return tags


class ScriptStatus():
    NOT_RUN = "Not Run"
    RUNNING = "Running"
    RERUN = "Re Run"
    PASSED = "Passed"
    FAIL = "Failed"
    STOPPED = 'Stopped'


class TestRunnerAgent:
    """Pass all listener events to a remote listener

    If called with one argument, that argument is a port, localhost is used as host, 30 seconds is a connection timeout
    If called with two, the first is a host, the second is a port, 30 seconds is a connection timeout
    If called with three, the first is a host, the second is a port, the third is a connection timeout
    """

    def __init__(self, *args):
        if len(args) == 1:
            self._batch_ID = int(args[0])
        if len(args) == 2:
            self._batch_ID = int(args[0])
            self._run_ID = int(args[1])
        else:
            self._batch_ID = None
        # print('batch_id', self._batch_ID)

        # intializing built in
        self.BuiltIn = BuiltIn()

    ROBOT_LISTENER_API_VERSION = 2
    MAX_VARIABLE_VALUE_TEXT_LENGTH = 2048

    def start_test(self, name, attrs):
        print('testStarted', attrs)
        print("Test Name", name)
        self._send_update(name, Status="'{}'".format(ScriptStatus.RUNNING),
                          Run_Count="Run_Count+1",
                          Start_Time="'{}'".format(self._normalize_date_time(attrs['starttime'])))

    def end_test(self, name, attrs):
        print('Test Ended', attrs)
        status = ScriptStatus.PASSED if attrs['status'] == 'PASS' else ScriptStatus.FAIL
        self._send_update(name, Status="'{}'".format(status),
                          End_Time="'{}'".format(self._normalize_date_time(attrs['endtime'])),
                          Log_path="'{}'".format(self.BuiltIn.get_variables()['${LOG_FILE}']))

    def _send_update(self, name, **kwargs):
        """Send the Scrpit Updated to the Database"""
        # sql_query = "Update tbl_scripts SET {} WHERE batch_id={} AND ScriptName='{}'".format(
        #     ",".join([str(key) + "=" + str(value) for (key, value) in kwargs.items()]), self._batch_ID, name)

        sql_query = "Update tbl_testruns SET {} WHERE tbl_testruns.Run_ID={}".format(
            ",".join([str(key) + "=" + str(value) for (key, value) in kwargs.items()]),
            self._run_ID)

        print('Sending Updates')
        print(sql_query)
        try:
            db_con = m.Robo_Executor_SQLLiteDB()
            db_con.open_connection()

            db_con.run_sql(sql_query, commit=True)

        finally:
            db_con.close_connection()

    def _normalize_date_time(self, date_time):
        return str(datetime.strptime(date_time, '%Y%m%d %H:%M:%S.%f'))[:-7]


class ExecutionPool:
    def __init__(self, task_list=None, processes=1, variable_list=None, *args, **kwargs):
        # Converting the Task row tuple as Dict
        # self.task_list = [task._asdict() for task in task_list]
        self.task_list = [dict(task) for task in task_list]
        self.variable_list = variable_list
        self.process_pool = Pool(processes=processes)
        self.result = []

    def run_command(self):
        self.result = self.process_pool.map_async(run_task, self.task_list)
        # while not (self.result.ready()):
        #     pass

    def remaining_task(self):
        if type(self.result) is multiprocessing.pool.MapResult:
            return self.result._number_left
        else:
            return 0

    def current_batch_id(self):
        return self.task_list[0].get('Batch_ID')

    def terminate_batch(self):
        self.process_pool.terminate()
