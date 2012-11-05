Parks README
==================

Getting Started
---------------

cd ..
virtualenv --no-site-packages pyramid
cd pyramid/Parks
../bin/python setup.py develop
../bin/initialize_Parks_db development.ini
../bin/pserve --reload development.ini
