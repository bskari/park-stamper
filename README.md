Parks README
==================

Getting Started
---------------

Install virtualenv from pip if you don't have it. Don't use your operating
system packages; I've found them flaky.
    sudo pip install virtualenvwrapper

Make a virtual environment for parks.
    mkvirtualenv parks

I'm using MySQL for my production database (I know, sorry... it's what I knew
when I started this project) and the installation of Python's MySQL
bindings will complain if you do not have a MySQL client installed, because it
wants to read a configuration file. So, you have to install it, even if you're
not going to use locally. Yay MySQL.
    sudo apt-get install libmysqlclient-dev

And set everything up.
    python setup.py develop
    initialize_Parks_db development.ini

Then run the test server with
    pserve --reload development.ini

That's it! It should be running on http://localhost:6543 . When you're done working on the environment, type
    deactivate
to get out of the environment. To get back, run
    workon parks
and restart the test server.

Running Tests
-------------

    ../bin/nosetests --cover-package=parks --cover-erase --with-coverage
