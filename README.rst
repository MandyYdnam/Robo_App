Description
--------------------------------
* Application to run the `Robot Framework`_ Test From the File System with following features.
* Group Robot Test Cases from different Folders and Group them in batch.
* Search Test using Robot Tags
* Run/Track the batch execution status in real time.
* Bookmarks your frequently used test sets to create batch easily.
* Run Robot Batch in parallel to seed up the execution.
* Designed to suite Mobile and Web test Automation in mind.
* This application is written in Python_ 3.7. Not tested for Python 3.8
* Can be integrated with Microfocus ALM Authentication.
* Download the Historical data in csv format.
* Dashboard for Historical Data (e.g. Test Executions)



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

    pip install robotframework-executor

To run the Application, Run following in Terminal/Command
    roboapp

How to Create a Batch
--------------------------------
|How To Create a Batch|

How to Run a Batch
--------------------------------
|How To Run a Batch|

How to Create a BookMark
--------------------------------
|How to Create a BookMark|

Statistics
--------------------------------
|Statistics|

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

Note
--------------------------------

If you are running this tool in virtual environment, then make sure you install all your project dependencies in the
same virtual environment.

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

Robot Framework Version Support
--------------------------------

.. list-table::
    :header-rows: 1

    * - robo-executor Version
      - robotframwork Version Supported
    * - v 0.1.2
      - v <= 3.1.2
    * - v 0.1.3
      - v 3.2.2 > 4.0
    * - v 0.1.5
      - v 4.1



History
--------------------------------

.. list-table::
    :header-rows: 1

    * - Version
      - Features/enhancements
    * - `0.1.5`_
      - | Support for Robot Framework 4.1. (If cannot use RF4.1, then use version 0.1.4 for this software.)
        | Bug fixes for Test execution and Test Creation Stats
    * - `0.1.4`_
      - Bug Fixes and Ubuntu Compatibility.
    * - 0.1.3
      - RF 3.2.2 Compatibility
    * - 0.1.1 - 0.1.2
      - Minor Documentation fixes.
        Requirements updated.
    * - `0.1.0`_
      - Added Options Menu,
        Bug Fixes
    * - `0.0.9`_
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
.. _0.1.0: https://github.com/MandyYdnam/Robo_App/blob/master/doc/Robo_app_1.0.rst
.. _0.0.9: https://github.com/MandyYdnam/Robo_App/blob/master/doc/Robo_app_0.09.rst
.. _0.1.4: https://github.com/MandyYdnam/Robo_App/milestone/2
.. _0.1.5: https://github.com/MandyYdnam/Robo_App/milestone/3

.. |How To Create a Batch| image:: https://media.giphy.com/media/XzovyaAGfI95husPa9/giphy.gif
  :width: 400
  :alt: How to Create a Batch

.. |How To Run a Batch| image:: https://media.giphy.com/media/dUr8Xnr96rWMBRNVae/giphy.gif
  :alt: How to Run a Batch

.. |How to Create a BookMark| image:: https://media.giphy.com/media/UWgieA2vCfThBZnEhi/giphy.gif
  :alt: How to Create a BookMark

.. |Statistics| image:: https://media.giphy.com/media/UQsa5kdflVx8DG685x/giphy.gif
  :alt: Statistics Demo
