Parks README
==================

Getting Started
---------------

Install virtualenv from pip if you don't have it. Don't use your operating
system packages; I've found them to be flaky.
    sudo pip install virtualenvwrapper

Make a virtual environment for parks. Also, I'm using Python 3, dammit. I'm
tired of Unicode errors.
    mkvirtualenv parks --python=/usr/bin/python3

You'll need to install the lib XML headers in order to install PyQuery. PyQuery
is like BeautifulSoup, but I like it more. It's very similar to jQuery.
    sudo apt-get install libxml2-dev libxslt-dev

And set everything up.
    git submodule init
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
