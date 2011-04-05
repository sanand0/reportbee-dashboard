About
=====
This is the code used to create the [student performance dashboard](http://www.s-anand.net/blog/visualising-student-performance/)

Running on Windows
==================
1. Install [ActivePython 2.5.x](http://www.activestate.com/activepython/downloads). (Version 2.7 should work too)
2. Install [SetupTools](http://pypi.python.org/pypi/setuptools#files) for the version of Python you've installed. (e.g. `setuptools-0.6c11.win32-py2.7.exe` if you installed Python 2.7)
3. On the Command Prompt, go to the folder where you downloaded this repository, and type:

    easy_install tornado
    easy_install django

4. Download this repository. On the command prompt, where this repository is saved, run:

    python main.py filename.csv

... where `filename.csv` is the file that contains the student data.
