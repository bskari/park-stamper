import os
import sys
from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'PyMySql',
    'PyQuery',
    'SQLAlchemy',
    'py-bcrypt',
    'pyramid',
    'pyramid_beaker',
    'pyramid_mako',
    'pyramid_tm',
    'python-dateutil',
    'transaction',
    'waitress',
    'webtest',
    'zope.sqlalchemy',
]

# There's got to be a less hacky way to do this
if 'develop' in sys.argv:
    requires.extend((
        'ipdb',
        'mock',
        'pyquery',
        'pyramid_debugtoolbar',
    ))

setup(
    name='Parks',
    version='0.0',
    description='Parks',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
      "Programming Language :: Python",
      "Framework :: Pyramid",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='parks',
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = parks:main
    [console_scripts]
    initialize_Parks_db = parks.scripts.initializedb:main
    """,
)
