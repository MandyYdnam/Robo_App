Description
--------------------------------
* Application to run the `Robot Framework`_ Test From the File System with following features.
* Group Robot Test Cases from different Folders and Group them in batch.
* Search Test using Robot Tags
* Run/Track the batch execution status in real time.
* Bookmarks your frequently used test sets to create batch easily.
* Run Robot Batch in multiple threads to seed up the execution.
* Designed to suite Mobile and Web test Automation in mind.
* This application is written in Python_ 3.7. Not tested for Python 3.8
* Can be integrated with Microfocus ALM Authentication.



Author
--------------------------------
`Mandeep Dhiman`_

Installation Requirements
--------------------------------
* Python_ 3
* `Robot Framework`_
* Tkinter
* requests_
* matplotlib_

Installation
------------

Using ``pip``
'''''''''''''
The recommended installation method is using
pip_

    pip install robot-executor

To run the tool Run following in Terminal/Command
    roboapp


ALM Authentication Configuration
--------------------------------
This Application comes with ALM Authentication. By Default this is feature is disabled.
To enable this feature, Select **'Options->Use ALM'** from the Options Menu.
Note: In order it to work, Make sure you are setting ALM URL from **'Options->Preferences'** Menu.

Usage
--------------------------------

* Browse to base Robot Framework Project Location Folder.
* Search the Test Cases by Browsing to different Folder.
* You can also Search Test by Tags.
* From the Search Results Add the Test cases to the Batch.
* Click on Create Batch.
* Fill in the Required Batch Details Create a Batch
* Once Batch is Created, Go to Batch Monitor.
* Right Click the batch and Click Start to Start the Test Execution.
* Application do not allow to overwrite existing bookmark.
* If you really want to updated exiting bookmark, then use admin password (Pr1y@)

Note:

Information Provided on Create batch form is exposed as Command line variables to robot Test. So values in these
fields can be used in the Robot Test as Variables.
Read `Setting variables in command line`_

Here is the Mapping of fields to variable names.

* Language => ENV_LANGUAGE
* Test Plan Path => ALMTestPlanPath
* Test Lab Path => ALMTestLabPath
* Test Set Name => ALMTestSetName


Mobile Specific Mapping:

* Select Device / Browser => ENV_DEVICE_UDID
* Select Server=> ENV_MC_SERVER
* User Name => ENV_MC_USER_NAME
* User Password => ENV_MC_USER_PASS


Browser Specific Mapping:

* Select Device / Browser => ENV_Browser
* Select URL => ENV_URL


If you are using Microfocus's ALM Login Form then following variable will be exposed:

* AlmUrl
* Name => almuserid
* Password => almuserpswd
* Domain => almdomain
* Project => almproject


Project Contributors
--------------------------------

* `Mandeep Dhiman`_


Know Bugs
--------------------------------

* Sorting in Scripts Table

History
--------------------------------

.. list-table::
    :header-rows: 1

    * - Version
      - Features/enhancements
    * - 0.1.0
      - Added Options Menu,
        Bug Fixes
    * - 0.0.9
      - Clone Batch Feature,
        Fixed Broken RST
    * - 0.0.8
      - Added Mac Compatibility,
        Sorting For Batch Execution Monitor






.. _Robot Framework: https://robotframework.org
.. _pip: http://pip-installer.org
.. _GitHub: https://github.com/MandyYdnam/Robo_App
.. _Python: https://python.org
.. _requests: https://pypi.org/project/requests/
.. _Setting variables in command line: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#setting-variables-in-command-line
.. _Mandeep Dhiman: https://github.com/MandyYdnam
.. _matplotlib: https://matplotlib.org/