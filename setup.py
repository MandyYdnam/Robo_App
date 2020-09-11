#!/usr/bin/env python

from setuptools import setup, find_packages
import robo_app

with open("README.rst") as fh:
    long_description = fh.read()

setup(
    name="robotframework-executor",
    version=robo_app.__version__,
    author="Mandeep Dhiman",
    author_email="mandeepsinghdhiman@outlook.com",
    description="A GUI based Robot Test Executor",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/MandyYdnam/Robo_App",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['requests>=2.22', 'robotframework<=3.1.2', 'matplotlib>=3.2.1'],
    entry_points={'console_scripts':['roboapp = robo_app:main']
    }
)