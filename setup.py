from setuptools import setup, find_packages
import robo_app

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="robot-executor",
    version=robo_app.__version__,
    author="Mandeep Dhiman",
    author_email="mandeepsinghdhiman@outlook.com",
    description="A GUI based Robot Test Executor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['requests>=2.22','robotframework>=3.1'],
    entry_points={'console_scripts':['roboapp = robo_app:main']
    }
)