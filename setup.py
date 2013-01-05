import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'mock',
    'py-bcrypt',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_beaker',
    'pyramid_tm',
    'python-dateutil',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'webtest',
    'zope.sqlalchemy',
]

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
