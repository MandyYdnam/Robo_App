Description
============
* Application to run the Robot Test From the File System with following features.
* Group Robot Test Cases from different Folders and Group them in batch.
* Search Test using Robot Tags
* Run/Track the batch execution status in real time.
* Bookmarks your frequently used test sets to create batch easily.
* Run Robot Batch in multiple threads to seed up the execution.
* Designed to suite Mobile and Web test Automation in mind.
* This application is written in Python 3.7. Not tested for Python 3.8
* Can be integrated with Microfocus ALM Authentication.



Author
==========
Mandeep Dhiman

Installation Requirements
===========================
* Python 3
* Robot Framework
* Tkinter
* requests

Installation
------------

Using ``pip``
'''''''''''''
The recommended installation method is using
`pip <http://pip-installer.org>`__::
    pip install robot-executor

To run the tool Run following in Terminal/Command
    roboapp

Configuration
================
ALM Authentication Configuration
This Application comes with ALM Authentication. By Default this is feature is disabled.
To enable this feature, Download the source from the `Git Hub <https://github.com/MandyYdnam/Robo_App>`_
Update Following in constants.py
    * USE_ALM = True
    * ALM_URI = "enter your alm uri"

And Build the distribution from source.
Once done, Install the newly build package and Try to run.


Usage
============

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
Read `Setting variables in command line <https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#setting-variables-in-command-line>`_

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
==============

* `Mandeep Dhiman <https://github.com/MandyYdnam/>`_


Know Bugs
=============
* Fresh Install- Clicking Bookmarks is clearing the selected project


v 0.0.8
Features
-----------
* Added Mac Compatibility


v 0.0.7
Features
-----------
* Sorting For Batch Execution Monitor
* Add License

v 0.0.6
Features
-----------
* URL Parameter for Web
* Search by Tags

v 0.0.5
Features
-----------
* ALM Login Screen And Integration


v 0.0.4
Features
-----------
* Enhanced Book Mark Feature


v 0.0.3
Features
-----------
* Add Feature To Create Bookmaks for Test Case
* Back End changes from Tuple to Dict
* Load bookmarks to update after creating new BM.
* Enhancements to Database Model Function

v 0.0.2
Features
-----------
* Add Feature To Update Already Existing Batch
* Add Feature to Update Script.


v 0.0.1
Features
-----------
* Provides user ability to run the Robot Test cases from the project
* Stores the Past Results from the Execution
* Provides Batch Monitor to see the Live Batch Execution Process
